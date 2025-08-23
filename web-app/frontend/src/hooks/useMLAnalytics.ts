import { useState, useEffect } from 'react';

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

export interface MLAnalyticsData {
  symbol: string;
  model_info: ModelInfo;
  performance_metrics: PerformanceMetrics;
  predictions_summary: PredictionsSummary;
  training_statistics: TrainingStatistics;
  feature_importance: FeatureImportance[];
}

export const useMLAnalytics = (symbol: string) => {
  const [data, setData] = useState<MLAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMLAnalytics = async (stockSymbol: string) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`🤖 Fetching ML analytics for ${stockSymbol}...`);
      
      const response = await fetch(`http://localhost:3001/api/stocks/${stockSymbol}/ml-analytics`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`No ML model found for ${stockSymbol}`);
        }
        throw new Error(`Failed to fetch ML analytics: ${response.status}`);
      }
      
      const analyticsData = await response.json();
      console.log(`✅ ML analytics loaded for ${stockSymbol}`);
      
      setData(analyticsData);
      setLoading(false);
      
    } catch (err) {
      console.error('❌ Error fetching ML analytics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch ML analytics');
      setData(null);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol) {
      fetchMLAnalytics(symbol);
    }
  }, [symbol]);

  return { 
    data, 
    loading, 
    error, 
    refetch: () => fetchMLAnalytics(symbol) 
  };
};