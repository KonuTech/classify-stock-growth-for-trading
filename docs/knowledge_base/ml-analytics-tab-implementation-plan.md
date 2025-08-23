# ML Analytics Tab Implementation Plan

## Executive Summary

This document outlines the plan to add a new "ML Analytics" tab to the Stock Detail modal in our web application. The tab will showcase machine learning model training results, predictions, and performance metrics for each stock's XGBoost 7-day growth prediction model.

## Current State Analysis

### Database Structure ✅
- **ML Tables Available**: `ml_models`, `ml_predictions`, `ml_feature_data`, `ml_backtest_results`
- **Active Models**: 10 stocks with trained XGBoost models (CDR: 1536 predictions, BDX: 1505, KTY: 1470, etc.)
- **Model Performance**: ROC-AUC ranging from 0.409 (PLW) to 0.554 (BDX), Test Accuracy 0.414-0.538
- **Data Volume**: 9,563 total predictions across all stocks

### Current Web App Structure ✅
- **Component**: `StockDetail.tsx` with 4 existing tabs (Overview, Advanced Analysis, Returns, Statistics)
- **Architecture**: React with TypeScript, Recharts for visualization
- **Tab System**: `ChartTabs` component with keyboard navigation (TAB key cycling)
- **Data Flow**: Backend API endpoints → Frontend components → Chart visualization

### Inspiration from Jupyter Notebook ✅
- **Chart Types**: Confusion Matrix, ROC Curve, Precision-Recall Curve, Prediction Probability Distribution
- **Visualization Style**: 2×2 subplot layout, professional color schemes (Blues for heatmap, orange for ROC curve)
- **Key Metrics**: Model accuracy, ROC-AUC, confusion matrix values, feature importance

## Implementation Plan

### Phase 1: Backend API Development

#### 1.1 New API Endpoint
**Route**: `GET /api/stocks/:symbol/ml-analytics`

**Response Structure**:
```json
{
  "symbol": "XTB",
  "model_info": {
    "model_version": "v2.1_prod.20250823_072640",
    "status": "active",
    "test_roc_auc": 0.552859,
    "test_accuracy": 0.414097,
    "training_records": 0,
    "feature_count": 25,
    "training_start_date": "2023-01-01",
    "training_end_date": "2024-12-31"
  },
  "performance_metrics": {
    "confusion_matrix": [[734, 9], [781, 10]],
    "roc_curve": {
      "fpr": [0.0, 0.1, 0.2, ...],
      "tpr": [0.0, 0.15, 0.35, ...]
    },
    "precision_recall": {
      "precision": [1.0, 0.9, 0.8, ...],
      "recall": [0.0, 0.1, 0.2, ...]
    }
  },
  "predictions_summary": {
    "total_predictions": 454,
    "positive_predictions": 89,
    "negative_predictions": 365,
    "accuracy_rate": 0.742,
    "latest_predictions": [
      {
        "prediction_date": "2025-08-22",
        "target_date": "2025-08-29",
        "predicted_class": true,
        "prediction_probability": 0.73,
        "actual_class": null,
        "trading_signal": "BUY"
      }
    ]
  },
  "backtest_results": {
    "total_return": 0.156,
    "sharpe_ratio": 1.23,
    "win_rate": 0.52,
    "total_trades": 42
  },
  "feature_importance": [
    {"feature_name": "rsi_14", "importance": 0.134},
    {"feature_name": "macd_line", "importance": 0.098}
  ]
}
```

#### 1.2 Database Queries
- **Model Info**: JOIN `ml_models` with `base_instruments`
- **Performance Metrics**: Calculate confusion matrix from `ml_predictions` 
- **ROC/PR Curves**: Aggregate prediction probabilities and actual outcomes
- **Backtest Results**: Query `ml_backtest_results` table
- **Feature Importance**: Parse JSON from `ml_models.feature_importance`

### Phase 2: Frontend Component Development

#### 2.1 New Tab Addition
**File**: `web-app/frontend/src/components/StockDetail.tsx`
- Add ML Analytics tab to `tabOptions` array: `{ id: 'ml-analytics', label: 'ML Analytics', icon: '🤖' }`

#### 2.2 ML Analytics Component
**File**: `web-app/frontend/src/components/charts/MLAnalyticsChart.tsx`

