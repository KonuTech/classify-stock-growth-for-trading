"""
Complete Random Forest stock growth classification pipeline.
Integrates data extraction, feature engineering, model training, and backtesting.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import json

try:
    from .data_extractor import MultiStockDataExtractor
    from .feature_engineering import StockFeatureEngineer
    from .preprocessing import RandomForestPreprocessor
    from .model_trainer import MultiStockRandomForestTrainer
    from .backtesting import TradingBacktester
except ImportError:
    from data_extractor import MultiStockDataExtractor
    from feature_engineering import StockFeatureEngineer
    from preprocessing import RandomForestPreprocessor
    from model_trainer import MultiStockRandomForestTrainer
    from backtesting import TradingBacktester

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StockGrowthClassificationPipeline:
    """Complete pipeline for stock growth classification and trading strategy"""
    
    def __init__(self, db_config: Dict = None, 
                 random_state: int = 42,
                 output_dir: str = "output"):
        """
        Initialize the complete pipeline
        
        Args:
            db_config: Database configuration
            random_state: Random state for reproducibility
            output_dir: Directory to save results
        """
        self.db_config = db_config
        self.random_state = random_state
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.extractor = MultiStockDataExtractor(db_config)
        self.engineer = StockFeatureEngineer()
        self.preprocessor = RandomForestPreprocessor(random_state)
        self.trainer = MultiStockRandomForestTrainer(random_state)
        self.backtester = TradingBacktester()
        
        # Pipeline state
        self.pipeline_results = {}
        self.execution_log = []
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Log pipeline execution step"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'status': status,
            'details': details
        }
        self.execution_log.append(log_entry)
        logger.info(f"{step}: {status} - {details}")
        
    def run_complete_pipeline(self, 
                            min_records: int = 500,
                            min_years: float = 2.0,
                            max_features: int = 30,
                            grid_type: str = 'comprehensive',
                            probability_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Run the complete pipeline from data extraction to backtesting
        
        Args:
            min_records: Minimum records required per stock
            min_years: Minimum years of data required
            max_features: Maximum features for model training
            grid_type: Hyperparameter grid type
            probability_threshold: Trading probability threshold
            
        Returns:
            Complete pipeline results
        """
        logger.info("Starting complete stock growth classification pipeline...")
        start_time = datetime.now()
        
        try:
            # Step 1: Data Extraction
            self.log_step("Data Extraction", "STARTED")
            
            all_data = self.extractor.extract_all_stocks_data()
            quality_data = self.extractor.filter_stocks_by_data_quality(
                all_data, min_records=min_records, min_years=min_years
            )
            
            if not quality_data:
                raise ValueError("No stocks meet quality criteria")
                
            self.pipeline_results['available_stocks'] = list(quality_data.keys())
            self.log_step("Data Extraction", "COMPLETED", f"{len(quality_data)} stocks extracted")
            
            # Step 2: Feature Engineering
            self.log_step("Feature Engineering", "STARTED")
            
            engineered_data = self.engineer.engineer_multiple_stocks(quality_data)
            
            if not engineered_data:
                raise ValueError("Feature engineering failed for all stocks")
                
            self.pipeline_results['engineered_stocks'] = list(engineered_data.keys())
            self.log_step("Feature Engineering", "COMPLETED", f"{len(engineered_data)} stocks engineered")
            
            # Step 3: Data Splitting
            self.log_step("Data Splitting", "STARTED")
            
            split_data = self.extractor.split_all_stocks_data(engineered_data)
            
            self.pipeline_results['split_data'] = split_data
            self.log_step("Data Splitting", "COMPLETED", f"{len(split_data)} stocks split")
            
            # Step 4: Preprocessing
            self.log_step("Preprocessing", "STARTED")
            
            preprocessed_data = self.preprocessor.preprocess_multiple_stocks(
                split_data, max_features=max_features
            )
            
            if not preprocessed_data:
                raise ValueError("Preprocessing failed for all stocks")
                
            self.pipeline_results['preprocessed_stocks'] = list(preprocessed_data.keys())
            self.pipeline_results['preprocessing_summary'] = self.preprocessor.get_preprocessing_summary(preprocessed_data)
            self.log_step("Preprocessing", "COMPLETED", f"{len(preprocessed_data)} stocks preprocessed")
            
            # Step 5: Model Training
            self.log_step("Model Training", "STARTED")
            
            training_results = self.trainer.train_multiple_stocks(
                preprocessed_data, grid_type=grid_type
            )
            
            if not training_results:
                raise ValueError("Model training failed for all stocks")
                
            self.pipeline_results['trained_models'] = list(training_results.keys())
            self.pipeline_results['training_summary'] = self.trainer.get_results_summary()
            self.log_step("Model Training", "COMPLETED", f"{len(training_results)} models trained")
            
            # Step 6: Backtesting
            self.log_step("Backtesting", "STARTED")
            
            # Prepare test data for backtesting
            test_data = {}
            for symbol in training_results.keys():
                if symbol in split_data:
                    _, _, test_df = split_data[symbol]
                    test_data[symbol] = test_df
                    
            backtest_results = self.backtester.backtest_multiple_stocks(
                training_results, test_data, probability_threshold=probability_threshold
            )
            
            self.pipeline_results['backtest_results'] = backtest_results
            self.log_step("Backtesting", "COMPLETED", f"{len(backtest_results['individual_results'])} stocks backtested")
            
            # Step 7: Results Summary
            self.log_step("Results Summary", "STARTED")
            
            pipeline_summary = self._generate_pipeline_summary(
                quality_data, engineered_data, preprocessed_data, 
                training_results, backtest_results
            )
            
            self.pipeline_results['pipeline_summary'] = pipeline_summary
            self.pipeline_results['execution_time_minutes'] = (datetime.now() - start_time).total_seconds() / 60
            
            # Save results
            self._save_pipeline_results()
            
            self.log_step("Results Summary", "COMPLETED", "Pipeline results saved")
            
            logger.info(f"Complete pipeline finished successfully in {self.pipeline_results['execution_time_minutes']:.1f} minutes")
            return self.pipeline_results
            
        except Exception as e:
            self.log_step("Pipeline", "FAILED", str(e))
            logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self.extractor.close()
            
    def _generate_pipeline_summary(self, quality_data: Dict, engineered_data: Dict,
                                 preprocessed_data: Dict, training_results: Dict,
                                 backtest_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive pipeline summary"""
        
        summary = {
            'execution_date': datetime.now().isoformat(),
            'data_processing': {
                'initial_stocks': len(quality_data),
                'engineered_stocks': len(engineered_data),
                'trained_stocks': len(training_results),
                'backtested_stocks': len(backtest_results['individual_results']),
                'success_rate': len(backtest_results['individual_results']) / len(quality_data) if quality_data else 0
            },
            'model_performance': {},
            'trading_performance': {},
            'best_performing_stocks': [],
            'recommendations': []
        }
        
        # Model performance summary
        if training_results:
            training_summary = self.trainer.get_results_summary()
            summary['model_performance'] = {
                'avg_cv_score': training_summary['cv_score'].mean(),
                'avg_test_accuracy': training_summary['test_accuracy'].mean(),
                'avg_test_roc_auc': training_summary['test_roc_auc'].mean(),
                'best_model_symbol': training_summary.loc[training_summary['test_roc_auc'].idxmax(), 'symbol'],
                'best_model_roc_auc': training_summary['test_roc_auc'].max()
            }
            
        # Trading performance summary
        if 'portfolio_summary' in backtest_results:
            portfolio_summary = backtest_results['portfolio_summary']
            summary['trading_performance'] = portfolio_summary
            
            # Identify best performing stocks
            individual_results = backtest_results['individual_results']
            sorted_stocks = sorted(
                [(k, v) for k, v in individual_results.items() if 'error' not in v],
                key=lambda x: x[1]['total_return'],
                reverse=True
            )
            
            summary['best_performing_stocks'] = [
                {
                    'symbol': symbol,
                    'total_return': result['total_return'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'win_rate': result['win_rate']
                }
                for symbol, result in sorted_stocks[:5]  # Top 5
            ]
            
        # Generate recommendations
        summary['recommendations'] = self._generate_recommendations(summary)
        
        return summary
        
    def _generate_recommendations(self, summary: Dict) -> List[str]:
        """Generate trading recommendations based on results"""
        recommendations = []
        
        # Model performance recommendations
        if 'model_performance' in summary:
            avg_roc_auc = summary['model_performance'].get('avg_test_roc_auc', 0)
            if avg_roc_auc > 0.65:
                recommendations.append("✅ Strong model performance - ROC-AUC above 0.65, suitable for trading")
            elif avg_roc_auc > 0.55:
                recommendations.append("⚠️ Moderate model performance - consider additional feature engineering")
            else:
                recommendations.append("❌ Weak model performance - not recommended for live trading")
                
        # Trading performance recommendations
        if 'trading_performance' in summary:
            trading_perf = summary['trading_performance']
            avg_return = trading_perf.get('avg_total_return', 0)
            profitable_rate = trading_perf.get('profitable_stock_rate', 0)
            
            if avg_return > 0.15:  # >15% average return
                recommendations.append("✅ Excellent trading returns - strategy shows strong alpha generation")
            elif avg_return > 0.05:  # >5% average return
                recommendations.append("✅ Positive trading returns - strategy beats cash")
            else:
                recommendations.append("❌ Poor trading returns - strategy needs improvement")
                
            if profitable_rate > 0.7:  # >70% stocks profitable
                recommendations.append("✅ High success rate across stocks - robust strategy")
            elif profitable_rate > 0.5:  # >50% stocks profitable
                recommendations.append("⚠️ Moderate success rate - consider stock selection criteria")
            else:
                recommendations.append("❌ Low success rate - strategy may not generalize well")
                
        # Best stocks recommendations
        if summary['best_performing_stocks']:
            best_stocks = [stock['symbol'] for stock in summary['best_performing_stocks'][:3]]
            recommendations.append(f"🎯 Focus on top performers: {', '.join(best_stocks)}")
            
        return recommendations
        
    def _save_pipeline_results(self):
        """Save comprehensive pipeline results to files"""
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_dir / f"pipeline_run_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save pipeline summary as JSON
        summary_path = run_dir / "pipeline_summary.json"
        with open(summary_path, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            summary_json = self._convert_numpy_types(self.pipeline_results['pipeline_summary'])
            json.dump(summary_json, f, indent=2)
            
        # Save training summary as CSV
        if 'training_summary' in self.pipeline_results:
            training_path = run_dir / "training_summary.csv"
            self.pipeline_results['training_summary'].to_csv(training_path, index=False)
            
        # Save preprocessing summary as CSV
        if 'preprocessing_summary' in self.pipeline_results:
            preprocessing_path = run_dir / "preprocessing_summary.csv"
            self.pipeline_results['preprocessing_summary'].to_csv(preprocessing_path, index=False)
            
        # Save execution log
        log_path = run_dir / "execution_log.json"
        with open(log_path, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
            
        # Save models
        model_dir = run_dir / "models"
        self.trainer.save_all_models(str(model_dir))
        
        # Generate and save comprehensive report
        report_path = run_dir / "pipeline_report.txt"
        report = self.generate_comprehensive_report()
        with open(report_path, 'w') as f:
            f.write(report)
            
        logger.info(f"Pipeline results saved to {run_dir}")
        
    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(v) for v in obj]
        else:
            return obj
            
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive pipeline report"""
        
        if not self.pipeline_results:
            return "No pipeline results available"
            
        summary = self.pipeline_results.get('pipeline_summary', {})
        
        lines = [
            "STOCK GROWTH CLASSIFICATION PIPELINE REPORT",
            "=" * 60,
            f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Pipeline Duration: {self.pipeline_results.get('execution_time_minutes', 0):.1f} minutes",
            "",
            "DATA PROCESSING SUMMARY:",
            f"  Initial stocks extracted: {summary.get('data_processing', {}).get('initial_stocks', 0)}",
            f"  Successfully engineered: {summary.get('data_processing', {}).get('engineered_stocks', 0)}",
            f"  Models trained: {summary.get('data_processing', {}).get('trained_stocks', 0)}",
            f"  Backtests completed: {summary.get('data_processing', {}).get('backtested_stocks', 0)}",
            f"  Pipeline success rate: {summary.get('data_processing', {}).get('success_rate', 0):.1%}",
            "",
            "MODEL PERFORMANCE:",
            f"  Average CV Score: {summary.get('model_performance', {}).get('avg_cv_score', 0):.4f}",
            f"  Average Test Accuracy: {summary.get('model_performance', {}).get('avg_test_accuracy', 0):.4f}",
            f"  Average Test ROC-AUC: {summary.get('model_performance', {}).get('avg_test_roc_auc', 0):.4f}",
            f"  Best Model: {summary.get('model_performance', {}).get('best_model_symbol', 'N/A')} "
            f"(ROC-AUC: {summary.get('model_performance', {}).get('best_model_roc_auc', 0):.4f})",
            "",
            "TRADING PERFORMANCE:",
            f"  Equal-Weight Portfolio Return: {summary.get('trading_performance', {}).get('equal_weight_portfolio_return', 0):.2%}",
            f"  Average Return per Stock: {summary.get('trading_performance', {}).get('avg_total_return', 0):.2%}",
            f"  Profitable Stock Rate: {summary.get('trading_performance', {}).get('profitable_stock_rate', 0):.1%}",
            f"  Average Win Rate: {summary.get('trading_performance', {}).get('avg_win_rate', 0):.1%}",
            f"  Total Trades (All Stocks): {summary.get('trading_performance', {}).get('total_trades_all_stocks', 0)}",
            "",
            "TOP PERFORMING STOCKS:"
        ]
        
        # Add top performing stocks
        for i, stock in enumerate(summary.get('best_performing_stocks', []), 1):
            lines.append(
                f"  {i}. {stock['symbol']}: {stock['total_return']:+.2%} return, "
                f"Sharpe: {stock['sharpe_ratio']:.3f}, Win Rate: {stock['win_rate']:.1%}"
            )
        
        lines.extend([
            "",
            "RECOMMENDATIONS:",
        ])
        
        # Add recommendations
        for rec in summary.get('recommendations', []):
            lines.append(f"  {rec}")
            
        lines.extend([
            "",
            "=" * 60,
            "Pipeline execution completed successfully!",
            "=" * 60
        ])
        
        return "\n".join(lines)


def main():
    """Run the complete pipeline with default settings"""
    
    # Configuration
    config = {
        'db_config': {
            'host': 'localhost',
            'port': '5432',
            'database': 'stock_data',
            'user': 'postgres',
            'password': 'postgres'
        },
        'min_records': 500,
        'min_years': 2.0,
        'max_features': 30,
        'grid_type': 'comprehensive',  # Use 'quick' for faster testing
        'probability_threshold': 0.6
    }
    
    try:
        # Initialize pipeline
        pipeline = StockGrowthClassificationPipeline(
            db_config=config['db_config'],
            random_state=42,
            output_dir="pipeline_output"
        )
        
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(
            min_records=config['min_records'],
            min_years=config['min_years'],
            max_features=config['max_features'],
            grid_type=config['grid_type'],
            probability_threshold=config['probability_threshold']
        )
        
        # Print summary report
        report = pipeline.generate_comprehensive_report()
        print("\n" + report)
        
        print(f"\n🎉 Complete pipeline executed successfully!")
        print(f"📊 Results saved to: {pipeline.output_dir}")
        
        return results
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()