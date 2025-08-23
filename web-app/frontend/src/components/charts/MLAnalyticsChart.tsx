import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

interface ModelInfo {
  model_version: string;
  status: string;
  test_roc_auc: number;
  test_accuracy: number;
  training_records: number;
  validation_records: number;
  test_records: number;
  feature_count: number;
  training_start_date: string;
  training_end_date: string;
  trained_at: string;
}

interface PerformanceMetrics {
  confusion_matrix: number[][];
  roc_curve: {
    fpr: number[];
    tpr: number[];
  };
}

interface PredictionsSummary {
  total_predictions: number;
  positive_predictions: number;
  negative_predictions: number;
  accuracy_rate: number;
  latest_predictions: Array<{
    prediction_date: string;
    target_date: string;
    predicted_class: boolean;
    prediction_probability: number;
    actual_class: boolean | null;
    trading_signal: string;
  }>;
}

interface TrainingStatistics {
  test_roc_auc: number;
  test_accuracy: number;
  test_f1_score: number;
  cv_score: number;
  validation_roc_auc: number;
  precision: number;
  recall: number;
  calculated_f1_score: number;
  training_records: number;
  validation_records: number;
  test_records: number;
}

interface FeatureImportance {
  feature_name: string;
  importance: number;
}

interface MLAnalyticsData {
  symbol: string;
  model_info: ModelInfo;
  performance_metrics: PerformanceMetrics;
  predictions_summary: PredictionsSummary;
  training_statistics: TrainingStatistics;
  feature_importance: FeatureImportance[];
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

interface MLAnalyticsProps {
  symbol: string;
  data: MLAnalyticsData;
  stockData: StockInfo;
}

export default function MLAnalyticsChart({ symbol, data, stockData }: MLAnalyticsProps) {
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;
  const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString('pl-PL');
  
  const formatPrice = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice)) return 'N/A';
    return `${numPrice.toFixed(2)} PLN`;
  };

  // Prepare ROC curve data for Recharts
  const rocData = data.performance_metrics.roc_curve.fpr.map((fpr, i) => ({
    fpr,
    tpr: data.performance_metrics.roc_curve.tpr[i] || 0,
    diagonal: fpr // Perfect diagonal reference line
  }));

  // Prepare confusion matrix data for visualization
  const confusionData = [
    { label: 'True Negative', value: data.performance_metrics.confusion_matrix[0][0], color: '#1f77b4' },
    { label: 'False Positive', value: data.performance_metrics.confusion_matrix[0][1], color: '#ff7f0e' },
    { label: 'False Negative', value: data.performance_metrics.confusion_matrix[1][0], color: '#d62728' },
    { label: 'True Positive', value: data.performance_metrics.confusion_matrix[1][1], color: '#2ca02c' },
  ];

  // Prepare prediction distribution data
  const distributionData = [
    { 
      name: 'Negative Predictions', 
      value: data.predictions_summary.negative_predictions,
      fill: '#ef4444'
    },
    { 
      name: 'Positive Predictions', 
      value: data.predictions_summary.positive_predictions,
      fill: '#22c55e'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Model Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <div className="text-sm text-gray-500 dark:text-gray-400">Model Version</div>
          <div className="text-sm font-semibold text-gray-900 dark:text-white break-all">
            {data.model_info.model_version}
          </div>
          <div className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
            data.model_info.status === 'active' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200'
          }`}>
            {data.model_info.status}
          </div>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <div className="text-sm text-gray-500 dark:text-gray-400">ROC-AUC Score</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {data.model_info.test_roc_auc.toFixed(3)}
          </div>
          <div className={`text-xs ${
            data.model_info.test_roc_auc >= 0.55 ? 'text-green-600 dark:text-green-400' :
            data.model_info.test_roc_auc >= 0.50 ? 'text-yellow-600 dark:text-yellow-400' :
            'text-red-600 dark:text-red-400'
          }`}>
            {data.model_info.test_roc_auc >= 0.55 ? '✅ Good' :
             data.model_info.test_roc_auc >= 0.50 ? '⚠️ Fair' :
             '❌ Poor'}
          </div>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <div className="text-sm text-gray-500 dark:text-gray-400">Test Accuracy</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatPercent(data.model_info.test_accuracy)}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {data.model_info.test_records} test samples
          </div>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <div className="text-sm text-gray-500 dark:text-gray-400">Total Predictions</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {data.predictions_summary.total_predictions.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {data.model_info.feature_count} features
          </div>
        </div>
      </div>

      {/* Most Recent Prediction */}
      {data.predictions_summary.latest_predictions.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Latest ML Prediction
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Target Date</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Prediction</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Probability</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Signal</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actual</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {(() => {
                  const mostRecent = data.predictions_summary.latest_predictions[0];
                  return (
                    <tr key="most-recent" className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">
                        {formatDate(mostRecent.prediction_date)}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">
                        {formatDate(mostRecent.target_date)}
                      </td>
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          mostRecent.predicted_class
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {mostRecent.predicted_class ? '📈 Growth' : '📉 Decline'}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">
                        {formatPercent(mostRecent.prediction_probability)}
                      </td>
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          mostRecent.trading_signal === 'BUY'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            : mostRecent.trading_signal === 'SELL'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200'
                        }`}>
                          {mostRecent.trading_signal || 'HOLD'}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">
                        {mostRecent.actual_class !== null ? (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            mostRecent.actual_class
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {mostRecent.actual_class ? '✅ Growth' : '❌ Decline'}
                          </span>
                        ) : (
                          <span className="text-gray-500 dark:text-gray-400 text-xs">Pending</span>
                        )}
                      </td>
                    </tr>
                  );
                })()}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Price Data Table */}
      {stockData && stockData.price_history && stockData.price_history.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
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
                {stockData.price_history.slice(-10).reverse().map((price, index) => {
                  const isGain = price.close > price.open;
                  const isLoss = price.close < price.open;
                  const isFlat = price.close === price.open;
                  
                  return (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatDate(price.date)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.open)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.high)}</td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{formatPrice(price.low)}</td>
                      <td className="px-4 py-2 text-sm font-medium text-gray-900 dark:text-white">
                        <div className="flex items-center space-x-2">
                          <span>{formatPrice(price.close)}</span>
                          {isGain && (
                            <span className="text-green-500 dark:text-green-400 text-lg font-bold" title="Close > Open">
                              ▲
                            </span>
                          )}
                          {isLoss && (
                            <span className="text-red-500 dark:text-red-400 text-lg font-bold" title="Close < Open">
                              ▼
                            </span>
                          )}
                          {isFlat && (
                            <span className="text-gray-500 dark:text-gray-400 text-lg font-bold" title="Close = Open">
                              ■
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{price.volume.toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 2x2 Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            {symbol} - Confusion Matrix
          </h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={confusionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="label" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value: number) => [value.toLocaleString(), 'Count']}
                />
                <Bar dataKey="value" fill="#3b82f6">
                  {confusionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
            Accuracy: {formatPercent(data.predictions_summary.accuracy_rate)}
          </div>
        </div>

        {/* ROC Curve */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            {symbol} - ROC Curve
          </h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <LineChart data={rocData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="fpr" 
                  domain={[0, 1]}
                  label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  domain={[0, 1]}
                  label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value: number) => [value.toFixed(3), 'TPR/FPR']}
                  labelFormatter={(value: number) => `FPR: ${value.toFixed(3)}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="diagonal" 
                  stroke="#666666" 
                  strokeDasharray="5 5"
                  dot={false}
                  strokeWidth={1}
                />
                <Line 
                  type="monotone" 
                  dataKey="tpr" 
                  stroke="#ff7f0e" 
                  strokeWidth={3}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
            AUC: {data.model_info.test_roc_auc.toFixed(3)}
          </div>
        </div>

        {/* Prediction Distribution */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Prediction Distribution
          </h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={distributionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  formatter={(value: number) => [value.toLocaleString(), 'Predictions']}
                />
                <Bar dataKey="value" fill="#8884d8">
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
            Positive: {formatPercent(data.predictions_summary.positive_predictions / data.predictions_summary.total_predictions)} | 
            Negative: {formatPercent(data.predictions_summary.negative_predictions / data.predictions_summary.total_predictions)}
          </div>
        </div>

        {/* Training Statistics */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Training Statistics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Test ROC-AUC:</span>
              <span className={`font-medium ${
                data.training_statistics.test_roc_auc >= 0.55 ? 'text-green-600 dark:text-green-400' :
                data.training_statistics.test_roc_auc >= 0.50 ? 'text-yellow-600 dark:text-yellow-400' :
                'text-red-600 dark:text-red-400'
              }`}>
                {data.training_statistics.test_roc_auc.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Test Accuracy:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formatPercent(data.training_statistics.test_accuracy)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Precision:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data.training_statistics.precision > 0 ? formatPercent(data.training_statistics.precision) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Recall:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data.training_statistics.recall > 0 ? formatPercent(data.training_statistics.recall) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">F1-Score:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data.training_statistics.calculated_f1_score > 0 ? 
                  data.training_statistics.calculated_f1_score.toFixed(3) : 
                  (data.training_statistics.test_f1_score > 0 ? 
                    data.training_statistics.test_f1_score.toFixed(3) : 'N/A')
                }
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Validation ROC-AUC:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data.training_statistics.validation_roc_auc > 0 ? 
                  data.training_statistics.validation_roc_auc.toFixed(3) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">CV Score:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data.training_statistics.cv_score > 0 ? 
                  data.training_statistics.cv_score.toFixed(3) : 'N/A'}
              </span>
            </div>
            <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Training Split: {data.training_statistics.training_records?.toLocaleString() || 0} / {data.training_statistics.validation_records?.toLocaleString() || 0} / {data.training_statistics.test_records?.toLocaleString() || 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Importance Chart */}
      {data.feature_importance.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Top Feature Importance
          </h3>
          <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer>
              <BarChart 
                data={data.feature_importance.slice(0, 10)} 
                layout="horizontal"
                margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis 
                  type="category" 
                  dataKey="feature_name" 
                  width={90}
                  fontSize={12}
                />
                <Tooltip 
                  formatter={(value: number) => [value.toFixed(4), 'Importance']}
                />
                <Bar dataKey="importance" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

    </div>
  );
}