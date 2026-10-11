import Page from '@/client/components/Page';
import PanelA from '@/client/components/panels/PanelA';
import PanelB from '@/client/components/panels/PanelB';
import PanelPlaceholder from '@/client/components/panels/PanelPlaceholder';

export default function HomePage() {
  return (
    <Page className="bg-gray-100">
      <div className="max-w-6xl mx-auto w-full space-y-6">
        <header className="pt-2">
          <h1 className="text-xl font-semibold text-gray-900">Strata</h1>
          <p className="text-sm text-gray-600 max-w-2xl">
            An AI agent that forgets its failures will report its luck as discovery. Strata makes forgetting
            impossible — this is the window onto the Researcher and the Auditor, not a dashboard.
          </p>
        </header>
        {/* Panel B is the one memorable element (docs/DEMO.md) — full width,
            first, and visually dominant. Everything else stays quiet below it. */}
        <PanelB />
        <PanelA />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PanelPlaceholder title="The verdict" note="Coming soon: opening the Vault and comparing against control strategies." />
          <PanelPlaceholder title="Blocked and learned" note="Coming soon: blocked attempts and the Strategist's rules." />
        </div>
      </div>
    </Page>
  );
}
