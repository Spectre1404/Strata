export type Family =
  | 'momentum'
  | 'reversal'
  | 'liquidity_volume'
  | 'volatility_range'
  | 'relative_strength'
  | 'intraday_structure'
  | 'futures_premium'
  | 'other';

export interface SessionEvent {
  session_id: string;
  event: 'start' | 'end';
  ts: string;
  policy_version: number;
  attempts?: number;
  final_hash?: string;
}

export interface Prereg {
  _id: string;
  session_id: string;
  ts: string;
  text: string;
  family: Family;
  hash: string;
}

export interface Trial {
  _id: string;
  session_id: string;
  seq: number;
  ts: string;
  source: 'researcher' | 'judge' | 'control';
  prereg_id: string;
  text: string;
  family: Family;
  pipeline: string;
  construction: { type: 'cs_rank' | 'ts_sign'; top_k: number | null; rebalance_bars: number };
  causality: 'pass' | 'fail';
  metrics: { sr: number; skew: number; kurt: number; t_obs: number; ann_return: number; turnover: number };
}

export interface Audit {
  trial_id: string;
  ts: string;
  n_session: number;
  n_total: number;
  n_effective: number;
  sr: number;
  bar_session: number;
  bar_total: number;
  bar_effective: number;
  dsr_session: number;
  dsr_total: number;
  pass_session: boolean;
  pass_total: boolean;
}

export interface TrialGroup {
  trial_id: string;
  semantic_group: number;
  numeric_group: number;
  computed_at: string;
}

// -- Panel-facing shapes (what the client actually renders) --

export interface Counters {
  sessionAttempts: number;
  totalAttempts: number;
  effectiveAttempts: number;
  currentSessionId: string | null;
  familyCounts: Record<string, number>;
}

export interface TrialStreamItem {
  trialId: string;
  sessionId: string;
  ts: string;
  text: string;
  family: Family;
  preregHash: string;
  pipeline: string;
  sr: number;
}

export interface BarPoint {
  attemptNumber: number; // position across all sessions, 1-indexed
  trialId: string;
  sessionId: string;
  ts: string;
  text: string;
  pipeline: string;
  sr: number;
  bestSoFar: number;
  barSession: number;
  barTotal: number;
  passSession: boolean;
  passTotal: boolean;
  luckPassedAsDiscovery: boolean; // passSession && !passTotal
}
