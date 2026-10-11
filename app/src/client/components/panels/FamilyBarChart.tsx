import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface FamilyBarChartProps {
  familyCounts: Record<string, number>;
}

export default function FamilyBarChart({ familyCounts }: FamilyBarChartProps) {
  const data = Object.entries(familyCounts)
    .map(([family, count]) => ({ family: family.replace(/_/g, ' '), count }))
    .sort((a, b) => b.count - a.count);

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 4 }}>
        <CartesianGrid stroke="var(--viz-grid)" horizontal={false} />
        <XAxis type="number" allowDecimals={false} tick={{ fill: 'var(--viz-muted)', fontSize: 11 }} stroke="var(--viz-baseline)" />
        <YAxis
          type="category"
          dataKey="family"
          width={110}
          tick={{ fill: 'var(--viz-text-secondary)', fontSize: 11 }}
          stroke="var(--viz-baseline)"
        />
        <Tooltip contentStyle={{ background: 'var(--viz-surface)', border: '1px solid var(--viz-grid)', fontSize: 12 }} />
        <Bar dataKey="count" name="Attempts" fill="var(--viz-series-1)" radius={[0, 4, 4, 0]} maxBarSize={18} isAnimationActive={false} />
      </BarChart>
    </ResponsiveContainer>
  );
}
