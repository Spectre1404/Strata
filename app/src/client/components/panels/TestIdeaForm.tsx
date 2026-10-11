import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Button } from '@/client/components/ui/Button';
import { Input } from '@/client/components/ui/Input';

const PRESETS = [
  'Buy the pairs that fell the most in the last hour',
  'Use tomorrow\'s close to pick today\'s winners',
  'Long the top decile by 24h relative strength vs BTC'
];

// UI only — T4 wires this to a `requests` insert, picked up by Shiv's judge
// hook worker (S7). Scaffolded here per docs/DEMO.md's Panel B spec.
export default function TestIdeaForm() {
  const [idea, setIdea] = useState('');

  function submit(text: string) {
    if (!text.trim()) return;
    toast('Wiring this up to the Researcher is T4 — coming soon.');
    setIdea('');
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500">Test my idea</p>
      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          submit(idea);
        }}
      >
        <Input
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="e.g. Buy pairs whose funding rate just turned negative"
        />
        <Button type="submit">Test my idea</Button>
      </form>
      <div className="flex flex-wrap gap-2">
        {PRESETS.map((preset) => (
          <Button key={preset} type="button" variant="outline" size="sm" onClick={() => submit(preset)}>
            {preset}
          </Button>
        ))}
      </div>
    </div>
  );
}
