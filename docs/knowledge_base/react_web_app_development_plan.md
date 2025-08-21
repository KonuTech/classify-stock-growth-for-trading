# React Web Application Development Plan
## Stock Analysis & ML Prediction Dashboard

**Generated**: 2025-08-21  
**Target Environment**: `prod_stock_data` schema  
**Deployment**: Dockerized React application for cloud deployment

---

## 📊 Data Analysis Summary

### Available Production Data
- **Stock Instruments**: 10 Polish stocks (BDX, CDR, DVL, ELT, GPW, KTY, PLW, PZU, RBW, XTB)
- **Historical Prices**: 48,203 records spanning 1994-2025 (30+ years)
- **ML Models**: 10 active XGBoost models (one per stock)
- **ML Predictions**: 9,559 predictions with fresh daily updates
- **Feature Data**: 47,753 records with technical indicators
- **Performance Metrics**: ROC-AUC averaging 0.5161 across models

### Key Data Insights
- **Extensive History**: Stocks have 2,208 to 7,717 trading days each
- **Recent Predictions**: Fresh predictions for 2025-08-21 available
- **Technical Indicators**: RSI-14, moving averages (SMA-20, SMA-50) populated
- **Model Details**: XGBoost hyperparameters stored as JSON
- **Currency**: All stocks in PLN (Polish Złoty)

---

## 🎯 Application Architecture

### Technology Stack
- **Frontend**: React 18+ with TypeScript
- **Styling**: Tailwind CSS + Headless UI components
- **Charts**: Recharts or Chart.js for financial visualizations
- **State Management**: React Query (TanStack Query) + Zustand
- **Backend API**: Node.js + Express + PostgreSQL
- **Database**: Direct connection to `prod_stock_data` schema
- **Containerization**: Docker + Docker Compose
- **Dark Mode**: Tailwind CSS dark mode implementation

### Project Structure
```
stock-dashboard/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Main application pages
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client services
│   │   ├── types/           # TypeScript type definitions
│   │   ├── utils/           # Helper functions
│   │   └── styles/          # Tailwind CSS configurations
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── backend/                  # Node.js API server
│   ├── src/
│   │   ├── routes/          # API route handlers
│   │   ├── controllers/     # Business logic
│   │   ├── models/          # Database models/queries
│   │   ├── middleware/      # Express middleware
│   │   └── config/          # Database configuration
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Multi-service orchestration
└── README.md
```

---

## 📱 Application Features & Pages

### 1. Dashboard Overview Page
**Route**: `/`
**Purpose**: High-level portfolio overview

**Components**:
- **Market Summary Cards**: Total instruments, latest prediction date, overall model performance
- **Quick Stats**: Best performing predictions, recent accuracy rates
- **Alert Panel**: Upcoming prediction target dates, model status alerts
- **Recent Activity**: Latest predictions and price movements

**Data Sources**:
```sql
-- Market overview stats
SELECT COUNT(*) as total_stocks, 
       MAX(trading_date_local) as latest_data_date,
       AVG(test_roc_auc) as avg_model_performance
FROM base_instruments bi
JOIN ml_models mm ON bi.id = mm.instrument_id
LEFT JOIN stock_prices sp ON bi.id = sp.stock_id;
```

### 2. Stock Detail Page
**Route**: `/stock/:symbol`
**Purpose**: Comprehensive individual stock analysis

**Sections**:
- **Stock Header**: Symbol, name, current price, daily change
- **Price Chart**: Interactive candlestick/line chart with volume
- **Technical Indicators**: RSI, moving averages overlay
- **ML Predictions Timeline**: Historical predictions vs actual outcomes
- **Model Performance**: Accuracy, ROC-AUC, prediction confidence

**Visualizations**:
- **Price History Chart**: Candlestick chart with 1Y, 2Y, 5Y, All time periods
- **Technical Indicators**: RSI-14, SMA-20, SMA-50 overlays
- **Prediction Accuracy**: Success rate over time with confidence bands
- **Volume Analysis**: Trading volume correlation with price movements

