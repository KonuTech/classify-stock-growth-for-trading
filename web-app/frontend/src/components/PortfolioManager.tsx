import React, { useState, useRef } from 'react';
import { usePortfolio } from '../contexts/PortfolioContext';
import Button from './ui/Button';
import { ArrowDownTrayIcon, ArrowUpTrayIcon, TrashIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function PortfolioManager() {
  const { transactions, exportData, importData, clearAllTransactions } = usePortfolio();
  const [showImport, setShowImport] = useState(false);
  const [importText, setImportText] = useState('');
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExport = () => {
    const jsonData = exportData();
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    if (!importText.trim()) return;
    
    const success = importData(importText);
    setImportStatus(success ? 'success' : 'error');
    
    if (success) {
      setImportText('');
      setShowImport(false);
      setTimeout(() => setImportStatus('idle'), 3000);
    }
  };

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const success = importData(text);
      setImportStatus(success ? 'success' : 'error');
      setTimeout(() => setImportStatus('idle'), 3000);
    };
    reader.readAsText(file);
  };

  const handleClearAll = () => {
    clearAllTransactions();
    setShowConfirmClear(false);
  };

  if (transactions.length === 0) {
    return null; // Don't show if no transactions
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            💼 Portfolio Manager
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            ({transactions.length} transactions)
          </span>
        </div>
        
        {importStatus === 'success' && (
          <div className="text-xs text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">
            ✅ Imported successfully
          </div>
        )}
        
        {importStatus === 'error' && (
          <div className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded">
            ❌ Import failed
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleExport}
          className="flex items-center space-x-1 text-xs"
        >
          <ArrowDownTrayIcon className="h-3 w-3" />
          <span>Export</span>
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowImport(!showImport)}
          className="flex items-center space-x-1 text-xs"
        >
          <ArrowUpTrayIcon className="h-3 w-3" />
          <span>Import</span>
        </Button>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileImport}
          accept=".json"
          className="hidden"
        />
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center space-x-1 text-xs"
        >
          <ArrowUpTrayIcon className="h-3 w-3" />
          <span>Import File</span>
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowConfirmClear(true)}
          className="flex items-center space-x-1 text-xs text-red-600 dark:text-red-400 border-red-300 dark:border-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
        >
          <TrashIcon className="h-3 w-3" />
          <span>Clear All</span>
        </Button>
      </div>

      {/* Import Text Area */}
      {showImport && (
        <div className="mt-3 space-y-2">
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Paste JSON data from a previous export:
          </div>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder="Paste your exported portfolio JSON data here..."
            className="w-full h-32 px-3 py-2 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
          <div className="flex space-x-2">
            <Button
              size="sm"
              onClick={handleImport}
              disabled={!importText.trim()}
              className="text-xs"
            >
              Import Data
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setShowImport(false);
                setImportText('');
              }}
              className="text-xs"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Clear All Confirmation */}
      {showConfirmClear && (
        <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
          <div className="flex items-start space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="space-y-2">
              <div className="text-sm font-medium text-red-800 dark:text-red-300">
                Clear All Transactions?
              </div>
              <div className="text-xs text-red-700 dark:text-red-400">
                This will permanently delete all {transactions.length} transactions and cannot be undone. 
                Consider exporting your data first.
              </div>
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  onClick={handleClearAll}
                  className="text-xs bg-red-600 hover:bg-red-700 text-white"
                >
                  Yes, Clear All
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowConfirmClear(false)}
                  className="text-xs"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}