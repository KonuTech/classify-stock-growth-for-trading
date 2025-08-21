import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface StockDetailProps {
  symbol: string;
  onClose: () => void;
}

interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockInfo {
  symbol: string;
  name: string;
  currency: string;
  total_records: number;
  latest_date: string;
  latest_price: number;
  price_history: PriceData[];
}

export default function StockDetail({ symbol, onClose }: StockDetailProps) {
  const [stockData, setStockData] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y'>('3M');

  useEffect(() => {
    fetchStockDetail();
  }, [symbol, timeframe]);

  const fetchStockDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:3001/api/stocks/${symbol}?timeframe=${timeframe}`);
      const data = await response.json();
      setStockData(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch stock details');
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      minimumFractionDigits: 2
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL');
  };

  const calculatePriceChange = () => {
    if (!stockData?.price_history || stockData.price_history.length < 2) return null;
    
    const latest = stockData.price_history[stockData.price_history.length - 1];
    const previous = stockData.price_history[0];
    const change = latest.close - previous.close;
    const changePercent = (change / previous.close) * 100;
    
    return { change, changePercent };
  };

  const priceChange = calculatePriceChange();

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8">
          <div className="text-center text-gray-900 dark:text-white">Loading stock details...</div>
        </div>
      </div>
    );
  }

  if (error || !stockData) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8">
          <div className="text-center text-red-600 dark:text-red-400">{error || 'Stock not found'}</div>
          <button 
            onClick={onClose} 
            className="mt-4 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-500"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{stockData.symbol}</h2>
            <p className="text-gray-600 dark:text-gray-300">{stockData.name}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
          >
            <XMarkIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Stock Info */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="text-sm text-gray-500 dark:text-gray-400">Current Price</div>
              <div className="text-xl font-semibold text-gray-900 dark:text-white">
                {formatPrice(stockData.latest_price)}
              </div>
            </div>
            
            {priceChange && (
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <div className="text-sm text-gray-500 dark:text-gray-400">Change ({timeframe})</div>
                <div className={`text-xl font-semibold ${priceChange.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {priceChange.change >= 0 ? '+' : ''}{formatPrice(priceChange.change)}
                  <span className="text-sm ml-1">
                    ({priceChange.changePercent >= 0 ? '+' : ''}{priceChange.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            )}
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Records</div>
              <div className="text-xl font-semibold text-gray-900 dark:text-white">
                {stockData.total_records.toLocaleString()}
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="text-sm text-gray-500 dark:text-gray-400">Latest Date</div>
              <div className="text-xl font-semibold text-gray-900 dark:text-white">
                {formatDate(stockData.latest_date)}
              </div>
            </div>
          </div>

          {/* Timeframe Selector */}
          <div className="mb-4">
            <div className="flex space-x-2">
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

          {/* Price Chart */}
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Price History</h3>
            <div style={{ width: '100%', height: '300px' }}>
              <ResponsiveContainer>
                <LineChart data={stockData.price_history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString('pl-PL', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis 
                    domain={['dataMin - 1', 'dataMax + 1']}
                    tickFormatter={formatPrice}
                  />
                  <Tooltip 
                    labelFormatter={(value) => formatDate(value)}
                    formatter={(value: number) => [formatPrice(value), 'Close Price']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="close" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Price Data Table */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Recent Price Data</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Open</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">High</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Low</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Close</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Volume</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {stockData.price_history.slice(-10).reverse().map((price, index) => (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatDate(price.date)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.open)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.high)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.low)}</td>
                      <td className="px-4 py-2 text-sm font-medium text-gray-900 dark:text-white">{formatPrice(price.close)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{price.volume.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}