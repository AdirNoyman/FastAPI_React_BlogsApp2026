import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';

export function Sidebar() {
  const items = [
    'Latest Posts',
    'Announcements',
    'Calendars',
    'etc'
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Our Sidebar</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="divide-y divide-border">
          {items.map((item, index) => (
            <li key={index} className="py-3 first:pt-0 last:pb-0">
              {item}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
