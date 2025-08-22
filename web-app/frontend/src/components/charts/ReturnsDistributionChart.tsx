import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

interface ReturnsData {
  date: string;
  daily_return: number | string | null | undefined;
}

interface ReturnsDistributionChartProps {
  data: ReturnsData[];
  symbol: string;
  height?: number;
  bins?: number;
}

export default function ReturnsDistributionChart({ 
  data, 
  symbol, 
  height = 300,
  bins = 30
}: ReturnsDistributionChartProps) {
  console.log(`📊 ReturnsDistributionChart: Processing ${data.length} data points for ${symbol}`);

  const distributionData = useMemo(() => {
    // Filter out null/undefined returns and convert to numbers
    const validReturns = data
      .filter(d => {
        if (d.daily_return === null || d.daily_return === undefined) return false;
        
        const returnValue = typeof d.daily_return === 'string' 
          ? parseFloat(d.daily_return as string)
          : d.daily_return as number;
        
        return !isNaN(returnValue) && isFinite(returnValue);
      })
      .map(d => {
        const returnValue = typeof d.daily_return === 'string' 
          ? parseFloat(d.daily_return as string)
          : d.daily_return as number;
        return returnValue;
      });

    if (validReturns.length === 0) return { histogramData: [], stats: null };

    // Calculate statistics
    const mean = validReturns.reduce((sum, val) => sum + val, 0) / validReturns.length;
    const variance = validReturns.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / validReturns.length;
    const stdDev = Math.sqrt(variance);
    const min = Math.min(...validReturns);
    const max = Math.max(...validReturns);

    // Create histogram bins
    const range = max - min;
    const binWidth = range / bins;
    
    // Initialize bins
    const histogram: { [key: string]: number } = {};
    const binCenters: number[] = [];
    
    for (let i = 0; i < bins; i++) {
      const binStart = min + (i * binWidth);
      const binCenter = binStart + (binWidth / 2);
      binCenters.push(binCenter);
      histogram[binCenter.toFixed(3)] = 0;
    }

    // Fill histogram
    validReturns.forEach(returnValue => {
      const binIndex = Math.min(Math.floor((returnValue - min) / binWidth), bins - 1);
      const binCenter = binCenters[binIndex];
      const key = binCenter.toFixed(3);
      histogram[key]++;
    });

    // Convert to array format for Recharts
    const histogramData = Object.entries(histogram).map(([binCenter, count]) => ({
      binCenter: parseFloat(binCenter),
      count,
      frequency: (count / validReturns.length) * 100,
      label: `${parseFloat(binCenter).toFixed(1)}%`,
      isMeanBin: Math.abs(parseFloat(binCenter) - mean) <= (binWidth / 2)
    })).sort((a, b) => a.binCenter - b.binCenter);

    // Find the closest bin to the mean for reference line
    const meanBinIndex = histogramData.reduce((closestIndex, bin, index) => {
      const currentDistance = Math.abs(bin.binCenter - mean);
      const closestDistance = Math.abs(histogramData[closestIndex].binCenter - mean);
      return currentDistance < closestDistance ? index : closestIndex;
    }, 0);
    
    const meanBinLabel = histogramData[meanBinIndex]?.label || `${mean.toFixed(1)}%`;

    const stats = {
      mean,
      stdDev,
      min,
      max,
      count: validReturns.length,
      skewness: calculateSkewness(validReturns, mean, stdDev),
      positiveCount: validReturns.filter(r => r > 0).length,
      negativeCount: validReturns.filter(r => r < 0).length,
      zeroCount: validReturns.filter(r => r === 0).length
    };

    return { histogramData, stats, meanBinLabel };
  }, [data, bins]);

  // Helper function to calculate skewness
  function calculateSkewness(values: number[], mean: number, stdDev: number): number {
    if (stdDev === 0) return 0;
    const n = values.length;
    const skewnessSum = values.reduce((sum, val) => {
      return sum + Math.pow((val - mean) / stdDev, 3);
    }, 0);
    return skewnessSum / n;
  }

  const { histogramData, stats, meanBinLabel } = distributionData;

  if (!stats || histogramData.length === 0) {
    return (
      <div className="w-full p-8 text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {symbol} Returns Distribution
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          No valid return data available for distribution analysis
        </p>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
          <p className="font-medium text-gray-900 dark:text-white mb-2">
            Return Range: ~{data.label}
          </p>
          <p className="text-sm text-blue-600 dark:text-blue-400">
            Count: {data.count} days
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Frequency: {data.frequency.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  const winRate = stats.count > 0 ? (stats.positiveCount / stats.count) * 100 : 0;

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {symbol} Returns Distribution
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400 mt-2">
          <div>
            <span className="font-medium">Mean:</span> {stats.mean.toFixed(3)}%
          </div>
          <div>
            <span className="font-medium">Std Dev:</span> {stats.stdDev.toFixed(3)}%
          </div>
          <div>
            <span className="font-medium">Skewness:</span> {stats.skewness.toFixed(2)}
          </div>
          <div>
            <span className="font-medium">Win Rate:</span> {winRate.toFixed(1)}%
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
          <div>
            <span className="text-green-600 dark:text-green-400">Positive:</span> {stats.positiveCount}
          </div>
          <div>
            <span className="text-red-600 dark:text-red-400">Negative:</span> {stats.negativeCount}
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Neutral:</span> {stats.zeroCount}
          </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={histogramData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis 
            dataKey="label"
            stroke="#6B7280"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            label={{ value: 'Frequency (%)', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => `${value.toFixed(1)}%`}
            stroke="#6B7280"
            fontSize={12}
          />
          
          {/* Reference line at mean */}
          <ReferenceLine 
            x={meanBinLabel} 
            stroke="#ef4444" 
            strokeWidth={2} 
            strokeDasharray="5 5"
            label={{ value: `Mean: ${stats.mean.toFixed(3)}%`, position: "top" }}
          />
          
          {/* Reference line at zero */}
          <ReferenceLine 
            x="0.0%" 
            stroke="#374151" 
            strokeWidth={1}
            label={{ value: "0%", position: "bottom" }}
          />
          
          <Bar 
            dataKey="frequency"
            name="Frequency"
          >
            {histogramData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.isMeanBin ? "#ef4444" : "#3b82f6"} 
                opacity={entry.isMeanBin ? 0.9 : 0.7}
              />
            ))}
          </Bar>
          
          <Tooltip content={<CustomTooltip />} />
        </BarChart>
      </ResponsiveContainer>
      
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Bell curve showing distribution of {stats.count} daily returns. 
        Red dashed line indicates mean return ({stats.mean.toFixed(3)}%).
        {stats.skewness > 0.5 && " Distribution is right-skewed (positive tail)."}
        {stats.skewness < -0.5 && " Distribution is left-skewed (negative tail)."}
        {Math.abs(stats.skewness) <= 0.5 && " Distribution is approximately symmetric."}
      </div>
    </div>
  );
}