import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';
import ReturnsDistributionChart from './ReturnsDistributionChart';

interface ReturnsData {
  date: string;
  daily_return: number | string | null | undefined;
}

interface ReturnsChartProps {
  data: ReturnsData[];
  symbol: string;
  height?: number;
  title?: string;
}

export default function ReturnsChart({ 
  data, 
  symbol, 
  height = 300,
  title = "Daily Returns"
}: ReturnsChartProps) {
  console.log(`🔄 ReturnsChart: Received ${data.length} data points for ${symbol}`);
  console.log('📊 First 3 data points:', data.slice(0, 3));

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Filter out null/undefined returns and add color information
  const processedData = data
    .filter(d => {
      if (d.daily_return === null || d.daily_return === undefined) return false;
      
      // Convert string to number if necessary
      const returnValue = typeof d.daily_return === 'string' 
        ? parseFloat(d.daily_return as string)
        : d.daily_return as number;
      
      return !isNaN(returnValue) && isFinite(returnValue);
    })
    .map(d => {
      // Ensure daily_return is a number
      const returnValue = typeof d.daily_return === 'string' 
        ? parseFloat(d.daily_return as string)
        : d.daily_return as number;
        
      return {
        ...d,
        daily_return: returnValue,
        color: returnValue >= 0 ? '#10b981' : '#ef4444',
        abs_return: Math.abs(returnValue)
      };
    });

  console.log(`✅ ReturnsChart: Processed ${processedData.length} valid data points`);
  console.log('📈 Sample processed data:', processedData.slice(0, 3));

  // Handle case when no valid data is available
  if (processedData.length === 0) {
    return (
      <div className="w-full p-8 text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {symbol} {title}
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          No valid daily return data available for visualization
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
          Total data points received: {data.length}
        </p>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const returnValue = typeof data.daily_return === 'number' ? data.daily_return : 0;
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
          <p className="font-medium text-gray-900 dark:text-white mb-2">
            {new Date(label).toLocaleDateString('pl-PL')}
          </p>
          <p className={`text-sm ${returnValue >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            Daily Return: {returnValue >= 0 ? '+' : ''}{returnValue.toFixed(2)}%
          </p>
        </div>
      );
    }
    return null;
  };

  // Calculate some basic statistics
  const avgReturn = processedData.length > 0 
    ? processedData.reduce((sum, d) => sum + d.daily_return, 0) / processedData.length 
    : 0;
  const positiveReturns = processedData.filter(d => d.daily_return > 0).length;
  const totalReturns = processedData.length;
  const winRate = totalReturns > 0 ? (positiveReturns / totalReturns) * 100 : 0;

  return (
    <div className="w-full space-y-8">
      {/* Timeline Chart */}
      <div className="w-full">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {symbol} {title} Timeline
          </h3>
          <div className="flex space-x-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
            <span>Avg: {avgReturn.toFixed(3)}%</span>
            <span>Win Rate: {winRate.toFixed(1)}%</span>
            <span>Days: {totalReturns}</span>
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatDate}
              stroke="#6B7280"
              fontSize={12}
            />
            <YAxis 
              tickFormatter={(value) => `${value.toFixed(1)}%`}
              stroke="#6B7280"
              fontSize={12}
            />
            
            {/* Reference line at zero */}
            <ReferenceLine y={0} stroke="#374151" strokeWidth={1} />
            
            <Bar 
              dataKey="daily_return"
              name="Daily Return"
            >
              {processedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
            
            <Tooltip content={<CustomTooltip />} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Distribution Chart (Bell Curve) */}
      <div className="w-full border-t border-gray-200 dark:border-gray-700 pt-6">
        <ReturnsDistributionChart 
          data={data} 
          symbol={symbol} 
          height={height} 
        />
      </div>
    </div>
  );
}