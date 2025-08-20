"""
Backtesting framework for Random Forest trading strategy.
Simulates trading based on model predictions and evaluates performance.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up logging using centralized configuration
from .logging_config import get_ml_logger
logger = get_ml_logger(__name__)


class TradingBacktester:
    """Backtest trading strategies based on Random Forest predictions"""
    
    def __init__(self, initial_capital: float = 100000.0, 
                 transaction_cost: float = 0.001,
                 position_size: float = 0.1):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            transaction_cost: Transaction cost as percentage (0.001 = 0.1%)
            position_size: Position size as fraction of capital (0.1 = 10%)
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.position_size = position_size
        self.backtest_results = {}
        
    def backtest_single_stock(self, test_df: pd.DataFrame, 
                            predictions: np.ndarray, 
                            probabilities: np.ndarray,
                            symbol: str = "",
                            prediction_threshold: float = 0.5,
                            probability_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Backtest trading strategy for a single stock
        
        Args:
            test_df: Test DataFrame with price data
            predictions: Model predictions (0/1)
            probabilities: Model probabilities [0,1]
            symbol: Stock symbol
            prediction_threshold: Threshold for binary predictions (not used if using probabilities)
            probability_threshold: Threshold for probability-based trading
            
        Returns:
            Backtesting results dictionary
        """
        logger.info(f"{symbol}: Starting backtest with {len(test_df)} periods...")
        
        # Ensure we have the same number of rows
        min_len = min(len(test_df), len(predictions), len(probabilities))
        test_df = test_df.iloc[-min_len:].copy().reset_index(drop=True)
        predictions = predictions[-min_len:]
        probabilities = probabilities[-min_len:]
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0  # 0 = no position, 1 = long position
        entry_price = 0
        trades = []
        portfolio_values = [capital]
        cash_values = [capital]
        
        # Get actual future returns
        if 'growth_future_30d' in test_df.columns:
            actual_returns = test_df['growth_future_30d'].values - 1
        else:
            # Calculate 30-day forward returns if not available
            prices = test_df['close_price'].values
            actual_returns = np.full(len(prices), np.nan)
            for i in range(len(prices) - 30):
                if i + 30 < len(prices):
                    actual_returns[i] = (prices[i + 30] / prices[i]) - 1
        
        dates = test_df['trading_date_local'].values
        prices = test_df['close_price'].values
        
        # Trading simulation
        for i in range(len(test_df) - 30):  # Leave buffer for 30-day returns
            current_date = dates[i]
            current_price = prices[i]
            model_probability = probabilities[i]
            actual_return = actual_returns[i]
            
            # Trading decision based on probability threshold
            should_buy = model_probability > probability_threshold
            
            # Execute trading logic
            if should_buy and position == 0:
                # Enter long position
                shares_to_buy = int((capital * self.position_size) / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price * (1 + self.transaction_cost)
                    if cost <= capital:
                        capital -= cost
                        position = shares_to_buy
                        entry_price = current_price
                        
                        trades.append({
                            'date': current_date,
                            'action': 'BUY',
                            'price': current_price,
                            'shares': shares_to_buy,
                            'cost': cost,
                            'capital_after': capital,
                            'model_probability': model_probability,
                            'actual_return': actual_return
                        })
                        
            elif not should_buy and position > 0:
                # Exit long position
                proceeds = position * current_price * (1 - self.transaction_cost)
                capital += proceeds
                
                # Calculate trade return
                trade_return = (current_price - entry_price) / entry_price
                
                trades.append({
                    'date': current_date,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'proceeds': proceeds,
                    'capital_after': capital,
                    'trade_return': trade_return,
                    'model_probability': model_probability,
                    'actual_return': actual_return
                })
                
                position = 0
                entry_price = 0
                
            # Calculate current portfolio value
            if position > 0:
                portfolio_value = capital + (position * current_price)
            else:
                portfolio_value = capital
                
            portfolio_values.append(portfolio_value)
            cash_values.append(capital)
            
        # Close final position if open
        if position > 0:
            final_price = prices[-31]  # Use price 30 days before end
            proceeds = position * final_price * (1 - self.transaction_cost)
            capital += proceeds
            trade_return = (final_price - entry_price) / entry_price
            
            trades.append({
                'date': dates[-31],
                'action': 'SELL',
                'price': final_price,
                'shares': position,
                'proceeds': proceeds,
                'capital_after': capital,
                'trade_return': trade_return,
                'model_probability': probabilities[-31],
                'actual_return': actual_returns[-31] if not np.isnan(actual_returns[-31]) else 0
            })
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics(
            trades, portfolio_values, test_df, symbol, probabilities, 
            actual_returns, probability_threshold
        )
        
        # Store results
        self.backtest_results[symbol] = results
        
        logger.info(f"{symbol}: Backtest completed - Total return: {results['total_return']:.2%}, Sharpe ratio: {results['sharpe_ratio']:.3f}")
        
        return results
        
    def _calculate_performance_metrics(self, trades: List[Dict], 
                                     portfolio_values: List[float],
                                     test_df: pd.DataFrame,
                                     symbol: str,
                                     probabilities: np.ndarray,
                                     actual_returns: np.ndarray,
                                     probability_threshold: float) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        if not trades:
            logger.warning(f"{symbol}: No trades executed during backtest period")
            return {
                'symbol': symbol,
                'total_return': 0.0,
                'annualized_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0.0,
                'avg_return_per_trade': 0.0,
                'volatility': 0.0,
                'trades': trades,
                'portfolio_values': portfolio_values,
                'error': 'No trades executed'
            }
        
        # Convert trades to DataFrame for analysis
        trades_df = pd.DataFrame(trades)
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        # Calculate returns
        final_value = portfolio_values[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate portfolio daily returns
        portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
        portfolio_returns = portfolio_returns[portfolio_returns != 0]  # Remove zero returns
        
        # Time period calculation
        start_date = pd.to_datetime(test_df['trading_date_local'].iloc[0])
        end_date = pd.to_datetime(test_df['trading_date_local'].iloc[-1])
        years = (end_date - start_date).days / 365.25
        
        # Annualized return
        if years > 0:
            annualized_return = (1 + total_return) ** (1/years) - 1
        else:
            annualized_return = 0
            
        # Volatility (annualized)
        if len(portfolio_returns) > 1:
            volatility = np.std(portfolio_returns) * np.sqrt(252)
        else:
            volatility = 0
            
        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Max drawdown
        running_max = np.maximum.accumulate(portfolio_values)
        drawdowns = (np.array(portfolio_values) - running_max) / running_max
        max_drawdown = abs(min(drawdowns))
        
        # Trade statistics
        completed_trades = sell_trades[sell_trades['trade_return'].notna()]
        if len(completed_trades) > 0:
            trade_returns = completed_trades['trade_return'].values
            winning_trades = len(trade_returns[trade_returns > 0])
            win_rate = winning_trades / len(trade_returns)
            avg_return_per_trade = np.mean(trade_returns)
        else:
            winning_trades = 0
            win_rate = 0
            avg_return_per_trade = 0
            
        # Model performance analysis
        signal_accuracy = self._calculate_signal_accuracy(
            probabilities, actual_returns, probability_threshold
        )
        
        # Buy and hold comparison
        if 'close_price' in test_df.columns:
            buy_hold_return = (test_df['close_price'].iloc[-31] / test_df['close_price'].iloc[0]) - 1
        else:
            buy_hold_return = 0
            
        return {
            'symbol': symbol,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'total_trades': len(completed_trades),
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_return_per_trade': avg_return_per_trade,
            'buy_hold_return': buy_hold_return,
            'excess_return': total_return - buy_hold_return,
            'signal_accuracy': signal_accuracy,
            'trades': trades,
            'portfolio_values': portfolio_values,
            'probability_threshold': probability_threshold,
            'final_capital': final_value,
            'years': years
        }
        
    def _calculate_signal_accuracy(self, probabilities: np.ndarray, 
                                 actual_returns: np.ndarray, 
                                 threshold: float) -> Dict[str, float]:
        """Calculate signal accuracy metrics"""
        
        # Remove NaN values
        valid_mask = ~np.isnan(actual_returns)
        valid_probs = probabilities[valid_mask]
        valid_returns = actual_returns[valid_mask]
        
        if len(valid_returns) == 0:
            return {'precision': 0, 'recall': 0, 'accuracy': 0}
            
        # Model signals
        predicted_positive = valid_probs > threshold
        actual_positive = valid_returns > 0
        
        # Calculate metrics
        tp = np.sum(predicted_positive & actual_positive)
        fp = np.sum(predicted_positive & ~actual_positive)
        fn = np.sum(~predicted_positive & actual_positive)
        tn = np.sum(~predicted_positive & ~actual_positive)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        accuracy = (tp + tn) / len(valid_returns)
        
        return {
            'precision': precision,
            'recall': recall,
            'accuracy': accuracy
        }
        
    def backtest_multiple_stocks(self, test_results: Dict[str, Dict[str, Any]],
                                test_data: Dict[str, pd.DataFrame],
                                probability_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Backtest multiple stocks
        
        Args:
            test_results: Dictionary of test results from model training
            test_data: Dictionary of test DataFrames
            probability_threshold: Probability threshold for trading signals
            
        Returns:
            Combined backtest results
        """
        logger.info(f"Starting backtest for {len(test_results)} stocks...")
        
        individual_results = {}
        
        for symbol in test_results.keys():
            if symbol not in test_data:
                logger.warning(f"No test data found for {symbol}")
                continue
                
            try:
                # Get model predictions and test data
                model_results = test_results[symbol]['test_results']
                predictions = model_results['test_predictions']
                probabilities = model_results['test_probabilities']
                test_df = test_data[symbol]
                
                # Run backtest
                backtest_result = self.backtest_single_stock(
                    test_df=test_df,
                    predictions=predictions,
                    probabilities=probabilities,
                    symbol=symbol,
                    probability_threshold=probability_threshold
                )
                
                individual_results[symbol] = backtest_result
                
            except Exception as e:
                logger.error(f"Failed to backtest {symbol}: {e}")
                continue
                
        # Generate portfolio summary
        portfolio_summary = self._generate_portfolio_summary(individual_results)
        
        return {
            'individual_results': individual_results,
            'portfolio_summary': portfolio_summary,
            'probability_threshold': probability_threshold
        }
        
    def _generate_portfolio_summary(self, individual_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate portfolio-level summary statistics"""
        
        if not individual_results:
            return {}
            
        # Aggregate metrics
        total_returns = [r['total_return'] for r in individual_results.values() if 'error' not in r]
        annualized_returns = [r['annualized_return'] for r in individual_results.values() if 'error' not in r]
        sharpe_ratios = [r['sharpe_ratio'] for r in individual_results.values() if 'error' not in r and r['sharpe_ratio'] != 0]
        win_rates = [r['win_rate'] for r in individual_results.values() if 'error' not in r]
        total_trades = [r['total_trades'] for r in individual_results.values() if 'error' not in r]
        
        if not total_returns:
            return {'error': 'No valid backtest results'}
            
        # Portfolio statistics
        portfolio_summary = {
            'num_stocks': len(total_returns),
            'avg_total_return': np.mean(total_returns),
            'median_total_return': np.median(total_returns),
            'best_return': max(total_returns),
            'worst_return': min(total_returns),
            'avg_annualized_return': np.mean(annualized_returns),
            'avg_sharpe_ratio': np.mean(sharpe_ratios) if sharpe_ratios else 0,
            'avg_win_rate': np.mean(win_rates),
            'total_trades_all_stocks': sum(total_trades),
            'positive_return_stocks': len([r for r in total_returns if r > 0]),
            'profitable_stock_rate': len([r for r in total_returns if r > 0]) / len(total_returns)
        }
        
        # Equal-weight portfolio return
        equal_weight_return = np.mean(total_returns)
        portfolio_summary['equal_weight_portfolio_return'] = equal_weight_return
        
        return portfolio_summary
        
    def generate_backtest_report(self, symbol: str = None, save_path: Optional[str] = None) -> str:
        """Generate comprehensive backtest report"""
        
        if symbol and symbol in self.backtest_results:
            # Single stock report
            result = self.backtest_results[symbol]
            report = self._generate_single_stock_report(result)
        else:
            # Multi-stock summary report
            report = self._generate_multi_stock_report()
            
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {save_path}")
            
        return report
        
    def _generate_single_stock_report(self, result: Dict[str, Any]) -> str:
        """Generate single stock backtest report"""
        
        lines = [
            f"BACKTEST REPORT - {result['symbol']}",
            "=" * 50,
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "STRATEGY PERFORMANCE:",
            f"  Total Return: {result['total_return']:.2%}",
            f"  Annualized Return: {result['annualized_return']:.2%}",
            f"  Sharpe Ratio: {result['sharpe_ratio']:.3f}",
            f"  Max Drawdown: {result['max_drawdown']:.2%}",
            f"  Volatility: {result['volatility']:.2%}",
            "",
            "TRADING STATISTICS:",
            f"  Total Trades: {result['total_trades']}",
            f"  Winning Trades: {result['winning_trades']}",
            f"  Win Rate: {result['win_rate']:.2%}",
            f"  Avg Return per Trade: {result['avg_return_per_trade']:.2%}",
            "",
            "BENCHMARK COMPARISON:",
            f"  Buy & Hold Return: {result['buy_hold_return']:.2%}",
            f"  Excess Return: {result['excess_return']:.2%}",
            "",
            "MODEL PERFORMANCE:",
            f"  Signal Accuracy: {result['signal_accuracy']['accuracy']:.2%}",
            f"  Signal Precision: {result['signal_accuracy']['precision']:.2%}",
            f"  Signal Recall: {result['signal_accuracy']['recall']:.2%}",
            f"  Probability Threshold: {result['probability_threshold']:.1%}",
            ""
        ]
        
        return "\n".join(lines)
        
    def _generate_multi_stock_report(self) -> str:
        """Generate multi-stock portfolio report"""
        
        if not self.backtest_results:
            return "No backtest results available"
            
        # Calculate portfolio metrics
        portfolio_summary = self._generate_portfolio_summary(self.backtest_results)
        
        lines = [
            "MULTI-STOCK PORTFOLIO BACKTEST REPORT",
            "=" * 50,
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "PORTFOLIO SUMMARY:",
            f"  Number of Stocks: {portfolio_summary['num_stocks']}",
            f"  Equal-Weight Portfolio Return: {portfolio_summary['equal_weight_portfolio_return']:.2%}",
            f"  Average Return per Stock: {portfolio_summary['avg_total_return']:.2%}",
            f"  Median Return per Stock: {portfolio_summary['median_total_return']:.2%}",
            f"  Best Stock Return: {portfolio_summary['best_return']:.2%}",
            f"  Worst Stock Return: {portfolio_summary['worst_return']:.2%}",
            f"  Profitable Stock Rate: {portfolio_summary['profitable_stock_rate']:.2%}",
            "",
            "AVERAGE METRICS:",
            f"  Avg Annualized Return: {portfolio_summary['avg_annualized_return']:.2%}",
            f"  Avg Sharpe Ratio: {portfolio_summary['avg_sharpe_ratio']:.3f}",
            f"  Avg Win Rate: {portfolio_summary['avg_win_rate']:.2%}",
            f"  Total Trades (All Stocks): {portfolio_summary['total_trades_all_stocks']}",
            "",
            "INDIVIDUAL STOCK RESULTS:",
            "-" * 30
        ]
        
        # Add individual stock results
        sorted_results = sorted(self.backtest_results.items(), 
                              key=lambda x: x[1]['total_return'] if 'error' not in x[1] else -999, 
                              reverse=True)
        
        for symbol, result in sorted_results:
            if 'error' in result:
                lines.append(f"  {symbol}: ERROR - {result['error']}")
            else:
                lines.append(f"  {symbol}: {result['total_return']:+.2%} return, "
                           f"{result['total_trades']} trades, "
                           f"{result['win_rate']:.1%} win rate")
                
        return "\n".join(lines)
        
    def plot_performance(self, symbol: str, save_path: Optional[str] = None):
        """Plot backtest performance for a single stock"""
        
        if symbol not in self.backtest_results:
            raise ValueError(f"No backtest results found for {symbol}")
            
        result = self.backtest_results[symbol]
        
        if 'error' in result:
            logger.error(f"Cannot plot performance for {symbol}: {result['error']}")
            return
            
        # Create performance plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Portfolio value over time
        portfolio_values = result['portfolio_values']
        ax1.plot(portfolio_values, label='Strategy Portfolio Value', linewidth=2)
        ax1.axhline(y=self.initial_capital, color='red', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title(f'{symbol} - Portfolio Value Over Time')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown plot
        running_max = np.maximum.accumulate(portfolio_values)
        drawdowns = (np.array(portfolio_values) - running_max) / running_max * 100
        ax2.fill_between(range(len(drawdowns)), drawdowns, 0, alpha=0.7, color='red')
        ax2.set_title(f'{symbol} - Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Time Period')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance plot saved to {save_path}")
            
        plt.show()


if __name__ == "__main__":
    # Test backtesting with sample data
    logger.info("Testing backtesting framework...")
    
    # Create sample test data and predictions
    np.random.seed(42)
    n_samples = 100
    
    # Sample data
    dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
    prices = 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, n_samples))
    
    test_df = pd.DataFrame({
        'trading_date_local': dates,
        'close_price': prices,
        'volume': np.random.randint(1000, 10000, n_samples)
    })
    
    # Add 30-day forward returns
    test_df['growth_future_30d'] = test_df['close_price'].shift(-30) / test_df['close_price']
    
    # Sample predictions (slightly better than random)
    probabilities = np.random.beta(2, 2, n_samples)  # Probabilities between 0 and 1
    predictions = (probabilities > 0.5).astype(int)
    
    # Run backtest
    backtester = TradingBacktester(initial_capital=100000)
    
    try:
        result = backtester.backtest_single_stock(
            test_df=test_df,
            predictions=predictions,
            probabilities=probabilities,
            symbol='TEST',
            probability_threshold=0.6
        )
        
        # Generate report
        report = backtester.generate_backtest_report('TEST')
        print(report)
        
        print("\n🎉 Backtesting framework test completed successfully!")
        
    except Exception as e:
        logger.error(f"Backtesting test failed: {e}")
        import traceback
        traceback.print_exc()