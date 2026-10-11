import { Card, CardContent, CardHeader, CardTitle } from '@/client/components/ui/Card';

interface PanelPlaceholderProps {
  title: string;
  note: string;
}

// Panels C and D land in T4 — kept quiet here so the page layout reads as
// complete without claiming anything isn't built yet.
export default function PanelPlaceholder({ title, note }: PanelPlaceholderProps) {
  return (
    <Card className="bg-gray-50 border-dashed">
      <CardHeader>
        <CardTitle className="text-base text-gray-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-400">{note}</p>
      </CardContent>
    </Card>
  );
}