**Component Structure**:
```tsx
interface MLAnalyticsProps {
  symbol: string;
  modelData: MLAnalyticsData;
}

export default function MLAnalyticsChart({ symbol, modelData }: MLAnalyticsProps) {
  return (
    <div className="space-y-6">
      {/* Model Overview Cards */}
      <ModelOverviewCards data={modelData.model_info} />
      
      {/* 2x2 Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ConfusionMatrixChart data={modelData.performance_metrics.confusion_matrix} />
        <ROCCurveChart data={modelData.performance_metrics.roc_curve} />
        <PrecisionRecallChart data={modelData.performance_metrics.precision_recall} />
        <PredictionDistributionChart predictions={modelData.predictions_summary} />
      </div>
      
      {/* Feature Importance */}
      <FeatureImportanceChart features={modelData.feature_importance} />
      
      {/* Recent Predictions Table */}
      <RecentPredictionsTable predictions={modelData.predictions_summary.latest_predictions} />
    </div>
  );
}
```

#### 2.3 Individual Chart Components

##### 2.3.1 ConfusionMatrixChart
- **Library**: Custom D3.js heatmap or recharts-compatible solution
- **Design**: Blue color scheme matching Jupyter notebook
- **Labels**: "Predicted Negative/Positive", "Actual Negative/Positive"

##### 2.3.2 ROCCurveChart  
- **Library**: Recharts LineChart
- **Features**: Orange curve, diagonal reference line, AUC annotation
- **Styling**: Match notebook's professional appearance

##### 2.3.3 PrecisionRecallChart
- **Library**: Recharts LineChart  
- **Features**: Green curve, AP (Average Precision) score display

##### 2.3.4 PredictionDistributionChart
- **Library**: Recharts BarChart
- **Features**: Stacked histogram, negative/positive class distribution

##### 2.3.5 FeatureImportanceChart
- **Library**: Recharts BarChart
- **Features**: Horizontal bar chart, top 10-15 features

#### 2.4 Model Overview Cards
**Design**: 4-card grid showing key metrics
- **Model Version & Status**
- **ROC-AUC Score**: Large prominent number with color coding
- **Test Accuracy**: Percentage with visual indicator
- **Total Predictions**: Count with timeframe

### Phase 3: Data Integration

#### 3.1 API Hook Development
**File**: `web-app/frontend/src/hooks/useMLAnalytics.ts`
```tsx
export const useMLAnalytics = (symbol: string) => {
  const [data, setData] = useState<MLAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMLAnalytics(symbol);
  }, [symbol]);

  return { data, loading, error, refetch: () => fetchMLAnalytics(symbol) };
};
```

#### 3.2 Integration with StockDetail
- **Conditional Loading**: Show loading state while fetching ML data
- **Error Handling**: Graceful degradation if no ML model exists for stock
- **Cache Integration**: Leverage existing Redis caching for ML endpoint

### Phase 4: Backend Implementation Details

#### 4.1 Database Connection
**File**: `web-app/backend/src/index.js`
- Add new route handler for `/api/stocks/:symbol/ml-analytics`
- Implement complex SQL queries joining multiple ML tables

#### 4.2 SQL Queries
```sql
-- Model Information
SELECT m.*, bi.symbol 
FROM ml_models m 
JOIN base_instruments bi ON m.instrument_id = bi.id 
WHERE bi.symbol = $1 AND m.status = 'active'
LIMIT 1;

-- Confusion Matrix Data
SELECT 
  predicted_class, 
  actual_class, 
  COUNT(*) as count 
FROM ml_predictions 
WHERE instrument_id = $1 AND actual_class IS NOT NULL
GROUP BY predicted_class, actual_class;

-- ROC Curve Points
SELECT 
  prediction_probability,
  actual_class
FROM ml_predictions 
WHERE instrument_id = $1 AND actual_class IS NOT NULL
ORDER BY prediction_probability DESC;
```

