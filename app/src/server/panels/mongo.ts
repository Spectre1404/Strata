// Real implementation of the panel data layer, reading Strata's actual Atlas
// collections through the `app` role (connected via MONGODB_URI, set to
// MONGODB_URI_APP's value — see docs/CONTRACTS.md rule 13: the app connects
// with that role only).
//
// `indexes: []` on every Store below: the Store constructor requires the
// field (crashes on undefined), but we deliberately declare none. The
// collections already exist in Atlas, created by Shiv's setup scripts, and
// the `app` role has no createIndex privilege (atlas/roles.md) — a non-empty
// list here would make Modelence try to provision indexes on startup and
// fail under that role.
//
// Unverified against live Atlas as of this commit — no .env values yet. Swap
// DATA_SOURCE=mongo once Shiv's scripts/seed_fixtures.py has run and my .env
// is filled in (see db.ts).
import { schema, Store } from 'modelence/server';
import type { Audit, BarPoint, Counters, Prereg, SessionEvent, Trial, TrialGroup, TrialStreamItem } from './types';

const dbSessions = new Store('sessions', {
  schema: {
    session_id: schema.string(),
    event: schema.string(),
    ts: schema.date(),
    policy_version: schema.number(),
    attempts: schema.number().optional(),
    final_hash: schema.string().optional()
  },
  indexes: []
});

const dbPreregistrations = new Store('preregistrations', {
  schema: {
    _id: schema.string(),
    session_id: schema.string(),
    ts: schema.date(),
    text: schema.string(),
    family: schema.string(),
    hash: schema.string()
  },
  indexes: []
});

const dbTrials = new Store('trials', {
  schema: {
    _id: schema.string(),
    session_id: schema.string(),
    seq: schema.number(),
    ts: schema.date(),
    source: schema.string(),
    prereg_id: schema.string(),
    text: schema.string(),
    family: schema.string(),
    pipeline: schema.string(),
    construction: schema.object({
      type: schema.string(),
      top_k: schema.number().nullable(),
      rebalance_bars: schema.number()
    }),
    causality: schema.string(),
    metrics: schema.object({
      sr: schema.number(),
      skew: schema.number(),
      kurt: schema.number(),
      t_obs: schema.number(),
      ann_return: schema.number(),
      turnover: schema.number()
    }),
    prev_hash: schema.string(),
    hash: schema.string()
  },
  indexes: []
});

const dbAudits = new Store('audits', {
  schema: {
    trial_id: schema.string(),
    ts: schema.date(),
    n_session: schema.number(),
    n_total: schema.number(),
    n_effective: schema.number(),
    sr: schema.number(),
    bar_session: schema.number(),
    bar_total: schema.number(),
    bar_effective: schema.number(),
    dsr_session: schema.number(),
    dsr_total: schema.number(),
    pass_session: schema.boolean(),
    pass_total: schema.boolean()
  },
  indexes: []
});

const dbTrialGroups = new Store('trial_groups', {
  schema: {
    trial_id: schema.string(),
    embedding: schema.embedding(),
    semantic_group: schema.number(),
    numeric_group: schema.number(),
    computed_at: schema.date()
  },
  indexes: []
});

// Fixtures.ts (and the shared BarPoint/Trial/etc. shapes in types.ts) work
// with ISO date strings, matching the static JSON fixtures. Real Mongo docs
// come back with `Date` objects for `schema.date()` fields — normalize here
// so the rest of the code never has to care which backend it's talking to.
function withIsoTs<T extends { ts: Date }>(doc: T): Omit<T, 'ts'> & { ts: string } {
  return { ...doc, ts: doc.ts.toISOString() };
}

async function currentSessionId(): Promise<string | null> {
  // Cast straight after fetch: Store's inferred document type attaches its
  // own method types (including one named `event`), which shadows
  // CONTRACTS.md's `sessions.event` field and breaks the string comparisons
  // below under strict mode.
  const events = (await dbSessions.fetch({})).map(withIsoTs) as unknown as SessionEvent[];
  const started = new Set(events.filter((s) => s.event === 'start').map((s) => s.session_id));
  const ended = new Set(events.filter((s) => s.event === 'end').map((s) => s.session_id));
  const open = [...started].filter((id) => !ended.has(id));
  if (open.length === 0) return null;
  const latest = events
    .filter((s) => s.event === 'start' && open.includes(s.session_id))
    .sort((a, b) => b.ts.localeCompare(a.ts))[0];
  return latest?.session_id ?? null;
}

export async function getCounters(): Promise<Counters> {
  const [sessionId, trialDocs, trialGroupDocs] = await Promise.all([
    currentSessionId(),
    dbTrials.fetch({}),
    dbTrialGroups.fetch({})
  ]);
  const trials = trialDocs as unknown as Trial[];
  const trialGroups = trialGroupDocs as unknown as TrialGroup[];
  const familyCounts: Record<string, number> = {};
  for (const t of trials) {
    familyCounts[t.family] = (familyCounts[t.family] ?? 0) + 1;
  }
  const effectiveAttempts = new Set(trialGroups.map((g) => g.numeric_group)).size;
  return {
    sessionAttempts: sessionId ? trials.filter((t) => t.session_id === sessionId).length : 0,
    totalAttempts: trials.length,
    effectiveAttempts,
    currentSessionId: sessionId,
    familyCounts
  };
}

export async function getTrialStream(limit: number): Promise<TrialStreamItem[]> {
  const [trialDocs, preregDocs] = await Promise.all([dbTrials.fetch({}), dbPreregistrations.fetch({})]);
  const trials = trialDocs.map(withIsoTs) as unknown as Trial[];
  const preregs = preregDocs.map(withIsoTs) as unknown as Prereg[];
  const preregById = new Map(preregs.map((p) => [p._id, p]));
  return [...trials]
    .sort((a, b) => b.ts.localeCompare(a.ts))
    .slice(0, limit)
    .map((t) => ({
      trialId: t._id,
      sessionId: t.session_id,
      ts: t.ts,
      text: t.text,
      family: t.family,
      preregHash: preregById.get(t.prereg_id)?.hash ?? '',
      pipeline: t.pipeline,
      sr: t.metrics.sr
    }));
}

export async function getBarSeries(): Promise<BarPoint[]> {
  const [trialDocs, auditDocs] = await Promise.all([dbTrials.fetch({}), dbAudits.fetch({})]);
  const trials = trialDocs.map(withIsoTs) as unknown as Trial[];
  const audits = auditDocs.map(withIsoTs) as unknown as Audit[];
  const auditByTrialId = new Map(audits.map((a) => [a.trial_id, a]));
  const ordered = [...trials].sort((a, b) => a.ts.localeCompare(b.ts));

  let best = -Infinity;
  const points: BarPoint[] = [];
  ordered.forEach((t, i) => {
    const audit = auditByTrialId.get(t._id);
    if (!audit) return;
    best = Math.max(best, t.metrics.sr);
    points.push({
      attemptNumber: i + 1,
      trialId: t._id,
      sessionId: t.session_id,
      ts: t.ts,
      text: t.text,
      pipeline: t.pipeline,
      sr: t.metrics.sr,
      bestSoFar: best,
      barSession: audit.bar_session,
      barTotal: audit.bar_total,
      passSession: audit.pass_session,
      passTotal: audit.pass_total,
      luckPassedAsDiscovery: audit.pass_session && !audit.pass_total
    });
  });
  return points;
}