**Data Sources**:
```sql
-- Stock price history with technical indicators
SELECT sp.trading_date_local, sp.open_price, sp.high_price, 
       sp.low_price, sp.close_price, sp.volume,
       mfd.rsi_14, mfd.sma_20, mfd.sma_50
FROM stock_prices sp
LEFT JOIN ml_feature_data mfd ON sp.stock_id = mfd.instrument_id 
    AND sp.trading_date_local = mfd.trading_date
WHERE sp.stock_id = (SELECT id FROM base_instruments WHERE symbol = $1)
ORDER BY sp.trading_date_local DESC;
```

### 3. ML Model Analysis Page
**Route**: `/models`
**Purpose**: Model performance and configuration analysis

**Sections**:
- **Model Performance Matrix**: ROC-AUC, accuracy, F1-score comparison across stocks
- **Hyperparameters Comparison**: XGBoost configuration heatmap
- **Training Metrics**: Training duration, data size, feature importance
- **Model Status**: Active/deprecated models, last training date

**Visualizations**:
- **Performance Comparison**: Multi-axis radar chart of model metrics
- **Hyperparameter Heatmap**: Visual comparison of XGBoost settings
- **Feature Importance**: Top 20 features across all models
- **Training Timeline**: Model deployment and performance over time

**Data Sources**:
```sql
-- Model performance comparison
SELECT bi.symbol, mm.model_version, mm.test_roc_auc, mm.test_accuracy,
       mm.hyperparameters, mm.feature_importance, mm.trained_at
FROM ml_models mm
JOIN base_instruments bi ON mm.instrument_id = bi.id
WHERE mm.status = 'active'
ORDER BY mm.test_roc_auc DESC;
```

### 4. Predictions Dashboard Page
**Route**: `/predictions`
**Purpose**: Current and historical ML predictions

**Sections**:
- **Current Predictions**: Today's predictions for all stocks
- **Prediction Calendar**: Historical predictions with actual outcomes
- **Accuracy Tracking**: Win rates, prediction confidence analysis
- **Trading Signals**: Buy/Hold/Sell recommendations based on probability

**Components**:
- **Prediction Cards**: Current predictions with confidence indicators
- **Accuracy Timeline**: Historical accuracy trends per stock
- **Signal Strength**: Visual representation of prediction probabilities
- **Outcome Analysis**: Predicted vs actual price movements

**Data Sources**:
```sql
-- Recent predictions with outcomes
SELECT bi.symbol, mp.prediction_date, mp.target_date,
       mp.predicted_class, mp.prediction_probability, 
       mp.actual_class, mp.trading_signal, mp.signal_strength
FROM ml_predictions mp
JOIN base_instruments bi ON mp.instrument_id = bi.id
WHERE mp.prediction_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY mp.prediction_date DESC, bi.symbol;
```

### 5. Portfolio Performance Page
**Route**: `/performance`
**Purpose**: Backtesting results and trading strategy analysis

**Sections**:
- **Strategy Performance**: Returns, Sharpe ratio, win rates
- **Risk Analysis**: Maximum drawdown, volatility metrics
- **Trade History**: Individual trade details and outcomes
- **Benchmark Comparison**: Strategy vs buy-and-hold performance

**Note**: *Current backtesting data shows zero returns - may need investigation or represent no-trade strategies*

---

## 🎨 UI/UX Design System

### Color Palette
**Light Mode**:
- Primary: `#1e40af` (blue-800)
- Secondary: `#059669` (green-600) 
- Success: `#10b981` (green-500)
- Warning: `#f59e0b` (yellow-500)
- Error: `#ef4444` (red-500)
- Background: `#f8fafc` (slate-50)

**Dark Mode**:
- Primary: `#3b82f6` (blue-500)
- Secondary: `#10b981` (green-500)
- Success: `#34d399` (green-400)
- Warning: `#fbbf24` (yellow-400)
- Error: `#f87171` (red-400)
- Background: `#0f172a` (slate-900)

### Typography
- **Headers**: Inter font family
- **Body**: System font stack
- **Monospace**: JetBrains Mono for numbers/codes

### Component Library
- **Cards**: Glassmorphism effect with subtle shadows
- **Charts**: Consistent color scheme with hover interactions
- **Tables**: Sortable columns, sticky headers, pagination
- **Forms**: Floating labels, validation states
- **Buttons**: Primary, secondary, ghost variants
- **Modals**: Overlay with backdrop blur effect

