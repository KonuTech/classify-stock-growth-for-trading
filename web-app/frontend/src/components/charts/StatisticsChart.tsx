import React from 'react';

interface StatisticsData {
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

interface StatisticsChartProps {
  data: StatisticsData[];
  symbol: string;
}

export default function StatisticsChart({ data, symbol }: StatisticsChartProps) {
  const calculateStatistics = () => {
    if (!data || data.length === 0) return null;

    const prices = data.map(d => d.close);
    const returns = data
      .map(d => d.daily_return)
      .filter(r => r !== null && r !== undefined && typeof r === 'number') as number[];
    
    const volumes = data.map(d => d.volume);

    const currentPrice = prices[prices.length - 1];
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    
    const avgReturn = returns.length > 0 ? returns.reduce((sum, r) => sum + r, 0) / returns.length : 0;
    const returnStdDev = returns.length > 1 
      ? Math.sqrt(returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / (returns.length - 1))
      : 0;
    
    const positiveReturns = returns.filter(r => r > 0).length;
    const winRate = returns.length > 0 ? (positiveReturns / returns.length) * 100 : 0;
    
    const avgVolume = volumes.reduce((sum, v) => sum + v, 0) / volumes.length;
    const maxVolume = Math.max(...volumes);
    
    const priceChange = prices.length > 1 ? ((currentPrice - prices[0]) / prices[0]) * 100 : 0;
    
    const sortedReturns = [...returns].sort((a, b) => a - b);
    const medianReturn = sortedReturns.length > 0 
      ? sortedReturns.length % 2 === 0
        ? (sortedReturns[sortedReturns.length / 2 - 1] + sortedReturns[sortedReturns.length / 2]) / 2
        : sortedReturns[Math.floor(sortedReturns.length / 2)]
      : 0;

    const maxDrawdown = calculateMaxDrawdown(prices);
    const sharpeRatio = returnStdDev !== 0 ? (avgReturn * Math.sqrt(252)) / (returnStdDev * Math.sqrt(252)) : 0;

    return {
      currentPrice,
      minPrice,
      maxPrice,
      priceChange,
      avgReturn,
      returnStdDev,
      medianReturn,
      winRate,
      avgVolume,
      maxVolume,
      maxDrawdown,
      sharpeRatio,
      totalDays: data.length,
      tradingDays: returns.length
    };
  };

  const calculateMaxDrawdown = (prices: number[]): number => {
    let maxDrawdown = 0;
    let peak = prices[0];
    
    for (let i = 1; i < prices.length; i++) {
      if (prices[i] > peak) {
        peak = prices[i];
      }
      const drawdown = (peak - prices[i]) / peak * 100;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }
    
    return maxDrawdown;
  };

  const formatPrice = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return 'N/A';
    return `${Math.round(numPrice)} PLN`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${Math.round(volume / 1000000)}M`;
    } else if (volume >= 1000) {
      return `${Math.round(volume / 1000)}K`;
    }
    return volume.toString();
  };

  const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${Math.round(value)}%`;

  const stats = calculateStatistics();

  if (!stats) {
    return (
      <div className="w-full p-8 text-center">
        <p className="text-gray-600 dark:text-gray-400">No data available for statistical analysis</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Price Statistics',
      stats: [
        { label: 'Current Price', value: formatPrice(stats.currentPrice) },
        { label: 'Price Range', value: `${formatPrice(stats.minPrice)} - ${formatPrice(stats.maxPrice)}` },
        { label: 'Total Return', value: formatPercent(stats.priceChange), color: stats.priceChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400' },
        { label: 'Max Drawdown', value: formatPercent(-stats.maxDrawdown), color: 'text-red-600 dark:text-red-400' }
      ]
    },
    {
      title: 'Return Statistics',
      stats: [
        { label: 'Average Daily Return', value: formatPercent(stats.avgReturn), color: stats.avgReturn >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400' },
        { label: 'Median Daily Return', value: formatPercent(stats.medianReturn), color: stats.medianReturn >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400' },
        { label: 'Daily Volatility', value: formatPercent(stats.returnStdDev) },
        { label: 'Win Rate', value: `${stats.winRate.toFixed(1)}%`, color: stats.winRate > 50 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400' }
      ]
    },
    {
      title: 'Volume Statistics',
      stats: [
        { label: 'Average Volume', value: formatVolume(stats.avgVolume) },
        { label: 'Maximum Volume', value: formatVolume(stats.maxVolume) },
        { label: 'Volume Ratio', value: `${((stats.maxVolume / stats.avgVolume)).toFixed(1)}x` },
        { label: 'Trading Days', value: stats.tradingDays.toString() }
      ]
    },
    {
      title: 'Risk Metrics',
      stats: [
        { label: 'Sharpe Ratio', value: stats.sharpeRatio.toFixed(1), color: stats.sharpeRatio > 1 ? 'text-green-600 dark:text-green-400' : stats.sharpeRatio > 0 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400' },
        { label: 'Annualized Return', value: formatPercent(stats.avgReturn * 252) },
        { label: 'Annualized Volatility', value: formatPercent(stats.returnStdDev * Math.sqrt(252)) },
        { label: 'Total Records', value: stats.totalDays.toString() }
      ]
    }
  ];

  return (
    <div className="w-full">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {symbol} Statistical Analysis
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Comprehensive statistical metrics and risk analysis
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {statCards.map((card, cardIndex) => (
          <div key={cardIndex} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
            <h4 className="text-base font-medium text-gray-900 dark:text-white mb-4">
              {card.title}
            </h4>
            <div className="space-y-3">
              {card.stats.map((stat, statIndex) => (
                <div key={statIndex} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {stat.label}
                  </span>
                  <span className={`text-sm font-medium ${stat.color || 'text-gray-900 dark:text-white'}`}>
                    {stat.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
          Key Insights
        </h4>
        <div className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
          <p>• <strong>Sharpe Ratio:</strong> Risk-adjusted returns ({stats.sharpeRatio > 1 ? 'Excellent' : stats.sharpeRatio > 0.5 ? 'Good' : 'Poor'})</p>
          <p>• <strong>Win Rate:</strong> {stats.winRate > 55 ? 'Strong upward bias' : stats.winRate > 45 ? 'Balanced performance' : 'Downward trend'}</p>
          <p>• <strong>Volatility:</strong> {stats.returnStdDev > 3 ? 'High risk' : stats.returnStdDev > 1.5 ? 'Moderate risk' : 'Low risk'} asset</p>
        </div>
      </div>
    </div>
  );
}