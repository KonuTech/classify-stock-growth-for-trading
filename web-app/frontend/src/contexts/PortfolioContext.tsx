import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface Transaction {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  date: string;
  price: number;
  quantity: number;
  createdAt: string;
}

export interface PortfolioPosition {
  symbol: string;
  totalShares: number;
  averageBuyPrice: number;
  totalInvested: number;
  totalSold: number;
  realizedProfit: number;
  unrealizedProfit: number;
  totalProfit: number;
  transactions: Transaction[];
}

interface PortfolioContextType {
  transactions: Transaction[];
  positions: Record<string, PortfolioPosition>;
  addTransaction: (transaction: Omit<Transaction, 'id' | 'createdAt'>) => void;
  removeTransaction: (id: string) => void;
  getPositionForSymbol: (symbol: string) => PortfolioPosition | null;
  getTotalPortfolioValue: (currentPrices: Record<string, number>) => number;
  getTotalPortfolioProfit: (currentPrices: Record<string, number>) => number;
  clearAllTransactions: () => void;
  exportData: () => string;
  importData: (jsonData: string) => boolean;
}

const PortfolioContext = createContext<PortfolioContextType | undefined>(undefined);

const STORAGE_KEY = 'stock_portfolio_transactions';

export function PortfolioProvider({ children }: { children: ReactNode }) {
  // Initialize state with localStorage data immediately
  const [transactions, setTransactions] = useState<Transaction[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      console.log('Portfolio: Initializing from localStorage, found:', saved ? `${saved.length} characters` : 'nothing');
      
      if (saved) {
        const parsedTransactions = JSON.parse(saved);
        console.log('Portfolio: Successfully initialized with', parsedTransactions.length, 'transactions');
        return parsedTransactions;
      }
    } catch (error) {
      console.error('Portfolio: Failed to parse saved transactions during initialization:', error);
      localStorage.removeItem(STORAGE_KEY);
    }
    return [];
  });

  // Save transactions to localStorage whenever they change
  useEffect(() => {
    const jsonData = JSON.stringify(transactions);
    localStorage.setItem(STORAGE_KEY, jsonData);
    console.log('Portfolio: Saved', transactions.length, 'transactions to localStorage (', jsonData.length, 'characters)');
  }, [transactions]);

  // Calculate positions from transactions
  const positions: Record<string, PortfolioPosition> = React.useMemo(() => {
    const positionsMap: Record<string, PortfolioPosition> = {};

    transactions.forEach(transaction => {
      if (!positionsMap[transaction.symbol]) {
        positionsMap[transaction.symbol] = {
          symbol: transaction.symbol,
          totalShares: 0,
          averageBuyPrice: 0,
          totalInvested: 0,
          totalSold: 0,
          realizedProfit: 0,
          unrealizedProfit: 0,
          totalProfit: 0,
          transactions: []
        };
      }

      const position = positionsMap[transaction.symbol];
      position.transactions.push(transaction);

      if (transaction.type === 'buy') {
        const newTotalInvested = position.totalInvested + (transaction.price * transaction.quantity);
        const newTotalShares = position.totalShares + transaction.quantity;
        
        position.totalInvested = newTotalInvested;
        position.totalShares = newTotalShares;
        position.averageBuyPrice = newTotalShares > 0 ? newTotalInvested / newTotalShares : 0;
      } else if (transaction.type === 'sell') {
        const sellValue = transaction.price * transaction.quantity;
        const costBasis = position.averageBuyPrice * transaction.quantity;
        
        position.totalShares = Math.max(0, position.totalShares - transaction.quantity);
        position.totalSold += sellValue;
        position.realizedProfit += (sellValue - costBasis);
      }
    });

    return positionsMap;
  }, [transactions]);

  const addTransaction = (transactionData: Omit<Transaction, 'id' | 'createdAt'>) => {
    const newTransaction: Transaction = {
      ...transactionData,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString()
    };
    setTransactions(prev => [...prev, newTransaction]);
  };

  const removeTransaction = (id: string) => {
    setTransactions(prev => prev.filter(t => t.id !== id));
  };

  const getPositionForSymbol = (symbol: string): PortfolioPosition | null => {
    return positions[symbol] || null;
  };

  const getTotalPortfolioValue = (currentPrices: Record<string, number>): number => {
    return Object.values(positions).reduce((total, position) => {
      const currentPrice = currentPrices[position.symbol] || 0;
      const currentValue = position.totalShares * currentPrice;
      return total + currentValue;
    }, 0);
  };

  const getTotalPortfolioProfit = (currentPrices: Record<string, number>): number => {
    return Object.values(positions).reduce((total, position) => {
      const currentPrice = currentPrices[position.symbol] || 0;
      const currentValue = position.totalShares * currentPrice;
      const unrealizedProfit = currentValue - (position.totalShares * position.averageBuyPrice);
      const totalProfit = position.realizedProfit + unrealizedProfit;
      return total + totalProfit;
    }, 0);
  };

  const clearAllTransactions = () => {
    setTransactions([]);
  };

  const exportData = (): string => {
    const exportData = {
      transactions,
      exportDate: new Date().toISOString(),
      version: '1.0'
    };
    return JSON.stringify(exportData, null, 2);
  };

  const importData = (jsonData: string): boolean => {
    try {
      const parsedData = JSON.parse(jsonData);
      
      // Validate data structure
      if (!parsedData.transactions || !Array.isArray(parsedData.transactions)) {
        console.error('Invalid data structure: missing or invalid transactions array');
        return false;
      }

      // Validate each transaction
      const validTransactions = parsedData.transactions.filter((t: any) => {
        return t.id && t.symbol && t.type && t.date && 
               typeof t.price === 'number' && typeof t.quantity === 'number';
      });

      if (validTransactions.length !== parsedData.transactions.length) {
        console.warn(`${parsedData.transactions.length - validTransactions.length} invalid transactions were skipped`);
      }

      setTransactions(validTransactions);
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  };

  const contextValue: PortfolioContextType = {
    transactions,
    positions,
    addTransaction,
    removeTransaction,
    getPositionForSymbol,
    getTotalPortfolioValue,
    getTotalPortfolioProfit,
    clearAllTransactions,
    exportData,
    importData
  };

  return (
    <PortfolioContext.Provider value={contextValue}>
      {children}
    </PortfolioContext.Provider>
  );
}

export function usePortfolio() {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
}