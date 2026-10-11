// Real implementation of the panel data layer, reading Strata's actual Atlas
// collections directly through the `app` role.
//
// Connects with its own native MongoClient on MONGODB_URI_APP / MONGODB_DB
// (read explicitly, not Modelence's own MONGODB_URI) rather than Modelence's
// `Store` class: Store binds to Modelence's own managed database connection,
// which is a separate thing from our Atlas sandbox. Modelence's own
// MONGODB_URI lives in .modelence.env (gitignored, written by `npx
// modelence setup`), not modelence.config.ts — that file only sets
// serverDir/serverEntry. Reading the app role's own URI directly here keeps
// panel reads on that role, matching docs/CONTRACTS.md's role table,
// independent of whatever Modelence Cloud uses internally. See also
// app/README.md: never set MONGODB_URI itself to an Atlas URI.
//
// Unverified against live Atlas as of this commit — no .env values yet. Swap
// DATA_SOURCE=mongo once Shiv's scripts/seed_fixtures.py has run and my .env
// is filled in (see db.ts).
import { MongoClient } from 'mongodb';
import type { Audit, BarPoint, Counters, Prereg, SessionEvent, Trial, TrialGroup, TrialStreamItem } from './types';

let client: MongoClient | null = null;

function getDb() {
  if (!client) {
    const uri = process.env.MONGODB_URI_APP;
    if (!uri) {
      throw new Error('MONGODB_URI_APP is not set — required when DATA_SOURCE=mongo');
    }
    client = new MongoClient(uri);
  }
  const dbName = process.env.MONGODB_DB;
  if (!dbName) {
    throw new Error('MONGODB_DB is not set — required when DATA_SOURCE=mongo');
  }
  return client.db(dbName);
}

// Fixtures.ts (and the shared BarPoint/Trial/etc. shapes in types.ts) work
// with ISO date strings, matching the static JSON fixtures. Real Mongo docs
// come back with `Date` objects for `ts`. Normalize here so the rest of the
// code never has to care which backend it's talking to.
function withIsoTs<T extends { ts: Date }>(doc: T): Omit<T, 'ts'> & { ts: string } {
  return { ...doc, ts: doc.ts.toISOString() };
}

async function currentSessionId(): Promise<string | null> {
  const docs = await getDb().collection<SessionEvent & { ts: Date }>('sessions').find({}).toArray();
  const events = docs.map(withIsoTs);
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
  const [sessionId, trials, trialGroups] = await Promise.all([
    currentSessionId(),
    getDb().collection<Trial>('trials').find({}).toArray(),
    getDb().collection<TrialGroup>('trial_groups').find({}).toArray()
  ]);
  const familyCounts: Record<string, number> = {};
  for (const t of trials) {
    familyCounts[t.family] = (familyCounts[t.family] ?? 0) + 1;
  }
  // T5 (grouping) isn't built, per Shiv's call to skip it unless everything
  // else is done — trial_groups will be empty against live data, so fall
  // back to the total rather than show a misleading "0 effective" count.
  const effectiveAttempts = trialGroups.length > 0 ? new Set(trialGroups.map((g) => g.numeric_group)).size : trials.length;
  return {
    sessionAttempts: sessionId ? trials.filter((t) => t.session_id === sessionId).length : 0,
    totalAttempts: trials.length,
    effectiveAttempts,
    currentSessionId: sessionId,
    familyCounts
  };
}

export async function getTrialStream(limit: number): Promise<TrialStreamItem[]> {
  const [trialDocs, preregDocs] = await Promise.all([
    getDb().collection<Trial & { ts: Date }>('trials').find({}).toArray(),
    getDb().collection<Prereg & { ts: Date }>('preregistrations').find({}).toArray()
  ]);
  const trials = trialDocs.map(withIsoTs);
  const preregs = preregDocs.map(withIsoTs);
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
  const [trialDocs, auditDocs] = await Promise.all([
    getDb().collection<Trial & { ts: Date }>('trials').find({}).toArray(),
    getDb().collection<Audit & { ts: Date }>('audits').find({}).toArray()
  ]);
  const trials = trialDocs.map(withIsoTs);
  const audits = auditDocs.map(withIsoTs);
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
      // The formal verdicts, not a simple sr-vs-bar read: a sr-vs-bar
      // comparison also highlights every session's first attempt (that
      // session's bar is 0 at n=1), which contradicts the detail dialog's
      // own pass_session/pass_total. pass_session/pass_total are DSR-based
      // (factor in skew/kurtosis) and are the actual verdict.
      luckPassedAsDiscovery: audit.pass_session && !audit.pass_total
    });
  });
  return points;
}
