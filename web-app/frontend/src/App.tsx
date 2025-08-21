import React, { useState, useEffect, useMemo } from 'react';
import './App.css';
import { ThemeProvider } from './contexts/ThemeContext';
import StockDetail from './components/StockDetail';
import StockFilter from './components/StockFilter';
import StockComparison from './components/StockComparison';
import WatchlistButton from './components/WatchlistButton';
import ThemeToggle from './components/ThemeToggle';
import Card from './components/ui/Card';
import Button from './components/ui/Button';

// Define what our stock data looks like
interface Stock {
  symbol: string;
  name: string;
  currency: string;
  total_records: number;
  latest_date: string;
  latest_price: number;
}

function AppContent() {
  // State is React's way of remembering data that can change
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'symbol' | 'name' | 'price' | 'records'>('symbol');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // useEffect runs code when the component loads
  useEffect(() => {
    fetchStocks();
  }, []);

  // Function to get stocks from our backend
  const fetchStocks = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/stocks');
      const data = await response.json();
      setStocks(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch stocks');
      setLoading(false);
    }
  };

  // Filter and sort stocks based on search and sort criteria
  const filteredAndSortedStocks = useMemo(() => {
    let filtered = stocks.filter(stock =>
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'symbol':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'price':
          aValue = a.latest_price || 0;
          bValue = b.latest_price || 0;
          break;
        case 'records':
          aValue = a.total_records;
          bValue = b.total_records;
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [stocks, searchTerm, sortBy, sortOrder]);

  // Show loading message
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center transition-colors">
        <div className="text-xl dark:text-white">Loading stocks...</div>
      </div>
    );
  }

  // Show error message
  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center transition-colors">
        <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  // Main content - show the stocks
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow transition-colors">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              📊 Stock Analysis Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                onClick={() => setShowComparison(true)}
                className="flex items-center space-x-2"
              >
                <span>📈</span>
                <span>Compare Stocks</span>
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 px-4">
        {/* Summary cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Portfolio Overview
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="text-2xl">📈</div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Total Stocks
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {filteredAndSortedStocks.length} / {stocks.length}
                    </dd>
                  </dl>
                </div>
              </div>
            </Card>

            <Card className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="text-2xl">💹</div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Currency
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      PLN
                    </dd>
                  </dl>
                </div>
              </div>
            </Card>

            <Card className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="text-2xl">🗓️</div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Latest Data
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {stocks[0]?.latest_date || 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Search and Filter */}
        <StockFilter
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          sortBy={sortBy}
          onSortChange={setSortBy}
          sortOrder={sortOrder}
          onSortOrderChange={setSortOrder}
        />

        {/* Stocks list */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Stocks List {searchTerm && `(${filteredAndSortedStocks.length} results)`}
          </h2>
          
          {filteredAndSortedStocks.length === 0 ? (
            <Card className="p-8 text-center">
              <div className="text-gray-500 dark:text-gray-400">
                {searchTerm ? 'No stocks found matching your search.' : 'No stocks available.'}
              </div>
              {searchTerm && (
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => setSearchTerm('')}
                >
                  Clear search
                </Button>
              )}
            </Card>
          ) : (
            <Card className="overflow-hidden">
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredAndSortedStocks.map((stock) => (
                  <li key={stock.symbol}>
                    <div 
                      className="px-4 py-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                      onClick={() => setSelectedStock(stock.symbol)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                              <span className="text-sm font-medium text-white">
                                {stock.symbol.substring(0, 2)}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="flex text-sm">
                              <p className="font-medium text-indigo-600 dark:text-indigo-400 truncate">
                                {stock.symbol}
                              </p>
                              <p className="ml-1 text-gray-500 dark:text-gray-400">
                                ({stock.currency})
                              </p>
                            </div>
                            <div className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                              {stock.name}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="text-sm text-gray-900 dark:text-white">
                              Price: {stock.latest_price ? `${stock.latest_price} PLN` : 'N/A'}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {stock.total_records.toLocaleString()} records
                            </div>
                          </div>
                          <WatchlistButton stock={stock} />
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetail 
          symbol={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}

      {/* Stock Comparison Modal */}
      {showComparison && (
        <StockComparison 
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
}

// Main App component with Theme Provider
function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
