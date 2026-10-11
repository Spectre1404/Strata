// Fixture-backed implementation of the panel data layer. Used while Shiv's
// scripts/seed_fixtures.py hasn't landed in Atlas yet. See mongo.ts for the
// real implementation and db.ts for the switch between the two.
import sessionsData from './fixtures/sessions.json';
import preregsData from './fixtures/preregistrations.json';
import trialsData from './fixtures/trials.json';
import auditsData from './fixtures/audits.json';
import trialGroupsData from './fixtures/trial_groups.json';
import type { Audit, BarPoint, Counters, Prereg, SessionEvent, Trial, TrialGroup, TrialStreamItem } from './types';

const sessions = sessionsData as SessionEvent[];
const preregs = preregsData as Prereg[];
const trials = trialsData as Trial[];
const audits = auditsData as Audit[];
const trialGroups = trialGroupsData as TrialGroup[];

function currentSessionId(): string | null {
  const started = new Set(sessions.filter((s) => s.event === 'start').map((s) => s.session_id));
  const ended = new Set(sessions.filter((s) => s.event === 'end').map((s) => s.session_id));
  const open = [...started].filter((id) => !ended.has(id));
  if (open.length === 0) return null;
  // Most recently started open session.
  const latest = sessions
    .filter((s) => s.event === 'start' && open.includes(s.session_id))
    .sort((a, b) => b.ts.localeCompare(a.ts))[0];
  return latest?.session_id ?? null;
}

export async function getCounters(): Promise<Counters> {
  const sessionId = currentSessionId();
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
