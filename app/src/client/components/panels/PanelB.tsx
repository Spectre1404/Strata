import { useState } from 'react';
import { Badge } from '@/client/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/client/components/ui/Card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/client/components/ui/Dialog';
import { useBarSeries } from '@/client/hooks/usePanels';
import type { BarPoint } from '@/server/panels/types';
import BarSeriesChart from './BarSeriesChart';
import TestIdeaForm from './TestIdeaForm';

function VerdictBadge({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-600">{label}</span>
      <Badge color={passed ? 'primary' : 'destructive'} variant="soft">
        {passed ? 'Clears the bar' : "Doesn't clear the bar"}
      </Badge>
    </div>
  );
}

export default function PanelB() {
  const { data: points } = useBarSeries();
  const [selected, setSelected] = useState<BarPoint | null>(null);

  return (
    <Card className="border-2 border-gray-900">
      <CardHeader>
        <CardTitle className="text-lg">The bar</CardTitle>
        <p className="text-sm text-gray-600">
          An agent that forgets its failures will report its luck as discovery. Every attempt counts against it.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <BarSeriesChart points={points ?? []} onSelect={setSelected} />
        <TestIdeaForm />
      </CardContent>

      <Dialog open={selected !== null} onOpenChange={(open) => !open && setSelected(null)}>
        <DialogContent>
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle>Attempt #{selected.attemptNumber}</DialogTitle>
                <DialogDescription>{selected.text}</DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Pipeline</p>
                  <pre className="text-xs font-mono bg-gray-50 border border-gray-200 rounded-md p-2 overflow-x-auto whitespace-pre-wrap">
                    {selected.pipeline}
                  </pre>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-gray-500">Sharpe (daily): {selected.sr.toFixed(3)}</p>
                  <VerdictBadge label="This session" passed={selected.passSession} />
                  <VerdictBadge label="Full record" passed={selected.passTotal} />
                </div>
                <p className="text-xs text-gray-400">
                  Daily returns aren't shown here yet — the app's database role can't read {'`trial_returns`'} (a
                  contract gap flagged for Shiv; needs a CONTRACTS.md change we both approve).
                </p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}
