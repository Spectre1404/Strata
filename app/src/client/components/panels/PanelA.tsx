import { Badge } from '@/client/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/client/components/ui/Card';
import { useCounters, useTrialStream } from '@/client/hooks/usePanels';
import FamilyBarChart from './FamilyBarChart';

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-2xl font-semibold text-gray-900">{value}</div>
    </div>
  );
}

function timeAgo(ts: string): string {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(ts).getTime()) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.floor(minutes / 60)}h ago`;
}

export default function PanelA() {
  const { data: counters } = useCounters();
  const { data: stream } = useTrialStream(12);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Live research</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-[1fr_auto] gap-4">
          <div className="space-y-2 max-h-72 overflow-y-auto pr-2">
            {(stream ?? []).map((item) => (
              <div key={item.trialId} className="border-b border-gray-100 pb-2 last:border-0">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm text-gray-900 leading-snug">{item.text}</p>
                  <span className="text-sm font-medium text-gray-900 shrink-0">{item.sr.toFixed(3)}</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="soft" color="neutral">{item.family.replace(/_/g, ' ')}</Badge>
                  <span className="text-[11px] font-mono text-gray-400">{item.preregHash.slice(0, 8)}</span>
                  <span className="text-[11px] text-gray-400">{timeAgo(item.ts)}</span>
                </div>
              </div>
            ))}
            {!stream?.length && <p className="text-sm text-gray-500">No attempts yet.</p>}
          </div>
          <div className="flex flex-col gap-4 w-36">
            <StatTile label="This session" value={counters?.sessionAttempts ?? 0} />
            <StatTile label="All sessions" value={counters?.totalAttempts ?? 0} />
            <StatTile label="Effective" value={counters?.effectiveAttempts ?? 0} />
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Attempts by family</p>
          <FamilyBarChart familyCounts={counters?.familyCounts ?? {}} />
        </div>
      </CardContent>
    </Card>
  );
}
