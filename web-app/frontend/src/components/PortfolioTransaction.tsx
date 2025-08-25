import React, { useState } from 'react';
import { usePortfolio } from '../contexts/PortfolioContext';
import Button from './ui/Button';
import { PlusIcon, MinusIcon, TrashIcon } from '@heroicons/react/24/outline';

interface PortfolioTransactionProps {
  symbol: string;
  currentPrice: number;
}

export default function PortfolioTransaction({ symbol, currentPrice }: PortfolioTransactionProps) {
  const { addTransaction, getPositionForSymbol, removeTransaction } = usePortfolio();
  const [showBuyForm, setShowBuyForm] = useState(false);
  const [showSellForm, setShowSellForm] = useState(false);
  const [showTransactions, setShowTransactions] = useState(false);
  
  const [buyDate, setBuyDate] = useState(new Date().toISOString().split('T')[0]);
  const [buyPrice, setBuyPrice] = useState(currentPrice.toString());
  const [buyQuantity, setBuyQuantity] = useState('');
  
  const [sellDate, setSellDate] = useState(new Date().toISOString().split('T')[0]);
  const [sellPrice, setSellPrice] = useState(currentPrice.toString());
  const [sellQuantity, setSellQuantity] = useState('');

  const position = getPositionForSymbol(symbol);
  const hasShares = position && position.totalShares > 0;

  const handleBuy = () => {
    if (buyDate && buyPrice && buyQuantity && parseFloat(buyQuantity) > 0) {
      addTransaction({
        symbol,
        type: 'buy',
        date: buyDate,
        price: parseFloat(buyPrice),
        quantity: parseFloat(buyQuantity)
      });
      setBuyQuantity('');
      setShowBuyForm(false);
    }
  };

  const handleSell = () => {
    if (sellDate && sellPrice && sellQuantity && parseFloat(sellQuantity) > 0) {
      addTransaction({
        symbol,
        type: 'sell',
        date: sellDate,
        price: parseFloat(sellPrice),
        quantity: parseFloat(sellQuantity)
      });
      setSellQuantity('');
      setShowSellForm(false);
    }
  };

  const calculateUnrealizedProfit = () => {
    if (!position || position.totalShares <= 0) return 0;
    const currentValue = position.totalShares * currentPrice;
    const costBasis = position.totalShares * position.averageBuyPrice;
    return currentValue - costBasis;
  };

  const calculateTotalProfit = () => {
    if (!position) return 0;
    return position.realizedProfit + calculateUnrealizedProfit();
  };

  const formatPrice = (price: number) => `${price.toFixed(2)} PLN`;
  const formatProfit = (profit: number) => {
    const sign = profit >= 0 ? '+' : '';
    return `${sign}${profit.toFixed(2)} PLN`;
  };

  return (
    <div className="space-y-2">
      {/* Portfolio Summary */}
      {position && (position.totalShares > 0 || position.realizedProfit !== 0 || position.transactions.length > 0) && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <div className="text-xs font-medium text-blue-800 dark:text-blue-300">
                📊 Portfolio Position
              </div>
              {position.totalShares > 0 ? (
                <>
                  <div className="text-xs text-blue-700 dark:text-blue-400">
                    {position.totalShares} shares @ avg {formatPrice(position.averageBuyPrice)}
                  </div>
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    Current value: {formatPrice(position.totalShares * currentPrice)}
                  </div>
                </>
              ) : (
                <div className="text-xs text-blue-700 dark:text-blue-400">
                  No current holdings
                </div>
              )}
              {position.realizedProfit !== 0 && (
                <div className="text-xs text-blue-600 dark:text-blue-400">
                  Realized P&L: {formatProfit(position.realizedProfit)}
                </div>
              )}
            </div>
            <div className="text-right space-y-1">
              <div className={`text-xs font-medium ${
                calculateTotalProfit() >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}>
                {formatProfit(calculateTotalProfit())}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Total Profit
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setShowBuyForm(!showBuyForm);
            setShowSellForm(false);
            setBuyPrice(currentPrice.toString());
          }}
          className="flex items-center space-x-1 text-xs"
        >
          <PlusIcon className="h-3 w-3" />
          <span>Buy</span>
        </Button>
        
        {hasShares && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setShowSellForm(!showSellForm);
              setShowBuyForm(false);
              setSellPrice(currentPrice.toString());
              setSellQuantity(position?.totalShares.toString() || '');
            }}
            className="flex items-center space-x-1 text-xs"
          >
            <MinusIcon className="h-3 w-3" />
            <span>Sell</span>
          </Button>
        )}
        
        {position && position.transactions.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowTransactions(!showTransactions)}
            className="text-xs"
          >
            {showTransactions ? 'Hide' : 'History'}
          </Button>
        )}
      </div>

      {/* Buy Form */}
      {showBuyForm && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-700 space-y-2">
          <div className="text-xs font-medium text-green-800 dark:text-green-300">Buy {symbol}</div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Date</label>
              <input
                type="date"
                value={buyDate}
                onChange={(e) => setBuyDate(e.target.value)}
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Price (PLN)</label>
              <input
                type="number"
                step="0.01"
                value={buyPrice}
                onChange={(e) => setBuyPrice(e.target.value)}
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Quantity</label>
              <input
                type="number"
                step="1"
                value={buyQuantity}
                onChange={(e) => setBuyQuantity(e.target.value)}
                placeholder="Shares"
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              size="sm"
              onClick={handleBuy}
              disabled={!buyDate || !buyPrice || !buyQuantity || parseFloat(buyQuantity) <= 0}
              className="text-xs"
            >
              Confirm Buy
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBuyForm(false)}
              className="text-xs"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Sell Form */}
      {showSellForm && (
        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-700 space-y-2">
          <div className="text-xs font-medium text-red-800 dark:text-red-300">
            Sell {symbol} (Available: {position?.totalShares || 0} shares)
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Date</label>
              <input
                type="date"
                value={sellDate}
                onChange={(e) => setSellDate(e.target.value)}
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Price (PLN)</label>
              <input
                type="number"
                step="0.01"
                value={sellPrice}
                onChange={(e) => setSellPrice(e.target.value)}
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Quantity</label>
              <input
                type="number"
                step="1"
                value={sellQuantity}
                onChange={(e) => setSellQuantity(e.target.value)}
                max={position?.totalShares || 0}
                placeholder="Shares"
                className="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              size="sm"
              onClick={handleSell}
              disabled={!sellDate || !sellPrice || !sellQuantity || parseFloat(sellQuantity) <= 0 || parseFloat(sellQuantity) > (position?.totalShares || 0)}
              className="text-xs"
            >
              Confirm Sell
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSellForm(false)}
              className="text-xs"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Transaction History */}
      {showTransactions && position && position.transactions.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <div className="text-xs font-medium text-gray-800 dark:text-gray-300 mb-2">Transaction History</div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {position.transactions.map((transaction) => (
              <div key={transaction.id} className="flex justify-between items-center text-xs">
                <div className="flex items-center space-x-2">
                  <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                    transaction.type === 'buy' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {transaction.type.toUpperCase()}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {new Date(transaction.date).toLocaleDateString('pl-PL')}
                  </span>
                  <span className="text-gray-900 dark:text-white">
                    {transaction.quantity} @ {formatPrice(transaction.price)}
                  </span>
                </div>
                <button
                  onClick={() => removeTransaction(transaction.id)}
                  className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                >
                  <TrashIcon className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}