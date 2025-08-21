import { useState, useCallback, useEffect } from 'react';

interface WatchlistItem {
  symbol: string;
  name: string;
  addedAt: string;
  targetPrice?: number;
  notes?: string;
}

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(() => {
    try {
      const saved = localStorage.getItem('stock-watchlist');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Save to localStorage whenever watchlist changes
  useEffect(() => {
    localStorage.setItem('stock-watchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  const addToWatchlist = useCallback((stock: { symbol: string; name: string }, targetPrice?: number, notes?: string) => {
    setWatchlist(prev => {
      const exists = prev.find(item => item.symbol === stock.symbol);
      if (exists) return prev;
      
      const newItem: WatchlistItem = {
        symbol: stock.symbol,
        name: stock.name,
        addedAt: new Date().toISOString(),
        targetPrice,
        notes
      };
      
      return [...prev, newItem];
    });
  }, []);

  const removeFromWatchlist = useCallback((symbol: string) => {
    setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
  }, []);

  const updateWatchlistItem = useCallback((symbol: string, updates: Partial<WatchlistItem>) => {
    setWatchlist(prev => prev.map(item => 
      item.symbol === symbol ? { ...item, ...updates } : item
    ));
  }, []);

  const isInWatchlist = useCallback((symbol: string) => {
    return watchlist.some(item => item.symbol === symbol);
  }, [watchlist]);

  const clearWatchlist = useCallback(() => {
    setWatchlist([]);
  }, []);

  return {
    watchlist,
    addToWatchlist,
    removeFromWatchlist,
    updateWatchlistItem,
    isInWatchlist,
    clearWatchlist,
    watchlistCount: watchlist.length
  };
}