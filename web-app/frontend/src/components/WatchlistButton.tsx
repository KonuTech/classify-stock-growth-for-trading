import React from 'react';
import { HeartIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { useWatchlist } from '../contexts/WatchlistContext';

interface WatchlistButtonProps {
  stock: {
    symbol: string;
    name: string;
  };
  className?: string;
}

export default function WatchlistButton({ stock, className = '' }: WatchlistButtonProps) {
  const { addToWatchlist, removeFromWatchlist, isInWatchlist } = useWatchlist();
  const inWatchlist = isInWatchlist(stock.symbol);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering stock detail view
    
    if (inWatchlist) {
      removeFromWatchlist(stock.symbol);
    } else {
      addToWatchlist(stock);
    }
  };

  return (
    <button
      onClick={handleToggle}
      className={`p-2 rounded-full transition-colors ${
        inWatchlist 
          ? 'text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300' 
          : 'text-gray-400 hover:text-red-500 dark:hover:text-red-400'
      } ${className}`}
      title={inWatchlist ? 'Remove from watchlist' : 'Add to watchlist'}
    >
      {inWatchlist ? (
        <HeartSolidIcon className="h-6 w-6" />
      ) : (
        <HeartIcon className="h-6 w-6" />
      )}
    </button>
  );
}