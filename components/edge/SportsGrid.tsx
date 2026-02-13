'use client';

import { useState, useRef, useEffect } from 'react';
import { GameCard } from './GameCard';

const BOOK_CONFIG: Record<string, { name: string; color: string }> = {
  'fanduel': { name: 'FanDuel', color: '#1493ff' },
  'draftkings': { name: 'DraftKings', color: '#53d337' },
  'betmgm': { name: 'BetMGM', color: '#c4a44d' },
  'caesars': { name: 'Caesars', color: '#00693e' },
  'pointsbetus': { name: 'PointsBet', color: '#e42222' },
  'bovada': { name: 'Bovada', color: '#cc0000' },
  'betonlineag': { name: 'BetOnline', color: '#ff6600' },
  'lowvig': { name: 'LowVig', color: '#6b7280' },
  'mybookieag': { name: 'MyBookie', color: '#1a1a2e' },
  'williamhill_us': { name: 'William Hill', color: '#003c14' },
  'betus': { name: 'BetUS', color: '#0066cc' },
  'betrivers': { name: 'BetRivers', color: '#1a3c6e' },
  'fanatics': { name: 'Fanatics', color: '#00904a' },
  'espnbet': { name: 'ESPN BET', color: '#d00' },
  'fliff': { name: 'Fliff', color: '#7c3aed' },
  'hardrockbet': { name: 'Hard Rock', color: '#000' },
  'bet365': { name: 'Bet365', color: '#027b5b' },
  'unibet_us': { name: 'Unibet', color: '#147b45' },
  'superbook': { name: 'SuperBook', color: '#b8860b' },
  'wynnbet': { name: 'WynnBET', color: '#94734a' },
  'tipico_us': { name: 'Tipico', color: '#1a1a1a' },
  'ballybet': { name: 'Bally Bet', color: '#e31837' },
};

interface SportsGridProps {
  games: Array<{
    game: any;
    bookmakerOdds: Record<string, { consensus: any; edge: any }>;
    edgeCount?: number;  // Number of edges detected for this game
  }>;
  availableBooks: string[];
}

export function SportsGrid({ games, availableBooks }: SportsGridProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const priorityOrder = ['fanduel', 'draftkings', 'betmgm', 'caesars', 'betrivers', 'pointsbetus', 'espnbet'];
  const sortedBooks = [...availableBooks].sort((a, b) => {
    const aIndex = priorityOrder.indexOf(a);
    const bIndex = priorityOrder.indexOf(b);
    if (aIndex === -1 && bIndex === -1) return 0;
    if (aIndex === -1) return 1;
    if (bIndex === -1) return -1;
    return aIndex - bIndex;
  });

  const [selectedBook, setSelectedBook] = useState(sortedBooks[0] || '');

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (sortedBooks.length === 0) {
    return <p className="text-zinc-400">No odds available</p>;
  }

  const selectedConfig = BOOK_CONFIG[selectedBook] || { name: selectedBook, color: '#6b7280' };

  const BookIcon = ({ bookKey, size = 24 }: { bookKey: string; size?: number }) => {
    const config = BOOK_CONFIG[bookKey] || { name: bookKey, color: '#6b7280' };
    const initials = config.name.split(' ').map(w => w[0]).join('').slice(0, 2);
    
    return (
      <div 
        className="rounded flex items-center justify-center font-bold text-white flex-shrink-0"
        style={{ 
          backgroundColor: config.color,
          width: size,
          height: size,
          fontSize: size * 0.4,
        }}
      >
        {initials}
      </div>
    );
  };

  return (
    <div>
      {/* Sportsbook Dropdown */}
      <div className="relative mb-6" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-3 px-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg hover:bg-zinc-700/70 transition-all min-w-[200px]"
        >
          <BookIcon bookKey={selectedBook} size={28} />
          <span className="font-medium text-zinc-100">{selectedConfig.name}</span>
          <svg 
            className={`w-4 h-4 text-zinc-400 ml-auto transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute z-50 mt-2 w-64 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl overflow-hidden">
            <div className="max-h-80 overflow-y-auto">
              {sortedBooks.map((book) => {
                const config = BOOK_CONFIG[book] || { name: book, color: '#6b7280' };
                const isSelected = book === selectedBook;
                return (
                  <button
                    key={book}
                    onClick={() => {
                      setSelectedBook(book);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all ${
                      isSelected 
                        ? 'bg-emerald-500/10 text-emerald-400' 
                        : 'hover:bg-zinc-700/50 text-zinc-300'
                    }`}
                  >
                    <BookIcon bookKey={book} size={28} />
                    <span className="font-medium">{config.name}</span>
                    {isSelected && (
                      <svg className="w-4 h-4 ml-auto text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Games Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {games.map(({ game, bookmakerOdds, edgeCount }) => {
          const odds = bookmakerOdds[selectedBook];
          const hasExchange = !!(bookmakerOdds['kalshi'] || bookmakerOdds['polymarket']);
          return (
            <GameCard
              key={game.id}
              game={game}
              consensus={odds?.consensus}
              edge={odds?.edge}
              edgeCount={edgeCount}
              hasExchange={hasExchange}
            />
          );
        })}
      </div>
    </div>
  );
}