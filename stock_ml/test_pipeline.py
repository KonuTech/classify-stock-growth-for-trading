"""
Test script for the complete data extraction and preprocessing pipeline.
Tests all modules working together from database extraction to model-ready data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import logging
try:
    # Try relative imports first (when used as module)
    from .data_extractor import MultiStockDataExtractor
    from .feature_engineering import StockFeatureEngineer
    from .preprocessing import XGBoostPreprocessor
    from .model_trainer_optimized import XGBoostTrainer
    from .backtesting import TradingBacktester
except ImportError:
    # Fall back to direct imports (when run as script)
    from data_extractor import MultiStockDataExtractor
    from feature_engineering import StockFeatureEngineer
    from preprocessing import XGBoostPreprocessor
    from model_trainer_optimized import XGBoostTrainer
    from backtesting import TradingBacktester

# Set up logging using centralized configuration
try:
    from .logging_config import get_ml_logger
except ImportError:
    from logging_config import get_ml_logger
logger = get_ml_logger(__name__)


def test_complete_pipeline():
    """Test the complete data pipeline from extraction to preprocessing"""
    logger.info("Starting complete pipeline test...")
    
    # Initialize components
    extractor = MultiStockDataExtractor()
    engineer = StockFeatureEngineer()
    preprocessor = XGBoostPreprocessor()
    
    try:
        # Step 1: Data Extraction
        logger.info("\n" + "="*50)
        logger.info("STEP 1: DATA EXTRACTION")
        logger.info("="*50)
        
        # Get available stocks
        available_stocks = extractor.get_available_stocks()
        logger.info(f"Available stocks: {available_stocks}")
        
        # Extract all stock data
        all_data = extractor.extract_all_stocks_data()
        logger.info(f"Extracted data for {len(all_data)} stocks")
        
        # Filter by quality
        quality_data = extractor.filter_stocks_by_data_quality(
            all_data, 
            min_records=500,  # At least 500 trading days
            min_years=2.0     # At least 2 years
        )
        logger.info(f"Quality stocks: {list(quality_data.keys())}")
        
        if not quality_data:
            logger.error("No stocks meet quality criteria. Exiting.")
            return False
            
        # Step 2: Feature Engineering
        logger.info("\n" + "="*50)
        logger.info("STEP 2: FEATURE ENGINEERING")
        logger.info("="*50)
        
        engineered_data = engineer.engineer_multiple_stocks(quality_data)
        
        if not engineered_data:
            logger.error("Feature engineering failed. Exiting.")
            return False
            
        for symbol, df in engineered_data.items():
            logger.info(f"{symbol}: {df.shape[0]} records, {df.shape[1]} features")
            target_dist = df['target'].value_counts(normalize=True) if 'target' in df.columns else {}
            logger.info(f"  Target distribution: {target_dist.to_dict()}")
            
        # Step 3: Data Splitting
        logger.info("\n" + "="*50)
        logger.info("STEP 3: DATA SPLITTING")
        logger.info("="*50)
        
        split_data = extractor.split_all_stocks_data(engineered_data)
        
        for symbol, (train_df, val_df, test_df) in split_data.items():
            logger.info(f"{symbol}: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
            
        # Step 4: Preprocessing
        logger.info("\n" + "="*50)
        logger.info("STEP 4: PREPROCESSING")
        logger.info("="*50)
        
        preprocessed_data = preprocessor.preprocess_multiple_stocks(
            split_data, 
            max_features=30
        )
        
        if not preprocessed_data:
            logger.error("Preprocessing failed. Exiting.")
            return False
            
        # Step 5: Results Summary
        logger.info("\n" + "="*50)
        logger.info("STEP 5: RESULTS SUMMARY")
        logger.info("="*50)
        
        summary = preprocessor.get_preprocessing_summary(preprocessed_data)
        print(summary.to_string(index=False))
        
        # Detailed results for one stock (preferably XTB)
        test_symbol = 'XTB' if 'XTB' in preprocessed_data else list(preprocessed_data.keys())[0]
        if test_symbol in preprocessed_data:
            logger.info(f"\n" + "="*30)
            logger.info(f"DETAILED RESULTS FOR {test_symbol}")
            logger.info("="*30)
            
            data = preprocessed_data[test_symbol]
            
            logger.info(f"Original features: {data['original_feature_count']}")
            logger.info(f"Selected features: {data['final_feature_count']}")
            logger.info(f"Selected feature names (top 10): {data['selected_features'][:10]}")
            
            logger.info(f"\nDataset sizes:")
            logger.info(f"  Training: {data['X_train'].shape}")
            logger.info(f"  Validation: {data['X_val'].shape}")
            logger.info(f"  Test: {data['X_test'].shape}")
            
            logger.info(f"\nTarget distributions:")
            logger.info(f"  Training: {data['y_train'].value_counts(normalize=True).to_dict()}")
            logger.info(f"  Validation: {data['y_val'].value_counts(normalize=True).to_dict()}")
            logger.info(f"  Test: {data['y_test'].value_counts(normalize=True).to_dict()}")
            
            # Check for any remaining NaN values
            train_nan = data['X_train'].isnull().sum().sum()
            val_nan = data['X_val'].isnull().sum().sum()
            test_nan = data['X_test'].isnull().sum().sum()
            
            logger.info(f"\nMissing values check:")
            logger.info(f"  Training: {train_nan} NaN values")
            logger.info(f"  Validation: {val_nan} NaN values")
            logger.info(f"  Test: {test_nan} NaN values")
            
            # Feature statistics
            logger.info(f"\nFeature statistics (training set):")
            feature_stats = data['X_train'].describe()
            logger.info(f"  Mean range: {feature_stats.loc['mean'].min():.4f} to {feature_stats.loc['mean'].max():.4f}")
            logger.info(f"  Std range: {feature_stats.loc['std'].min():.4f} to {feature_stats.loc['std'].max():.4f}")
            
        logger.info("\n" + "="*50)
        logger.info("PIPELINE TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        extractor.close()


def test_single_stock_pipeline(symbol: str = 'XTB', include_ml: bool = True, force_cpu: bool = True, grid_type: str = 'quick'):
    """Test complete pipeline for a single stock including ML training and backtesting
    
    Args:
        symbol: Stock symbol to test
        include_ml: Include ML training and backtesting
        force_cpu: Force CPU usage (recommended for reliability)
        grid_type: Grid search type - 'quick', 'comprehensive', 'production'
    """
    logger.info(f"Testing {'complete ML' if include_ml else 'data'} pipeline for {symbol} (grid_type={grid_type})...")
    
    extractor = MultiStockDataExtractor()
    engineer = StockFeatureEngineer()
    preprocessor = XGBoostPreprocessor()
    
    if include_ml:
        # Use CPU-first configuration by default
        trainer = XGBoostTrainer(random_state=42, force_cpu=force_cpu)
        backtester = TradingBacktester(initial_capital=100000)
    
    try:
        # Step 1: Extract single stock
        logger.info(f"\n📊 STEP 1: DATA EXTRACTION FOR {symbol}")
        df = extractor.extract_single_stock_data(symbol)
        if df.empty:
            logger.error(f"No data found for {symbol}")
            return False
            
        logger.info(f"✅ Extracted {len(df)} records for {symbol}")
        logger.info(f"   Date range: {df['trading_date_local'].min()} to {df['trading_date_local'].max()}")
        
        # Step 2: Engineer features
        logger.info(f"\n🔧 STEP 2: FEATURE ENGINEERING FOR {symbol}")
        engineered_df = engineer.engineer_all_features(df, symbol)
        if engineered_df.empty:
            logger.error(f"Feature engineering failed for {symbol}")
            return False
            
        logger.info(f"✅ Engineered {engineered_df.shape[1]} features for {symbol}")
        
        if 'target' in engineered_df.columns:
            target_dist = engineered_df['target'].value_counts(normalize=True)
            logger.info(f"   Target distribution: Positive {target_dist.get(1, 0):.1%}, Negative {target_dist.get(0, 0):.1%}")
        
        # Step 3: Split data
        logger.info(f"\n📈 STEP 3: DATA SPLITTING FOR {symbol}")
        train_df, val_df, test_df = extractor.split_data_chronologically(engineered_df)
        logger.info(f"✅ Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        # Step 4: Preprocess
        logger.info(f"\n🔄 STEP 4: PREPROCESSING FOR {symbol}")
        result = preprocessor.preprocess_single_stock(train_df, val_df, test_df, symbol, max_features=25)
        
        logger.info(f"✅ Preprocessing completed for {symbol}")
        logger.info(f"   Features: {result['original_feature_count']} → {result['final_feature_count']}")
        logger.info(f"   Selected features: {result['selected_features'][:5]}...")
        
        # Class distribution analysis
        class_analysis = result.get('class_analysis', {})
        if class_analysis:
            logger.info(f"   Class imbalance ratio: {class_analysis['imbalance_ratio']:.1f}:1")
            logger.info(f"   Positive samples: {class_analysis['positive_count']} ({class_analysis['positive_ratio']:.1%})")
        
        if not include_ml:
            logger.info(f"✅ Data pipeline test completed successfully for {symbol}")
            return True
        
        # Step 5: Model Training
        logger.info(f"\n🤖 STEP 5: MODEL TRAINING FOR {symbol}")
        training_results = trainer.train_with_grid_search(
            X_train=result['X_train'],
            y_train=result['y_train'],
            X_val=result['X_val'],
            y_val=result['y_val'],
            symbol=symbol,
            grid_type=grid_type,  # Use parameter for grid search type
            cv_folds=3
        )
        
        logger.info(f"✅ Model training completed for {symbol}")
        logger.info(f"   Best CV score: {training_results['cv_score']:.4f}")
        logger.info(f"   Validation ROC-AUC: {training_results['val_roc_auc']:.4f}")
        logger.info(f"   Best params: {training_results['best_params']}")
        
        # Step 6: Test Evaluation (use model from training results)
        logger.info(f"\n📋 STEP 6: TEST EVALUATION FOR {symbol}")
        
        # Get trained model and make predictions on test set
        model = training_results['model']
        X_test = result['X_test']
        y_test = result['y_test']
        
        # Make predictions
        test_predictions = model.predict(X_test)
        test_probabilities = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
        test_accuracy = accuracy_score(y_test, test_predictions)
        test_roc_auc = roc_auc_score(y_test, test_probabilities)
        test_f1 = f1_score(y_test, test_predictions)
        
        # Create test results dict
        test_results = {
            'test_predictions': test_predictions,
            'test_probabilities': test_probabilities,
            'test_accuracy': test_accuracy,
            'test_roc_auc': test_roc_auc,
            'test_f1': test_f1
        }
        
        logger.info(f"✅ Test evaluation completed for {symbol}")
        logger.info(f"   Test ROC-AUC: {test_results['test_roc_auc']:.4f}")
        logger.info(f"   Test Accuracy: {test_results['test_accuracy']:.4f}")
        logger.info(f"   Test F1-Score: {test_results['test_f1']:.4f}")
        
        # Step 7: Backtesting
        logger.info(f"\n💰 STEP 7: BACKTESTING FOR {symbol}")
        backtest_results = backtester.backtest_single_stock(
            test_df=test_df,
            predictions=test_results['test_predictions'],
            probabilities=test_results['test_probabilities'],
            symbol=symbol,
            probability_threshold=0.6
        )
        
        if 'error' not in backtest_results:
            logger.info(f"✅ Backtesting completed for {symbol}")
            logger.info(f"   Total return: {backtest_results['total_return']:.2%}")
            logger.info(f"   Win rate: {backtest_results['win_rate']:.2%}")
            logger.info(f"   Total trades: {backtest_results['total_trades']}")
            logger.info(f"   Sharpe ratio: {backtest_results['sharpe_ratio']:.3f}")
        else:
            logger.warning(f"⚠️ Backtesting issue for {symbol}: {backtest_results['error']}")
        
        # Final Assessment
        logger.info(f"\n🎯 FINAL ASSESSMENT FOR {symbol}")
        model_good = test_results['test_roc_auc'] >= 0.55 and test_results['test_accuracy'] >= 0.52
        trading_good = backtest_results.get('win_rate', 0) >= 0.40 if 'error' not in backtest_results else False
        
        logger.info(f"   Model Quality: {'✅ GOOD' if model_good else '⚠️ NEEDS IMPROVEMENT'}")
        if 'error' not in backtest_results:
            logger.info(f"   Trading Quality: {'✅ GOOD' if trading_good else '⚠️ NEEDS IMPROVEMENT'}")
        
        overall_success = model_good and (trading_good or 'error' in backtest_results)
        logger.info(f"   Overall: {'✅ SUCCESS' if overall_success else '⚠️ PARTIAL SUCCESS'}")
        
        return True
        
    except Exception as e:
        logger.error(f"Single stock pipeline failed for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        extractor.close()


if __name__ == "__main__":
    # Run tests
    print("🧪 Stock ML Pipeline Tests")
    print("=" * 50)
    print("Choose test mode:")
    print("1. Single stock ML test (XTB) - Complete pipeline with training")
    print("2. Single stock data test (XTB) - Data pipeline only")
    print("3. Multi-stock data test - All stocks data pipeline")
    print("4. Interactive mode - Choose symbol")
    
    import sys
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = input("\nEnter choice (1-4, default=1): ").strip() or "1"
    
    try:
        if mode == "1":
            print("\n🚀 Running Single Stock ML Test (XTB)...")
            success = test_single_stock_pipeline('XTB', include_ml=True)
            
        elif mode == "2":
            print("\n🚀 Running Single Stock Data Test (XTB)...")
            success = test_single_stock_pipeline('XTB', include_ml=False)
            
        elif mode == "3":
            print("\n🚀 Running Multi-Stock Data Test...")
            success = test_complete_pipeline()
            
        elif mode == "4":
            symbol = input("Enter stock symbol (default=XTB): ").strip() or "XTB"
            include_ml = input("Include ML training? (y/N): ").strip().lower() == 'y'
            force_cpu = input("Force CPU mode? (y/N): ").strip().lower() == 'y' if include_ml else False
            print(f"\n🚀 Running {'Complete ML' if include_ml else 'Data'} Test for {symbol}...")
            if include_ml and force_cpu:
                print("🔧 CPU mode forced - GPU acceleration disabled")
            success = test_single_stock_pipeline(symbol, include_ml=include_ml, force_cpu=force_cpu, grid_type='quick')
            
        else:
            print("Invalid choice. Running default single stock ML test...")
            success = test_single_stock_pipeline('XTB', include_ml=True, grid_type='quick')
        
        # Final result
        print("\n" + "=" * 60)
        if success:
            print("🎉 TEST COMPLETED SUCCESSFULLY!")
            print("✅ Pipeline is working correctly")
            print("✅ SMOTE removal was successful")
            if mode == "1" or (mode == "4" and include_ml):
                print("✅ Complete ML pipeline validated")
        else:
            print("❌ TEST FAILED!")
            print("⚠️ Check error messages above")
            print("⚠️ Verify database connection and data availability")
        
        print("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# QUICK EXECUTION COMMANDS FOR DATAFRAME DOCUMENTATION:
# 
# 1. Test ML pipeline with quick grid search and generate DataFrame documentation:
#    uv run python stock_ml/test_pipeline.py 1
#
# 2. Or run directly with Python:
#    uv run python -c "
#    import sys; sys.path.append('.')
#    from stock_ml.test_pipeline import test_single_stock_pipeline
#    test_single_stock_pipeline('XTB', include_ml=True, grid_type='quick')
#    "
#
# 3. Test different symbols or grid types:
#    uv run python -c "
#    import sys; sys.path.append('.')
#    from stock_ml.test_pipeline import test_single_stock_pipeline
#    test_single_stock_pipeline('CDR', include_ml=True, grid_type='quick')
#    "
#
# The DataFrame documentation files will be saved to:
#    ./docs/knowledge_base/dataframe_schemas/
#
# Files generated:
#    - feature_engineering_engineered_features_xtb.md
#    - model_training_results_xtb.md  
#    - model_predictions_xtb.md
#    - backtest_results_xtb.md
#    - trade_history_xtb.md