---

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
**Objectives**: Set up basic application structure and data connectivity

**Tasks**:
1. **Backend API Setup**
   - Express server with TypeScript
   - PostgreSQL connection to `prod_stock_data`
   - REST API endpoints for core data
   - Docker configuration

2. **Frontend Foundation**
   - React + TypeScript + Tailwind CSS setup
   - Routing with React Router
   - Dark mode implementation
   - Basic layout components

3. **Data Layer**
   - API client setup with React Query
   - TypeScript interfaces for database entities
   - Error handling and loading states

**Deliverables**:
- Dockerized application stack
- Basic API endpoints (`/api/stocks`, `/api/models`)
- React application with navigation
- Dark/light mode toggle

### Phase 2: Dashboard & Stock Details (Week 3-4)
**Objectives**: Implement main dashboard and detailed stock views

**Tasks**:
1. **Dashboard Page**
   - Market overview cards
   - Quick statistics
   - Recent activity feed
   - Responsive grid layout

2. **Stock Detail Page**
   - Price chart with Recharts
   - Technical indicators visualization
   - Stock information panel
   - Historical data table

3. **Chart Implementations**
   - Candlestick price charts
   - Volume charts
   - Technical indicator overlays
   - Interactive time range selection

**Deliverables**:
- Complete dashboard with real data
- Interactive stock detail pages
- Financial chart visualizations
- Mobile-responsive design

### Phase 3: ML Features & Predictions (Week 5-6)
**Objectives**: Implement ML model analysis and prediction features

**Tasks**:
1. **Models Page**
   - Model performance comparison
   - Hyperparameter visualization
   - Feature importance charts
   - Training metrics display

2. **Predictions Dashboard**
   - Current predictions display
   - Historical prediction accuracy
   - Trading signal indicators
   - Prediction calendar view

3. **Advanced Analytics**
   - Accuracy trend analysis
   - Confidence score distributions
   - Model comparison tools
   - Prediction outcome tracking

**Deliverables**:
- ML model analysis interface
- Prediction dashboard with historical data
- Advanced analytics visualizations
- Trading signal recommendations

### Phase 4: Performance & Polish (Week 7-8)
**Objectives**: Optimize performance and add final features

**Tasks**:
1. **Performance Optimization**
   - API response caching
   - Chart rendering optimization
   - Lazy loading for large datasets
   - Database query optimization

2. **Advanced Features**
   - Real-time data updates
   - Export functionality (CSV, PDF)
   - Advanced filtering and search
   - User preferences persistence

3. **Final Polish**
   - Accessibility improvements
   - Error boundary implementation
   - Loading skeleton screens
   - Animation and micro-interactions

**Deliverables**:
- Production-ready application
- Export and sharing features
- Comprehensive error handling
- Performance-optimized charts

---

## 🐳 Docker Configuration

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["node", "dist/index.js"]
```

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:3001
  
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - DB_HOST=host.docker.internal
      - DB_PORT=5432
      - DB_NAME=stock_data
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_SCHEMA=prod_stock_data
    depends_on:
      - postgres

  postgres:
    image: postgres:17
    # Use existing database from main project
    network_mode: "host"
```

---

## 📡 API Endpoints Design

### Core Data Endpoints
```typescript
// Stock data
GET /api/stocks                          // List all stocks
GET /api/stocks/:symbol                  // Stock details
GET /api/stocks/:symbol/prices          // Price history
GET /api/stocks/:symbol/indicators      // Technical indicators

// ML Models
GET /api/models                         // All models summary
GET /api/models/:symbol                 // Specific model details
GET /api/models/performance             // Model performance comparison

// Predictions
GET /api/predictions                    // Recent predictions
GET /api/predictions/:symbol            // Symbol-specific predictions
GET /api/predictions/accuracy          // Accuracy metrics

// Analytics
GET /api/analytics/market              // Market overview stats
GET /api/analytics/performance         // Portfolio performance
```

### Response Formats
```typescript
interface StockPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface MLModel {
  symbol: string;
  version: string;
  performance: {
    rocAuc: number;
    accuracy: number;
    f1Score: number;
  };
  hyperparameters: Record<string, any>;
  trainedAt: string;
}

interface Prediction {
  symbol: string;
  predictionDate: string;
  targetDate: string;
  predictedClass: boolean;
  probability: number;
  confidence: number;
  tradingSignal: 'BUY' | 'HOLD' | 'SELL';
}
```

