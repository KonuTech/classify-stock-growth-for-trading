import React from 'react';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

interface StockFilterProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  sortBy: 'symbol' | 'name' | 'price' | 'records' | 'total_return' | 'max_drawdown' | 'price_range';
  onSortChange: (sort: 'symbol' | 'name' | 'price' | 'records' | 'total_return' | 'max_drawdown' | 'price_range') => void;
  sortOrder: 'asc' | 'desc';
  onSortOrderChange: (order: 'asc' | 'desc') => void;
}

export default function StockFilter({
  searchTerm,
  onSearchChange,
  sortBy,
  onSortChange,
  sortOrder,
  onSortOrderChange
}: StockFilterProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6 transition-colors">
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="Search stocks by symbol or name..."
          />
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">Sort by:</span>
          </div>
          
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value as any)}
            className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="symbol">Symbol</option>
            <option value="name">Name</option>
            <option value="price">Current Price</option>
            <option value="price_range">Price Range</option>
            <option value="total_return">Total Return</option>
            <option value="max_drawdown">Max Drawdown</option>
            <option value="records">Records</option>
          </select>

          <button
            onClick={() => onSortOrderChange(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>
    </div>
  );
}