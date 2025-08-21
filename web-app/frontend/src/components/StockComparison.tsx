import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { XMarkIcon, PlusIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useStockData } from '../hooks/useStockData';
import Card from './ui/Card';
import Button from './ui/Button';

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
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y'>('3M');
  const [availableStocks, setAvailableStocks] = useState<Stock[]>([]);
  const [loadingStocks, setLoadingStocks] = useState(true);

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

  // Fetch data for all selected stocks using our custom hook
  const stockDataHooks = selectedStocks.map(symbol => ({
    symbol,
    ...useStockData(symbol, timeframe)
  }));

  // Memoized calculation of comparison data
  const comparisonData = useMemo(() => {
    const allData = stockDataHooks
      .filter(hook => hook.data?.price_history && hook.data.price_history.length > 0)
      .map(hook => ({
        symbol: hook.symbol,
        prices: hook.data!.price_history!
      }));

    if (allData.length === 0) return [];

    // Find common dates across all stocks
    const allDates = allData.reduce((dates, stock) => {
      const stockDates = new Set(stock.prices.map(p => p.date));
      return dates.size === 0 
        ? stockDates 
        : new Set([...dates].filter(date => stockDates.has(date)));
    }, new Set<string>());

    const sortedDates = Array.from(allDates).sort();

    // Create normalized percentage change data
    return sortedDates.map(date => {
      const dataPoint: any = { date };
      
      allData.forEach(stock => {
        const priceData = stock.prices.find(p => p.date === date);
        if (priceData) {
          const firstPrice = stock.prices.find(p => sortedDates.includes(p.date))?.close || priceData.close;
          const percentChange = ((priceData.close - firstPrice) / firstPrice) * 100;
          dataPoint[stock.symbol] = percentChange;
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
        const dailyReturns = prices.slice(1).map((price, i) => 
          ((price.close - prices[i].close) / prices[i].close) * 100
        );
        const avgReturn = dailyReturns.reduce((a, b) => a + b, 0) / dailyReturns.length;
        const variance = dailyReturns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / dailyReturns.length;
        const volatility = Math.sqrt(variance) * Math.sqrt(252); // Annualized
        
        return {
          symbol: hook.symbol,
          name: hook.data!.name,
          totalReturn: totalReturn.toFixed(2),
          volatility: volatility.toFixed(2),
          currentPrice: lastPrice,
          priceChange: (lastPrice - firstPrice).toFixed(2)
        };
      });
  }, [stockDataHooks]);

  const addStock = useCallback((symbol: string) => {
    if (!selectedStocks.includes(symbol) && selectedStocks.length < 5) {
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

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 2
    }).format(price);
  };

  const isLoading = stockDataHooks.some(hook => hook.loading);
  const hasError = stockDataHooks.some(hook => hook.error);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-6xl w-full max-h-[95vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            📈 Stock Comparison Analysis
          </h2>
          <Button variant="ghost" onClick={onClose}>
            <XMarkIcon className="h-6 w-6" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Stock Selection */}
          <Card className="p-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Compare stocks:
              </span>
              
              {/* Selected stocks */}
              {selectedStocks.map(symbol => (
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
              
              {/* Add stock dropdown */}
              {selectedStocks.length < 5 && !loadingStocks && (
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
                        {stock.symbol} - {stock.name}
                      </option>
                    ))}
                </select>
              )}
              
              {loadingStocks && (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Loading stocks...
                </div>
              )}
              
              {/* Timeframe selector */}
              <div className="ml-auto flex space-x-2">
                {(['1M', '3M', '6M', '1Y'] as const).map((tf) => (
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
                          tickFormatter={(value) => `${value.toFixed(1)}%`}
                        />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleDateString('pl-PL')}
                          formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
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