#### 4.3 Redis Caching Strategy
- **Cache Key**: `ml_analytics:{symbol}`
- **TTL**: 24 hours (ML models don't change frequently)
- **Invalidation**: Manual trigger when models are retrained

### Phase 5: UI/UX Enhancements

#### 5.1 Visual Design
- **Color Scheme**: Professional blues/oranges matching notebook
- **Typography**: Clear metric labels, prominent numbers for key scores
- **Responsive Design**: 2×2 grid on desktop, stacked on mobile
- **Dark Mode Support**: Compatible with existing theme system

#### 5.2 Interactive Features
- **Chart Tooltips**: Detailed information on hover
- **Metric Explanations**: Help text for ROC-AUC, Precision-Recall concepts
- **Export Options**: Download charts as PNG/PDF (future enhancement)

#### 5.3 Loading States
- **Skeleton Loading**: Chart placeholders while data loads
- **Error States**: Informative messages if no ML model exists
- **Empty States**: Guidance for stocks without ML predictions

### Phase 6: Testing & Quality Assurance

#### 6.1 Data Validation
- **API Testing**: Verify all 10 stocks return valid ML data
- **Edge Cases**: Handle stocks without ML models gracefully
- **Performance**: Ensure complex SQL queries are optimized

#### 6.2 Frontend Testing
- **Component Testing**: Individual chart components render correctly
- **Integration Testing**: Full workflow from tab click to chart display
- **Cross-Browser**: Chrome, Firefox, Safari compatibility

#### 6.3 User Experience Testing
- **Navigation**: Tab switching works smoothly
- **Performance**: Charts render quickly (<2s load time)
- **Mobile Responsiveness**: Charts are readable on mobile devices

## Implementation Timeline

### Week 1: Backend Development
- **Days 1-2**: Database queries and API endpoint development
- **Days 3-4**: Data processing and response formatting
- **Day 5**: Redis caching integration and testing

### Week 2: Frontend Development
- **Days 1-2**: Chart component development (confusion matrix, ROC curve)
- **Days 3-4**: Remaining charts and model overview cards
- **Day 5**: Integration with StockDetail component

### Week 3: Integration & Polish
- **Days 1-2**: Full integration testing and bug fixes
- **Days 3-4**: UI/UX polish and responsive design
- **Day 5**: Performance optimization and final testing

## Success Metrics

### Technical Metrics
- **API Response Time**: <500ms for ML analytics endpoint
- **Chart Render Time**: <1s for all charts to display
- **Data Accuracy**: 100% match between database and displayed metrics

### User Experience Metrics
- **Tab Navigation**: Smooth switching between all 5 tabs
- **Mobile Usability**: Charts readable on mobile devices
- **Error Handling**: Graceful degradation for stocks without ML models

### Business Value
- **Model Transparency**: Users can see how XGBoost models perform
- **Trading Insights**: Clear visualization of prediction accuracy
- **Technical Credibility**: Professional presentation of ML capabilities

## Technical Considerations

### Performance Optimization
- **SQL Optimization**: Use appropriate indexes on ML tables
- **Data Pagination**: Limit prediction history to recent N records
- **Caching Strategy**: 24-hour cache for model performance data

### Scalability
- **New Models**: Easy addition of new stocks' ML models
- **Model Versions**: Handle multiple model versions per stock
- **Feature Evolution**: Extensible design for new chart types

### Maintenance
- **Model Updates**: Automatic cache invalidation when models retrain
- **Database Schema**: Compatible with existing ML table structure
- **Code Organization**: Modular components for easy maintenance

## Risk Mitigation

### Data Availability Risks
- **Missing Models**: Graceful handling of stocks without ML models
- **Incomplete Predictions**: Show partial data with appropriate warnings
- **Model Failures**: Clear error messages for failed model loads

### Performance Risks
- **Large Datasets**: Implement data pagination and lazy loading
- **Complex Calculations**: Cache expensive computations
- **Browser Compatibility**: Polyfills for older browsers if needed

### User Experience Risks
- **Information Overload**: Clear hierarchy and progressive disclosure
- **Technical Complexity**: Tooltips and help text for ML concepts
- **Mobile Experience**: Responsive design with touch-friendly interactions

## Conclusion

This implementation plan provides a comprehensive roadmap for adding ML Analytics capabilities to our stock analysis platform. The new tab will showcase our XGBoost models' performance with professional visualizations inspired by Jupyter notebook analysis, providing users with transparent insights into our AI-driven trading predictions.

The phased approach ensures systematic development, thorough testing, and smooth integration with the existing codebase while maintaining high performance and user experience standards.