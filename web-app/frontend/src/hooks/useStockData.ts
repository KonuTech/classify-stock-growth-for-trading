import { useState, useEffect, useCallback, useRef } from 'react';

interface StockData {
  symbol: string;
  name: string;
  currency: string;
  total_records: number;
  latest_date: string;
  latest_price: number;
  price_history: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

interface UseStockDataReturn {
  data: StockData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  lastUpdated: Date | null;
}

// Simple cache to avoid refetching the same data
const cache = new Map<string, { data: StockData; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useStockData(symbol: string, timeframe: '1M' | '3M' | '6M' | '1Y' = '3M'): UseStockDataReturn {
  const [data, setData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchStockData = useCallback(async () => {
    if (!symbol) return;

    const cacheKey = `${symbol}-${timeframe}`;
    const cached = cache.get(cacheKey);
    
    // Return cached data if it's still fresh
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setData(cached.data);
      setLastUpdated(new Date(cached.timestamp));
      setLoading(false);
      setError(null);
      return;
    }

    // Cancel previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:3001/api/stocks/${symbol}?timeframe=${timeframe}`,
        { signal: abortControllerRef.current.signal }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch ${symbol}: ${response.statusText}`);
      }

      const stockData = await response.json();
      
      // Cache the result
      const timestamp = Date.now();
      cache.set(cacheKey, { data: stockData, timestamp });
      
      setData(stockData);
      setLastUpdated(new Date(timestamp));
      setError(null);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return; // Request was cancelled, don't update state
      }
      
      setError(err instanceof Error ? err.message : 'Failed to fetch stock data');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe]);

  const refetch = useCallback(() => {
    const cacheKey = `${symbol}-${timeframe}`;
    cache.delete(cacheKey); // Clear cache for this stock
    fetchStockData();
  }, [fetchStockData, symbol, timeframe]);

  useEffect(() => {
    if (symbol) {
      fetchStockData();
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchStockData]);

  return {
    data,
    loading,
    error,
    refetch,
    lastUpdated
  };
}