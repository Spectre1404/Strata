import { AlertTriangle } from 'lucide-react';
import { CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from 'recharts';
import type { BarPoint } from '@/server/panels/types';

interface BarSeriesChartProps {
  points: BarPoint[];
  onSelect: (point: BarPoint) => void;
}

interface DotProps {
  cx?: number;
  cy?: number;
  payload?: BarPoint;
  onSelect?: (point: BarPoint) => void;
}

// Click handled directly on each dot rather than via the chart's onClick:
// recharts 3.x's chart-level click event only gives a label/index to match
// against, and that match proved unreliable at the chart's edges (the last
// point in particular). A per-mark handler sidesteps matching entirely.
function AttemptDot({ cx, cy, payload, onSelect }: DotProps) {
  if (cx === undefined || cy === undefined || !payload) return null;
  const highlighted = payload.luckPassedAsDiscovery;
  return (
    <circle
      cx={cx}
      cy={cy}
      r={highlighted ? 6 : 4}
      fill={highlighted ? 'var(--viz-warning)' : 'var(--viz-text-primary)'}
      stroke="var(--viz-surface)"
      strokeWidth={2}
      style={{ cursor: 'pointer' }}
      onClick={() => onSelect?.(payload)}
    />
  );
}

export default function BarSeriesChart({ points, onSelect }: BarSeriesChartProps) {
  const highlightCount = points.filter((p) => p.luckPassedAsDiscovery).length;

  return (
    <div>
      <ResponsiveContainer width="100%" height={440}>
        <ComposedChart data={points} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--viz-grid)" vertical={false} />
          <XAxis
            dataKey="attemptNumber"
            type="number"
            domain={['dataMin', 'dataMax']}
            tick={{ fill: 'var(--viz-muted)', fontSize: 12 }}
            stroke="var(--viz-baseline)"
            label={{ value: 'Attempt number (across all sessions)', position: 'insideBottom', offset: -4, fill: 'var(--viz-muted)', fontSize: 12 }}
          />
          <YAxis
            tick={{ fill: 'var(--viz-muted)', fontSize: 12 }}
            stroke="var(--viz-baseline)"
            label={{ value: 'Sharpe (daily)', angle: -90, position: 'insideLeft', fill: 'var(--viz-muted)', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{ background: 'var(--viz-surface)', border: '1px solid var(--viz-grid)', fontSize: 12 }}
            labelFormatter={(label) => `Attempt #${label}`}
            formatter={(value, name) => [typeof value === 'number' ? value.toFixed(3) : value, name]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line type="monotone" dataKey="barTotal" name="Full-memory bar" stroke="var(--viz-series-1)" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="stepAfter" dataKey="barSession" name="This session's bar" stroke="var(--viz-series-2)" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="bestSoFar" name="Best so far" stroke="var(--viz-text-secondary)" strokeWidth={2} strokeDasharray="4 3" dot={false} isAnimationActive={false} />
          <Scatter dataKey="sr" name="Attempt" shape={<AttemptDot onSelect={onSelect} />} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
      {highlightCount > 0 && (
        <p className="flex items-center gap-1.5 text-xs text-[color:var(--viz-text-secondary)] mt-1">
          <AlertTriangle className="size-3.5" style={{ color: 'var(--viz-warning)' }} aria-hidden="true" />
          {highlightCount} attempt{highlightCount === 1 ? '' : 's'}: passes this session's test, fails the full-memory test. Click a dot for details.
        </p>
      )}
    </div>
  );
}
