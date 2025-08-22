import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ChartTabs from './ChartTabs';
import AdvancedPriceChart from './charts/AdvancedPriceChart';
import ReturnsChart from './charts/ReturnsChart';
import StatisticsChart from './charts/StatisticsChart';
import { useDrag } from '../hooks/useDrag';

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

interface AnalyticsData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  daily_return?: number;
  ma_20?: number;
  ma_50?: number;
  volume_ma_20?: number;
  volatility_20d?: number;
}

interface AnalyticsResponse {
  symbol: string;
  timeframe: string;
  data: AnalyticsData[];
}

export default function StockDetail({ symbol, onClose }: StockDetailProps) {
  const [stockData, setStockData] = useState<StockInfo | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y' | 'MAX'>('1Y');
  const [activeTab, setActiveTab] = useState<string>('overview');

  // Drag functionality
  const { dragRef, handleRef, dragProps, handleProps } = useDrag();

  // Tab options - moved here to be available for useEffect
  const tabOptions = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'advanced', label: 'Advanced Analysis', icon: '📈' },
    { id: 'returns', label: 'Returns', icon: '💹' },
    { id: 'statistics', label: 'Statistics', icon: '📋' },
  ];

  useEffect(() => {
    fetchStockDetail();
  }, [symbol, timeframe]);

  // ESC and TAB key handlers
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      } else if (event.key === 'Tab') {
        // Prevent default tab behavior (focus change)
        event.preventDefault();
        
        // Cycle through tabs
        const currentIndex = tabOptions.findIndex(tab => tab.id === activeTab);
        const nextIndex = (currentIndex + 1) % tabOptions.length;
        setActiveTab(tabOptions[nextIndex].id);
      }
    };

    // Add event listener
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup event listener on component unmount
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose, activeTab, tabOptions]);

  const fetchStockDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`🔄 Fetching data for ${symbol} with timeframe ${timeframe}`);
      
      // Fetch both basic stock data and analytics data
      const [stockResponse, analyticsResponse] = await Promise.all([
        fetch(`http://localhost:3001/api/stocks/${symbol}?timeframe=${timeframe}`),
        fetch(`http://localhost:3001/api/stocks/${symbol}/analytics?timeframe=${timeframe}`)
      ]);
      
      console.log(`📊 Stock response status: ${stockResponse.status}`);
      console.log(`📈 Analytics response status: ${analyticsResponse.status}`);
      
      if (!stockResponse.ok) {
        throw new Error(`Failed to fetch stock data: ${stockResponse.status}`);
      }
      
      if (!analyticsResponse.ok) {
        console.warn(`⚠️ Analytics request failed: ${analyticsResponse.status}`);
        // Continue without analytics data
        const stockData = await stockResponse.json();
        setStockData(stockData);
        setAnalyticsData(null);
        setLoading(false);
        return;
      }
      
      const stockData = await stockResponse.json();
      const analyticsData = await analyticsResponse.json();
      
      console.log(`✅ Stock data loaded: ${stockData.symbol}`);
      console.log(`✅ Analytics data loaded: ${analyticsData.data?.length || 0} records`);
      
      setStockData(stockData);
      setAnalyticsData(analyticsData);
      setLoading(false);
    } catch (err) {
      console.error('❌ Error fetching stock details:', err);
      setError('Failed to fetch stock details');
      setLoading(false);
    }
  };

  const formatPrice = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return 'N/A';
    return `${numPrice.toFixed(2)} PLN`;
  };

  const formatPriceInteger = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return 'N/A';
    return `${Math.round(numPrice)} PLN`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL');
  };

  // Helper function to clean stock names
  const cleanStockName = (name: string) => {
    return name.replace(/ Stock$/, '').replace(/ stock$/, '');
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
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
      <div 
        ref={dragRef}
        {...dragProps}
        className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
        style={{
          ...dragProps.style,
          width: '90%',
          maxWidth: '1000px',
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
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{stockData.symbol}</h2>
            <p className="text-gray-600 dark:text-gray-300">{cleanStockName(stockData.name)}</p>
            <div className="flex space-x-4 text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>🖱️ Drag to move</span>
              <span>⌨️ TAB: Next tab</span>
              <span>ESC: Close</span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
          >
            <XMarkIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pt-4">
          <ChartTabs 
            tabs={tabOptions}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {/* Stock Info & Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="text-sm text-gray-500 dark:text-gray-400">Current Price</div>
              <div className="text-xl font-semibold text-gray-900 dark:text-white">
                {stockData.latest_price ? 
                  formatPrice(stockData.latest_price) : 
                  <span className="text-amber-600 dark:text-amber-400 text-base">⚠️ Price data missing</span>
                }
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="text-sm text-gray-500 dark:text-gray-400">Change ({timeframe})</div>
              <div className="text-xl font-semibold text-gray-900 dark:text-white">
                {priceChange ? (
                  <span className={priceChange.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                    {priceChange.change >= 0 ? '+' : ''}{formatPrice(priceChange.change)}
                    <span className="text-sm ml-1">
                      ({priceChange.changePercent >= 0 ? '+' : ''}{priceChange.changePercent.toFixed(1)}%)
                    </span>
                  </span>
                ) : (
                  <span className="text-amber-600 dark:text-amber-400 text-base">⚠️ Insufficient data for change calculation</span>
                )}
              </div>
            </div>
            
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
          <div className="mb-6">
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

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Basic Price Chart */}
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Price History</h3>
                {stockData.price_history && stockData.price_history.length > 0 ? (
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
                          tickFormatter={formatPriceInteger}
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
                ) : (
                  <div className="h-64 flex items-center justify-center text-center">
                    <div>
                      <div className="text-6xl text-amber-500 mb-4">📊</div>
                      <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Price History Available</h4>
                      <p className="text-gray-600 dark:text-gray-400">
                        No historical price data found for {stockData.symbol} in the {timeframe} timeframe.
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                        Try selecting a different timeframe or check back later.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'advanced' && analyticsData && (
            <div className="space-y-6">
              <AdvancedPriceChart 
                data={analyticsData.data}
                symbol={stockData.symbol}
                showMovingAverages={true}
                showVolume={true}
                height={450}
              />
            </div>
          )}

          {activeTab === 'returns' && analyticsData && (
            <div className="space-y-6">
              <ReturnsChart 
                data={analyticsData.data.map(d => ({
                  date: d.date,
                  daily_return: d.daily_return
                }))}
                symbol={stockData.symbol}
                height={350}
                title="Daily Returns"
              />
            </div>
          )}

          {activeTab === 'statistics' && analyticsData && (
            <div className="space-y-6">
              <StatisticsChart 
                data={analyticsData.data}
                symbol={stockData.symbol}
              />
            </div>
          )}

          {!analyticsData && activeTab !== 'overview' && (
            <div className="bg-gray-50 dark:bg-gray-700 p-8 rounded-lg text-center">
              <div className="text-6xl text-amber-500 mb-4">⚠️</div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Analytics Data Unavailable</h4>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Advanced analytics data could not be loaded for <strong>{symbol}</strong>.
              </p>
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-left max-w-md mx-auto">
                <h5 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">Possible reasons:</h5>
                <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                  <li>• Backend analytics service is not running</li>
                  <li>• Database connection issues</li>
                  <li>• Insufficient data for technical analysis</li>
                  <li>• Stock symbol not found in analytics tables</li>
                </ul>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-4">
                📊 Try the <strong>Overview</strong> tab for basic price data
              </p>
            </div>
          )}

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