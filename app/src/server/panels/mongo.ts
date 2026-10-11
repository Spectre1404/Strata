// Real implementation of the panel data layer, reading Strata's actual Atlas
// collections directly through the `app` role.
//
// Connects with its own native MongoClient on MONGODB_URI_APP / MONGODB_DB
// (read explicitly, not Modelence's own MONGODB_URI) rather than Modelence's
// `Store` class: Store binds to Modelence's own managed database connection,
// which is a separate thing from our Atlas sandbox (see modelence.config.ts /
// the Modelence Cloud environment this app is linked to). Reading the app
// role's own URI directly keeps panel reads on that role, matching
// docs/CONTRACTS.md's role table, independent of whatever Modelence Cloud
// uses internally.
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
      // The highlighted dot is the one sitting between the two lines on the
      // chart itself (sr clears the session bar but not the full-memory
      // bar) — computed straight from sr vs. the two bar values, not from
      // pass_session/pass_total (those are DSR-based and can legitimately
      // disagree with a simple sr-vs-bar read; the highlight should match
      // what the chart's own lines show).
      luckPassedAsDiscovery: t.metrics.sr > audit.bar_session && t.metrics.sr <= audit.bar_total
    });
  });
  return points;
}
