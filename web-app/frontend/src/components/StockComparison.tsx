import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { XMarkIcon, PlusIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useStockData } from '../hooks/useStockData';
import Card from './ui/Card';
import Button from './ui/Button';
import { useDrag } from '../hooks/useDrag';

interface StockComparisonProps {
  initialStocks?: string[];
  onClose: () => void;
}

interface Stock {
  symbol: string;
  name: string;
  latest_price: number;
}

const CHART_COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];

export default function StockComparison({ initialStocks = [], onClose }: StockComparisonProps) {
  const [selectedStocks, setSelectedStocks] = useState<string[]>(initialStocks);
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y' | 'MAX'>('1Y');
  const [availableStocks, setAvailableStocks] = useState<Stock[]>([]);
  const [loadingStocks, setLoadingStocks] = useState(true);

  // Drag functionality
  const { dragRef, handleRef, dragProps, handleProps } = useDrag();

  // Fetch available stocks from real API
  useEffect(() => {
    const fetchAvailableStocks = async () => {
      try {
        const response = await fetch('http://localhost:3001/api/stocks');
        const stocks = await response.json();
        setAvailableStocks(stocks);
      } catch (error) {
        console.error('Failed to fetch available stocks:', error);
      } finally {
        setLoadingStocks(false);
      }
    };

    fetchAvailableStocks();
  }, []);

  // ESC key handler to close modal
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // Add event listener
    document.addEventListener('keydown', handleEscapeKey);

    // Cleanup event listener on component unmount
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [onClose]);

  // Helper function to clean stock names
  const cleanStockName = (name: string) => {
    return name.replace(/ Stock$/, '').replace(/ stock$/, '');
  };

  // Fetch data for all selected stocks manually (can't use hooks in loops)
  const [stockData, setStockData] = useState<{[key: string]: any}>({});
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});

  useEffect(() => {
    const fetchStockData = async () => {
      const newLoading: {[key: string]: boolean} = {};
      const newData: {[key: string]: any} = {};
      
      for (const symbol of selectedStocks) {
        newLoading[symbol] = true;
        try {
          const response = await fetch(`http://localhost:3001/api/stocks/${symbol}?timeframe=${timeframe}`);
          if (response.ok) {
            newData[symbol] = await response.json();
          }
        } catch (error) {
          console.error(`Error fetching data for ${symbol}:`, error);
        }
        newLoading[symbol] = false;
      }
      
      setStockData(newData);
      setLoading(newLoading);
    };

    if (selectedStocks.length > 0) {
      fetchStockData();
    }
  }, [selectedStocks, timeframe]);

  // Create stockDataHooks-compatible format for backward compatibility
  const stockDataHooks = selectedStocks.map(symbol => ({
    symbol,
    data: stockData[symbol],
    loading: loading[symbol] || false,
    error: null
  }));

  // Memoized calculation of comparison data
  const comparisonData = useMemo(() => {
    const allData = stockDataHooks
      .filter(hook => hook.data?.price_history && hook.data.price_history.length > 0)
      .map(hook => ({
        symbol: hook.symbol,
        prices: hook.data!.price_history!.sort((a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime())
      }));

    if (allData.length === 0) return [];

    // Find all unique dates across all stocks (union instead of intersection)
    const allDatesSet = new Set<string>();
    allData.forEach(stock => {
      stock.prices.forEach((p: any) => allDatesSet.add(p.date));
    });

    const sortedDates = Array.from(allDatesSet).sort();

    // For each stock, find its first available price as baseline (0% growth point)
    const stockBaselines: {[symbol: string]: number} = {};
    allData.forEach(stock => {
      stockBaselines[stock.symbol] = stock.prices[0].close;
    });

    // Create normalized percentage change data
    return sortedDates.map(date => {
      const dataPoint: any = { date };
      
      allData.forEach(stock => {
        const priceData = stock.prices.find((p: any) => p.date === date);
        if (priceData) {
          // Calculate percentage change from the stock's own baseline (first available price)
          const baselinePrice = stockBaselines[stock.symbol];
          const percentChange = ((priceData.close - baselinePrice) / baselinePrice) * 100;
          dataPoint[stock.symbol] = percentChange;
        } else {
          // If stock doesn't have data for this date, don't include it in the chart for this date
          // This allows stocks with different trading histories to be compared properly
          dataPoint[stock.symbol] = undefined;
        }
      });
      
      return dataPoint;
    });
  }, [stockDataHooks]);

  // Memoized performance metrics
  const performanceMetrics = useMemo(() => {
    return stockDataHooks
      .filter(hook => hook.data?.price_history && hook.data.price_history.length > 0)
      .map(hook => {
        const prices = hook.data!.price_history!;
        const firstPrice = prices[0].close;
        const lastPrice = prices[prices.length - 1].close;
        const totalReturn = ((lastPrice - firstPrice) / firstPrice) * 100;
        
        // Calculate volatility (standard deviation of daily returns)
        const dailyReturns = prices.slice(1).map((price: any, i: number) => 
          ((price.close - prices[i].close) / prices[i].close) * 100
        );
        const avgReturn = dailyReturns.reduce((a: number, b: number) => a + b, 0) / dailyReturns.length;
        const variance = dailyReturns.reduce((sum: number, ret: number) => sum + Math.pow(ret - avgReturn, 2), 0) / dailyReturns.length;
        const volatility = Math.sqrt(variance) * Math.sqrt(252); // Annualized
        
        return {
          symbol: hook.symbol,
          name: cleanStockName(hook.data!.name),
          totalReturn: totalReturn.toFixed(1),
          volatility: volatility.toFixed(1),
          currentPrice: lastPrice,
          priceChange: (lastPrice - firstPrice).toFixed(1)
        };
      });
  }, [stockDataHooks]);

  const addStock = useCallback((symbol: string) => {
    if (!selectedStocks.includes(symbol)) {
      setSelectedStocks(prev => [...prev, symbol]);
    }
  }, [selectedStocks]);

  const removeStock = useCallback((symbol: string) => {
    setSelectedStocks(prev => prev.filter(s => s !== symbol));
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatPrice = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return 'N/A';
    return `${numPrice.toFixed(2)} PLN`;
  };

  const isLoading = stockDataHooks.some(hook => hook.loading);
  const hasError = stockDataHooks.some(hook => hook.error);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
      <div 
        ref={dragRef}
        {...dragProps}
        className="bg-white dark:bg-gray-800 rounded-lg max-w-6xl w-full max-h-[95vh] overflow-y-auto shadow-2xl"
        style={{
          ...dragProps.style,
          width: '95%',
          maxWidth: '1200px',
          transform: dragProps.style.left === 0 && dragProps.style.top === 0 ? 'translate(-50%, -50%)' : 'none',
          left: dragProps.style.left === 0 ? '50%' : dragProps.style.left,
          top: dragProps.style.top === 0 ? '50%' : dragProps.style.top,
        }}
      >
        {/* Header - Drag Handle */}
        <div 
          ref={handleRef}
          {...handleProps}
          className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700 select-none"
        >
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              📈 Stock Comparison Analysis
            </h2>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              🖱️ Drag to move
            </div>
          </div>
          <Button variant="ghost" onClick={onClose}>
            <XMarkIcon className="h-6 w-6" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Stock Selection */}
          <Card className="p-4">
            <div className="space-y-3">
              {/* Header with Add stock button and Timeframe selector */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Compare stocks:
                  </span>
                  
                  {/* Fixed position Add stock dropdown */}
                  {!loadingStocks && (
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          addStock(e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                      defaultValue=""
                    >
                      <option value="">+ Add stock</option>
                      {availableStocks
                        .filter(stock => !selectedStocks.includes(stock.symbol))
                        .map(stock => (
                          <option key={stock.symbol} value={stock.symbol}>
                            {stock.symbol} - {cleanStockName(stock.name)}
                          </option>
                        ))}
                    </select>
                  )}
                  
                  {loadingStocks && (
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Loading stocks...
                    </div>
                  )}
                </div>
                
                {/* Timeframe selector */}
                <div className="flex space-x-2">
                  {(['1M', '3M', '6M', '1Y', 'MAX'] as const).map((tf) => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        timeframe === tf
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Selected stocks in rows of 5 */}
              {selectedStocks.length > 0 && (
                <div className="space-y-2">
                  {Array.from({ length: Math.ceil(selectedStocks.length / 5) }, (_, rowIndex) => (
                    <div key={rowIndex} className="flex flex-wrap gap-2">
                      {selectedStocks
                        .slice(rowIndex * 5, (rowIndex + 1) * 5)
                        .map(symbol => (
                          <div
                            key={symbol}
                            className="flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                          >
                            {symbol}
                            <button
                              onClick={() => removeStock(symbol)}
                              className="ml-2 hover:text-blue-600 dark:hover:text-blue-300"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {selectedStocks.length === 0 ? (
            <Card className="p-8 text-center">
              <PlusIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                Select stocks to compare their performance
              </p>
              {availableStocks.length > 0 && (
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                  Available stocks: {availableStocks.map(s => s.symbol).join(', ')}
                </p>
              )}
            </Card>
          ) : (
            <>
              {/* Performance Comparison Chart */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Normalized Performance Comparison (%)
                </h3>
                
                {isLoading ? (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-gray-500 dark:text-gray-400">Loading chart data...</div>
                  </div>
                ) : hasError ? (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-red-500 dark:text-red-400">Error loading data</div>
                  </div>
                ) : comparisonData.length === 0 ? (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-gray-500 dark:text-gray-400">No data available for selected timeframe</div>
                  </div>
                ) : (
                  <div style={{ width: '100%', height: '400px' }}>
                    <ResponsiveContainer>
                      <LineChart data={comparisonData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={formatDate}
                        />
                        <YAxis 
                          tickFormatter={(value) => `${Math.round(value).toFixed(0)}%`}
                        />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleDateString('pl-PL')}
                          formatter={(value: number) => [`${value.toFixed(1)}%`, 'Return']}
                        />
                        <Legend />
                        {selectedStocks.map((symbol, index) => (
                          <Line
                            key={symbol}
                            type="monotone"
                            dataKey={symbol}
                            stroke={CHART_COLORS[index % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>

              {/* Performance Metrics Table */}
              {performanceMetrics.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Performance Metrics ({timeframe})
                  </h3>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b border-gray-200 dark:border-gray-700">
                          <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                            Stock
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                            Current Price
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                            Total Return
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                            Price Change
                          </th>
                          <th className="text-right py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                            Volatility
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {performanceMetrics.map((metric, index) => (
                          <tr key={metric.symbol}>
                            <td className="py-3 px-4">
                              <div className="flex items-center">
                                <div 
                                  className="w-3 h-3 rounded-full mr-3"
                                  style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                                />
                                <div>
                                  <div className="font-medium text-gray-900 dark:text-white">
                                    {metric.symbol}
                                  </div>
                                  <div className="text-sm text-gray-500 dark:text-gray-400">
                                    {metric.name}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {formatPrice(metric.currentPrice)}
                            </td>
                            <td className={`py-3 px-4 text-right font-medium ${
                              parseFloat(metric.totalReturn) >= 0 
                                ? 'text-green-600 dark:text-green-400' 
                                : 'text-red-600 dark:text-red-400'
                            }`}>
                              {parseFloat(metric.totalReturn) >= 0 ? '+' : ''}{metric.totalReturn}%
                            </td>
                            <td className={`py-3 px-4 text-right ${
                              parseFloat(metric.priceChange) >= 0 
                                ? 'text-green-600 dark:text-green-400' 
                                : 'text-red-600 dark:text-red-400'
                            }`}>
                              {parseFloat(metric.priceChange) >= 0 ? '+' : ''}{formatPrice(parseFloat(metric.priceChange))}
                            </td>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {metric.volatility}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}