---

## 🔧 Development Setup Commands

### Initial Setup
```bash
# Automated web application initialization
make web-init

# Manual setup (if needed)
mkdir web-app && cd web-app
mkdir frontend backend

# All dependencies are automatically installed by 'make web-init':
# - React + TypeScript + Tailwind CSS
# - Node.js + Express + PostgreSQL client
# - Docker configuration with prod_stock_data connection
```

### Development Commands
```bash
# Initialize web application structure (automated)
make web-init

# Start development servers (frontend + backend + database)
make web-dev

# Build production version
make web-build

# Start production containers
make web-start

# View application status and URLs
make web-status

# View logs
make web-logs

# Stop application
make web-stop

# Restart with latest changes
make web-restart

# Run tests
make web-test

# Clean up containers and images
make web-clean
```

---

## 📊 Data Validation & Issues

### Current Data Status
**✅ Available Data**:
- Complete price history (1994-2025)
- Active ML models with performance metrics
- Fresh daily predictions
- Technical indicators (RSI, moving averages)
- Hyperparameter configurations

**⚠️ Potential Issues**:
- Some technical indicators (MACD, Bollinger Bands) have null values
- Backtesting results show zero returns (may indicate no-trade strategy)
- Training record counts are zero (possible logging issue)

### Recommended Data Fixes
```sql
-- Check missing technical indicators
SELECT symbol, COUNT(*) as total_records,
       COUNT(macd_line) as macd_count,
       COUNT(bollinger_upper) as bollinger_count
FROM ml_feature_data mfd
JOIN base_instruments bi ON mfd.instrument_id = bi.id
GROUP BY symbol;

-- Update backtesting query (if needed)
SELECT * FROM ml_backtest_results 
WHERE total_trades > 0 AND total_return != 0;
```

---

## 🎯 Success Metrics

### Technical Metrics
- **Page Load Time**: < 2 seconds for dashboard
- **Chart Rendering**: < 500ms for 1000+ data points  
- **API Response**: < 200ms for standard queries
- **Mobile Performance**: 90+ Lighthouse score

### User Experience Metrics
- **Data Freshness**: Real-time updates for predictions
- **Visual Clarity**: Clear distinction between predictions and actual outcomes
- **Accessibility**: WCAG 2.1 AA compliance
- **Cross-browser**: Chrome, Firefox, Safari, Edge support

### Business Metrics
- **Data Coverage**: 100% of available stocks displayed
- **Prediction Accuracy**: Real-time accuracy tracking
- **Model Performance**: Visual comparison across all models
- **Historical Analysis**: Full 30-year price history visualization

---

## 🚀 Quick Start Guide

### Get Started in 3 Commands
```bash
# 1. Initialize web application structure
make web-init

# 2. Start development servers
make web-dev

# 3. Check status
make web-status
```

### Production Deployment
```bash
# Build and start production containers
make web-build
make web-start

# Monitor and manage
make web-logs
make web-status
```

## 📝 Next Steps

1. **Review and approve development plan**
2. **Run `make web-init` to set up development environment**
3. **Implement Phase 1: Core infrastructure**
4. **Validate API connectivity with prod_stock_data**
5. **Begin frontend development with dashboard mockups**
6. **Iterative development with weekly reviews**

## 📋 Makefile Command Reference

| Command | Description | Use Case |
|---------|-------------|----------|
| `make web-init` | Initialize React app structure | First-time setup |
| `make web-dev` | Start development servers | Local development |
| `make web-build` | Build production version | Prepare for deployment |
| `make web-start` | Start production containers | Production deployment |
| `make web-stop` | Stop all web containers | Shutdown |
| `make web-restart` | Restart with latest changes | Apply updates |
| `make web-logs` | View application logs | Debugging |
| `make web-status` | Show status and URLs | Check health |
| `make web-test` | Run all tests | Quality assurance |
| `make web-clean` | Clean containers/images | Maintenance |

---

**Note**: This plan assumes the existing PostgreSQL database remains accessible and the `prod_stock_data` schema contains the analyzed data structure. Any schema changes should be coordinated with the web application development.