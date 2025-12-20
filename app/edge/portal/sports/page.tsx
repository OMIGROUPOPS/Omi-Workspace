import { SUPPORTED_SPORTS } from '@/lib/edge/utils/constants';
import Link from 'next/link';

export default function SportsPage() {
  // Group sports by their group
  const grouped = SUPPORTED_SPORTS.reduce((acc, sport) => {
    if (!acc[sport.group]) {
      acc[sport.group] = [];
    }
    acc[sport.group].push(sport);
    return acc;
  }, {} as Record<string, typeof SUPPORTED_SPORTS[number][]>);

  // Order groups
  const groupOrder = [
    'American Football',
    'Basketball', 
    'Ice Hockey',
    'Baseball',
    'Combat Sports',
    'Soccer',
    'Golf',
    'Cricket',
    'Rugby',
    'Aussie Rules',
    'Handball',
    'Politics',
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">Sports</h1>
        <p className="text-zinc-400 mb-8">Select a league to view games and edges</p>

        <div className="space-y-8">
          {groupOrder.map((groupName) => {
            const sports = grouped[groupName];
            if (!sports) return null;

            return (
              <div key={groupName}>
                <h2 className="text-lg font-semibold text-zinc-300 mb-3">{groupName}</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  {sports.map((sport) => (
                    <Link
                      key={sport.key}
                      href={`/edge/portal/sports/${sport.key}`}
                      className="flex flex-col items-center gap-2 p-4 bg-zinc-900/50 border border-zinc-800 rounded-lg hover:border-zinc-700 hover:bg-zinc-900 transition-all"
                    >
                      <span className="text-2xl">{sport.icon}</span>
                      <span className="text-sm font-medium text-center">{sport.name}</span>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}