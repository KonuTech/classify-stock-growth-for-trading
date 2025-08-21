#!/usr/bin/env python3
"""
Document DataFrames for all instruments in test_stock_data schema.
Runs test_pipeline.py for each symbol to generate comprehensive documentation.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from stock_etl.core.database import get_test_database
from sqlalchemy import text

def get_all_instruments():
    """Get all active instruments from database"""
    
    db = get_test_database()
    
    with db.get_session() as session:
        result = session.execute(text('''
            SELECT bi.symbol, bi.instrument_type, bi.name
            FROM base_instruments bi
            WHERE bi.is_active = true
            ORDER BY bi.instrument_type, bi.symbol
        '''))
        
        instruments = result.fetchall()
        
    return instruments

def run_pipeline_for_symbol(symbol: str, instrument_type: str, name: str):
    """Run test_pipeline.py for a specific symbol"""
    
    print(f"\n{'='*60}")
    print(f"🚀 DOCUMENTING: {symbol} ({instrument_type})")
    print(f"📝 Name: {name}")
    print(f"{'='*60}")
    
    # Only run ML pipeline for stocks (indices may not have enough data for ML)
    include_ml = instrument_type == 'stock'
    
    if include_ml:
        print(f"🤖 Running COMPLETE ML pipeline with documentation...")
    else:
        print(f"📊 Running DATA pipeline only (no ML for {instrument_type})...")
    
    try:
        # Build command
        python_code = f'''
import sys
sys.path.append('.')
from stock_ml.test_pipeline import test_single_stock_pipeline

print("\\n🔥 Starting pipeline for {symbol}...")
result = test_single_stock_pipeline(
    symbol='{symbol}', 
    include_ml={include_ml}, 
    grid_type='quick'
)

if result:
    print("\\n✅ SUCCESS: {symbol} pipeline completed!")
    print("📋 DataFrame documentation generated in ./docs/knowledge_base/dataframe_schemas/")
else:
    print("\\n❌ FAILED: {symbol} pipeline failed")
'''
        
        # Execute the pipeline (NO TIMEOUT - let it complete)
        result = subprocess.run(
            ['uv', 'run', 'python', '-c', python_code],
            capture_output=False,  # Show output in real-time
            text=True
            # No timeout - let each symbol complete fully
        )
        
        if result.returncode == 0:
            print(f"\n✅ SUCCESS: {symbol} documentation completed")
            return True
        else:
            print(f"\n❌ FAILED: {symbol} pipeline failed with return code {result.returncode}")
            return False
            
    # Removed timeout handling - let pipelines complete fully
    except Exception as e:
        print(f"\n❌ ERROR: {symbol} pipeline failed with error: {e}")
        return False

def main():
    """Main execution function"""
    
    print("🧪 BATCH DOCUMENTATION FOR ALL INSTRUMENTS")
    print("=" * 60)
    print("This script will run test_pipeline.py for each instrument to generate")
    print("comprehensive DataFrame documentation for database integration.")
    print()
    
    # Get all instruments
    print("📋 Fetching instruments from database...")
    try:
        instruments = get_all_instruments()
    except Exception as e:
        print(f"❌ Failed to fetch instruments: {e}")
        return False
    
    if not instruments:
        print("❌ No instruments found in database")
        return False
    
    print(f"✅ Found {len(instruments)} instruments")
    
    # Separate stocks and indices
    stocks = [inst for inst in instruments if inst[1] == 'stock']
    indices = [inst for inst in instruments if inst[1] == 'index']
    
    print(f"   📈 Stocks: {len(stocks)}")
    print(f"   📊 Indices: {len(indices)}")
    
    # Show what will be processed
    print(f"\n🎯 STOCKS TO DOCUMENT (with ML):")
    for symbol, _, name in stocks:
        print(f"   - {symbol}: {name}")
    
    if indices:
        print(f"\n📊 INDICES TO DOCUMENT (data only):")
        for symbol, _, name in indices:
            print(f"   - {symbol}: {name}")
    
    # Auto-execute (no user confirmation needed)
    print(f"\n⚠️  This will run {len(instruments)} pipeline executions.")
    print(f"   Estimated time: {len(stocks) * 3 + len(indices) * 1} minutes")
    print(f"\n🚀 Starting automatically...")
    
    # Execute documentation for each instrument
    print(f"\n🚀 STARTING BATCH DOCUMENTATION...")
    start_time = time.time()
    
    successful = 0
    failed = 0
    results = []
    
    for symbol, instrument_type, name in instruments:
        result = run_pipeline_for_symbol(symbol, instrument_type, name)
        results.append((symbol, instrument_type, result))
        
        if result:
            successful += 1
            print(f"✅ {symbol}: SUCCESS")
        else:
            failed += 1
            print(f"❌ {symbol}: FAILED")
        
        # Brief pause between instruments
        time.sleep(2)
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"🏁 BATCH DOCUMENTATION COMPLETED")
    print(f"{'='*60}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"✅ Successful: {successful}/{len(instruments)}")
    print(f"❌ Failed: {failed}/{len(instruments)}")
    
    print(f"\n📊 DETAILED RESULTS:")
    for symbol, instrument_type, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {symbol} ({instrument_type}): {status}")
    
    print(f"\n📋 DOCUMENTATION FILES LOCATION:")
    print(f"   ./docs/knowledge_base/dataframe_schemas/")
    
    print(f"\n📊 EXPECTED FILE NAMING PATTERN (for stocks):")
    print(f"   step02_feature_engineering_output_{{symbol}}.md")
    print(f"   step05_model_training_results_{{symbol}}.md") 
    print(f"   step06_model_predictions_{{symbol}}.md")
    print(f"   step07_backtest_results_{{symbol}}.md")
    print(f"   step07_trade_history_{{symbol}}.md")
    
    if successful > 0:
        print(f"\n🎉 {successful} instruments documented successfully!")
        print(f"📈 Check the generated .md files for DataFrame structures")
        print(f"💡 Files are now clearly named by pipeline step and database table")
        return True
    else:
        print(f"\n😞 No instruments were successfully documented")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Documentation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)