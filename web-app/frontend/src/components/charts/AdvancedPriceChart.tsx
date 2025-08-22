import React from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PriceData {
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
}

interface AdvancedPriceChartProps {
  data: PriceData[];
  symbol: string;
  showMovingAverages?: boolean;
  showVolume?: boolean;
  height?: number;
}

export default function AdvancedPriceChart({ 
  data, 
  symbol, 
  showMovingAverages = true, 
  showVolume = true,
  height = 400 
}: AdvancedPriceChartProps) {
  console.log(`🔄 AdvancedPriceChart: Received ${data.length} data points for ${symbol}`);
  
  // Handle empty or invalid data
  if (!data || data.length === 0) {
    return (
      <div className="w-full">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {symbol} Price Analysis
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Price movement with technical indicators
          </p>
        </div>
        <div className="h-96 flex items-center justify-center text-center bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div>
            <div className="text-6xl text-amber-500 mb-4">📈</div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Advanced Data Available</h4>
            <p className="text-gray-600 dark:text-gray-400">
              Technical analysis data is not available for {symbol}.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Moving averages and volume data may be missing.
            </p>
          </div>
        </div>
      </div>
    );
  }
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

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
          <p className="font-medium text-gray-900 dark:text-white mb-2">
            {new Date(label).toLocaleDateString('pl-PL')}
          </p>
          <div className="space-y-1 text-sm">
            {data.close && (
              <p className="text-blue-600 dark:text-blue-400">
                Close: {formatPrice(data.close)}
              </p>
            )}
            {data.ma_20 && showMovingAverages && (
              <p className="text-orange-600 dark:text-orange-400">
                MA 20: {formatPrice(data.ma_20)}
              </p>
            )}
            {data.ma_50 && showMovingAverages && (
              <p className="text-red-600 dark:text-red-400">
                MA 50: {formatPrice(data.ma_50)}
              </p>
            )}
            {data.volume && showVolume && (
              <p className="text-green-600 dark:text-green-400">
                Volume: {formatVolume(data.volume)}
              </p>
            )}
            {data.daily_return && typeof data.daily_return === 'number' && (
              <p className={`${data.daily_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                Daily Return: {data.daily_return >= 0 ? '+' : ''}{data.daily_return.toFixed(2)}%
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {symbol} Price Analysis
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Price movement with technical indicators
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6B7280"
            fontSize={12}
          />
          <YAxis 
            yAxisId="price"
            orientation="left"
            tickFormatter={(value) => formatPrice(value)}
            stroke="#6B7280"
            fontSize={12}
          />
          {showVolume && (
            <YAxis 
              yAxisId="volume"
              orientation="right"
              tickFormatter={formatVolume}
              stroke="#6B7280"
              fontSize={12}
            />
          )}
          
          {/* Volume bars (background) */}
          {showVolume && (
            <Bar 
              yAxisId="volume"
              dataKey="volume" 
              fill="#10b981" 
              opacity={0.2}
              name="Volume"
            />
          )}
          
          {/* Price line */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Close Price"
          />
          
          {/* Moving averages */}
          {showMovingAverages && (
            <>
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="ma_20"
                stroke="#f59e0b"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="MA 20"
              />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="ma_50"
                stroke="#ef4444"
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
                name="MA 50"
              />
            </>
          )}
          
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}