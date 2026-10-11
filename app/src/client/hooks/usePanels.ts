import { useQuery } from '@tanstack/react-query';
import { modelenceQuery } from 'modelence/client';
import type { BarPoint, Counters, TrialStreamItem } from '@/server/panels/types';

// Polling every 2s, per docs/DEMO.md's Panel A spec ("implement polling first;
// add the change stream later only if time allows"). A later upgrade would
// swap this hook's useQuery for Modelence's modelenceLiveQuery, which wraps a
// MongoDB change stream server-side — no other code here would change.
const POLL_MS = 2000;

export function useCounters() {
  return useQuery({
    ...modelenceQuery<Counters>('panels.getCounters'),
    refetchInterval: POLL_MS
  });
}

export function useTrialStream(limit = 20) {
  return useQuery({
    ...modelenceQuery<TrialStreamItem[]>('panels.getTrialStream', { limit }),
    refetchInterval: POLL_MS
  });
}

export function useBarSeries() {
  return useQuery({
    ...modelenceQuery<BarPoint[]>('panels.getBarSeries'),
    refetchInterval: POLL_MS
  });
}
