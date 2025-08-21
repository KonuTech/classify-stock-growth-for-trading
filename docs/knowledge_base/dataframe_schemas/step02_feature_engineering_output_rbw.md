# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:39:45  
**Symbol**: RBW  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 4,383 rows × 193 columns
- **Memory Usage**: 6.68 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: RBW(4383) |
| currency | object | 0 | 0.0% |  | Examples: PLN(4383) |
| close_price | float64 | 0 | 0.0% |  |
| volume | int64 | 0 | 0.0% |  |
| trading_date_local | datetime64[ns] | 0 | 0.0% |  |
| year | int32 | 0 | 0.0% |  |
| month | int32 | 0 | 0.0% |  |
| weekday | int32 | 0 | 0.0% |  |
| quarter | int32 | 0 | 0.0% |  |
| day_of_year | int32 | 0 | 0.0% |  |
| week_of_year | UInt32 | 0 | 0.0% |  |
| is_month_end | int64 | 0 | 0.0% |  |
| is_quarter_end | int64 | 0 | 0.0% |  |
| is_year_end | int64 | 0 | 0.0% |  |
| growth_1d | float64 | 0 | 0.0% |  |
| growth_3d | float64 | 0 | 0.0% |  |
| growth_7d | float64 | 0 | 0.0% |  |
| growth_14d | float64 | 0 | 0.0% |  |
| growth_30d | float64 | 0 | 0.0% |  |
| growth_60d | float64 | 15 | 0.3% |  |
| growth_90d | float64 | 45 | 1.0% |  |
| growth_180d | float64 | 135 | 3.1% |  |
| growth_365d | float64 | 320 | 7.3% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.3% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 1.2% |  |
| sma_200 | float64 | 154 | 3.5% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 3.5% |  |
| sma_10_above_20 | int64 | 0 | 0.0% |  |
| sma_20_above_50 | int64 | 0 | 0.0% |  |
| sma_50_above_200 | int64 | 0 | 0.0% |  |
| price_above_sma_20 | int64 | 0 | 0.0% |  |
| price_above_sma_50 | int64 | 0 | 0.0% |  |
| daily_return | float64 | 0 | 0.0% |  |
| daily_return_squared | float64 | 0 | 0.0% |  |
| volatility_5d | float64 | 0 | 0.0% |  |
| return_mean_5d | float64 | 0 | 0.0% |  |
| volatility_10d | float64 | 0 | 0.0% |  |
| return_mean_10d | float64 | 0 | 0.0% |  |
| volatility_20d | float64 | 0 | 0.0% |  |
| return_mean_20d | float64 | 0 | 0.0% |  |
| volatility_30d | float64 | 0 | 0.0% |  |
| return_mean_30d | float64 | 0 | 0.0% |  |
| volatility_60d | float64 | 15 | 0.3% |  |
| return_mean_60d | float64 | 15 | 0.3% |  |
| price_momentum_5d | float64 | 0 | 0.0% |  |
| price_momentum_20d | float64 | 0 | 0.0% |  |
| price_position_20d | float64 | 0 | 0.0% |  |
| price_position_60d | float64 | 14 | 0.3% |  |
| volume_ma_5 | float64 | 0 | 0.0% |  |
| volume_ma_10 | float64 | 0 | 0.0% |  |
| volume_ma_20 | float64 | 0 | 0.0% |  |
| volume_ma_50 | float64 | 4 | 0.1% |  |
| volume_ratio_10d | float64 | 0 | 0.0% |  |
| volume_ratio_20d | float64 | 0 | 0.0% |  |
| volume_ratio_50d | float64 | 4 | 0.1% |  |
| volume_increasing_10d | int64 | 0 | 0.0% |  |
| volume_increasing_20d | int64 | 0 | 0.0% |  |
| price_volume_trend_5d | float64 | 0 | 0.0% |  |
| price_volume_trend_20d | float64 | 0 | 0.0% |  |
| volume_momentum_5d | float64 | 0 | 0.0% |  |
| volume_momentum_20d | float64 | 0 | 0.0% |  |
| volume_volatility_20d | float64 | 0 | 0.0% |  |
| obv_approx | int64 | 0 | 0.0% |  |
| obv_ma_20 | float64 | 0 | 0.0% |  |
| open_price | float64 | 0 | 0.0% |  |
| high_price | float64 | 0 | 0.0% |  |
| low_price | float64 | 0 | 0.0% |  |
| rsi_14 | float64 | 0 | 0.0% |  |
| rsi_7 | float64 | 0 | 0.0% |  |
| macd | float64 | 0 | 0.0% |  |
| macd_signal | float64 | 0 | 0.0% |  |
| macd_hist | float64 | 0 | 0.0% |  |
| stoch_k | float64 | 0 | 0.0% |  |
| stoch_d | float64 | 0 | 0.0% |  |
| stoch_rsi_k | float64 | 0 | 0.0% |  |
| stoch_rsi_d | float64 | 0 | 0.0% |  |
| williams_r | float64 | 0 | 0.0% |  |
| adx | float64 | 0 | 0.0% |  |
| plus_di | float64 | 0 | 0.0% |  |
| minus_di | float64 | 0 | 0.0% |  |
| cci | float64 | 0 | 0.0% |  |
| cmo | float64 | 0 | 0.0% |  |
| roc_10 | float64 | 0 | 0.0% |  |
| roc_20 | float64 | 0 | 0.0% |  |
| momentum_10 | float64 | 0 | 0.0% |  |
| atr | float64 | 0 | 0.0% |  |
| natr | float64 | 0 | 0.0% |  |
| bb_upper | float64 | 0 | 0.0% |  |
| bb_middle | float64 | 0 | 0.0% |  |
| bb_lower | float64 | 0 | 0.0% |  |
| bb_width | float64 | 0 | 0.0% |  |
| bb_position | float64 | 2 | 0.0% |  |
| obv | float64 | 0 | 0.0% |  |
| ad_line | float64 | 0 | 0.0% |  |
| mfi | float64 | 0 | 0.0% |  |
| typical_price | float64 | 0 | 0.0% |  |
| weighted_close | float64 | 0 | 0.0% |  |
| median_price | float64 | 0 | 0.0% |  |
| dema_20 | float64 | 0 | 0.0% |  |
| tema_20 | float64 | 12 | 0.3% |  |
| trima_20 | float64 | 0 | 0.0% |  |
| cdl_doji | int32 | 0 | 0.0% |  |
| cdl_hammer | int32 | 0 | 0.0% |  |
| cdl_engulfing | int32 | 0 | 0.0% |  |
| cdl_morning_star | int32 | 0 | 0.0% |  |
| cdl_evening_star | int32 | 0 | 0.0% |  |
| log_return_1d | float64 | 0 | 0.0% |  |
| log_return_5d | float64 | 0 | 0.0% |  |
| log_return_20d | float64 | 0 | 0.0% |  |
| log_return_60d | float64 | 15 | 0.3% |  |
| cum_log_return_30d | float64 | 0 | 0.0% |  |
| cum_log_return_60d | float64 | 15 | 0.3% |  |
| cum_log_return_180d | float64 | 135 | 3.1% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.3% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.1% |  |
| log_price_to_sma_200 | float64 | 154 | 3.5% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 2 | 0.0% |  |
| volume_boxcox | float64 | 0 | 0.0% |  |
| price_momentum_boxcox | float64 | 0 | 0.0% |  |
| rsi_log_odds | float64 | 0 | 0.0% |  |
| stoch_k_log_odds | float64 | 0 | 0.0% |  |
| macd_sigmoid | float64 | 0 | 0.0% |  |
| williams_r_sigmoid | float64 | 0 | 0.0% |  |
| fft_dominant_power_1_60 | float64 | 15 | 0.3% |  |
| fft_dominant_power_2_60 | float64 | 15 | 0.3% |  |
| fft_dominant_freq_1_60 | float64 | 15 | 0.3% |  |
| fft_spectral_centroid_60 | float64 | 15 | 0.3% |  |
| fft_spectral_rolloff_60 | float64 | 15 | 0.3% |  |
| fft_spectral_bandwidth_60 | float64 | 15 | 0.3% |  |
| dct_trend_strength_60 | float64 | 15 | 0.3% |  |
| dct_price_vs_trend_60 | float64 | 15 | 0.3% |  |
| dct_trend_slope_60 | float64 | 15 | 0.3% |  |
| wavelet_energy_scale_2_60 | float64 | 15 | 0.3% |  |
| wavelet_energy_scale_4_60 | float64 | 15 | 0.3% |  |
| wavelet_energy_scale_8_60 | float64 | 15 | 0.3% |  |
| wavelet_energy_scale_16_60 | float64 | 15 | 0.3% |  |
| wavelet_total_energy_60 | float64 | 4383 | 100.0% |  |
| wavelet_entropy_60 | float64 | 4383 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 1.7% |  |
| fft_dominant_power_2_120 | float64 | 75 | 1.7% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 1.7% |  |
| fft_spectral_centroid_120 | float64 | 75 | 1.7% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 1.7% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 1.7% |  |
| dct_trend_strength_120 | float64 | 75 | 1.7% |  |
| dct_price_vs_trend_120 | float64 | 75 | 1.7% |  |
| dct_trend_slope_120 | float64 | 75 | 1.7% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 1.7% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 1.7% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 1.7% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 1.7% |  |
| wavelet_total_energy_120 | float64 | 4383 | 100.0% |  |
| wavelet_entropy_120 | float64 | 4383 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 367 | 8.4% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 1948 | 44.4% |  |
| standing_waves | float64 | 6 | 0.1% |  |
| electric_field | float64 | 0 | 0.0% |  |
| magnetic_field | float64 | 0 | 0.0% |  |
| wave_dispersion | float64 | 15 | 0.3% |  |
| resonance_frequency | float64 | 0 | 0.0% |  |
| random_walk_deviation | float64 | 5 | 0.1% |  |
| diffusion_coefficient | float64 | 0 | 0.0% |  |
| ou_mean_reversion | float64 | 15 | 0.3% |  |
| jump_diffusion | float64 | 0 | 0.0% |  |
| levy_flight_tails | float64 | 0 | 0.0% |  |
| partition_function | float64 | 0 | 0.0% |  |
| growth_future_7d | float64 | 0 | 0.0% |  |
| target | int64 | 0 | 0.0% |  |

## Key Feature Statistics

### close_price
- **Mean**: 22.0275
- **Std**: 28.8336
- **Min**: 0.6604
- **Max**: 159.5150

### volume
- **Mean**: 24545.6785
- **Std**: 46655.1161
- **Min**: 1.0000
- **Max**: 1186674.0000

### growth_1d
- **Mean**: 1.0012
- **Std**: 0.0319
- **Min**: 0.7425
- **Max**: 1.4310

### growth_3d
- **Mean**: 1.0039
- **Std**: 0.0584
- **Min**: 0.5034
- **Max**: 1.9360

### growth_7d
- **Mean**: 1.0094
- **Std**: 0.0900
- **Min**: 0.2776
- **Max**: 1.8350

### growth_14d
- **Mean**: 1.0190
- **Std**: 0.1299
- **Min**: 0.2242
- **Max**: 1.9804

### growth_30d
- **Mean**: 1.0439
- **Std**: 0.2088
- **Min**: 0.1833
- **Max**: 2.7610

### growth_60d
- **Mean**: 1.0916
- **Std**: 0.3088
- **Min**: 0.1862
- **Max**: 3.8889

### growth_90d
- **Mean**: 1.1415
- **Std**: 0.3880
- **Min**: 0.2000
- **Max**: 3.1145

### growth_180d
- **Mean**: 1.3376
- **Std**: 0.7243
- **Min**: 0.1217
- **Max**: 4.1479


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |   obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |    macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |      cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |         obv |    ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|------------:|-------------:|-------------:|------------:|---------:|--------:|--------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|---------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|------------:|-----------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| RBW      | PLN        |        5.0803 |     6111 | 2007-12-12 00:00:00  |   2007 |      12 |         2 |         4 |           346 |             50 |              0 |                1 |             1 |      1.0170 |      1.0360 |      1.0374 |       1.1116 |       0.9250 |          nan |          nan |           nan |           nan |                  -0.0742 |                       nan |  4.9573 |   4.9128 |   4.7298 |      nan |       nan |       nan |   4.8958 |   4.9174 |   5.0038 |            1.0741 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0170 |                 0.0003 |          0.1461 |           0.0079 |           0.1882 |            0.0063 |           0.7027 |            0.0026 |           0.6219 |           -0.0018 |              nan |               nan |              0.1963 |               0.1635 |               1.0000 |                  nan |     6828.6000 |      5700.7000 |      9478.9500 |            nan |             1.0720 |             0.6447 |                nan |                       1 |                       0 |                 80.4071 |                 105.0762 |             745.0000 |             3060.0000 |                  0.7713 |        75805 |  24826.7000 |       4.9951 |       5.2073 |      4.9951 |  55.8575 | 72.4685 | -0.0631 |       -0.1391 |      0.0760 |   66.3426 |   63.1352 |      100.0000 |      100.0000 |     -16.4316 | 24.8298 |   19.8678 |    16.7392 | 150.6068 | 11.7149 |   6.4390 |   3.3245 |        0.3073 | 0.2275 | 4.4776 |     5.0992 |      4.9573 |     4.8154 |     0.0572 |        0.9333 | 152443.0000 | 36045.3009 | 92.7063 |          5.0942 |           5.0907 |         5.1012 |    4.7821 |       nan |     4.7338 |          0 |            0 |               0 |                  0 |                  0 |          0.0169 |          0.0394 |           0.0327 |              nan |              -0.0780 |                  nan |                   nan |              -0.3529 |                  nan |       8.7180 |             9.1569 |                -0.4390 |                0.0715 |                   nan |                    nan |        -2.8604 |           -0.0691 |          8.7180 |                  0.1514 |         0.2354 |             0.6786 |         0.4842 |               0.1620 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.1339 |              nan |              1.0000 |           0.4939 |            0.0270 |               0.0019 |           1.2405 |        0.0021 |         -0.2801 |             0.8522 |                 nan |           0.6696 |           0.1228 |           0.0668 |               nan |                1.8062 |                     nan |                  0.0007 |                 nan |           0.0041 |              3.0486 |               0.0493 |             0.9241 |        0 |
| RBW      | PLN        |        5.0933 |    10837 | 2007-12-13 00:00:00  |   2007 |      12 |         3 |         4 |           347 |             50 |              0 |                1 |             1 |      1.0026 |      1.0387 |      1.0527 |       1.1129 |       0.9165 |          nan |          nan |           nan |           nan |                  -0.0601 |                       nan |  4.9952 |   4.9338 |   4.7703 |      nan |       nan |       nan |   4.9262 |   4.9308 |   5.0080 |            1.0677 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0026 |                 0.0000 |          0.1489 |           0.0077 |           0.1631 |            0.0043 |           0.5026 |            0.0092 |           0.6207 |           -0.0021 |              nan |               nan |              0.1896 |               0.8107 |               1.0000 |                  nan |     8268.8000 |      5725.8000 |      9643.0500 |            nan |             1.8927 |             1.1238 |                nan |                       1 |                       1 |                 83.0512 |                 155.1906 |            7201.0000 |             3282.0000 |                  0.7573 |        86642 |  30193.4000 |       5.0803 |       5.1618 |      5.0145 |  56.3465 | 73.3023 | -0.0429 |       -0.1198 |      0.0769 |   71.3991 |   67.0307 |      100.0000 |      100.0000 |     -14.7400 | 23.6667 |   18.9211 |    15.9416 | 140.7344 | 12.6930 |   4.2865 |  18.9291 |        0.2093 | 0.2217 | 4.3537 |     5.1592 |      4.9952 |     4.8313 |     0.0657 |        0.7992 | 163280.0000 | 36804.7793 | 81.8381 |          5.0899 |           5.0907 |         5.0882 |    4.8280 |       nan |     4.7689 |        100 |            0 |               0 |                  0 |                  0 |          0.0026 |          0.0379 |           0.1734 |              nan |              -0.0872 |                  nan |                   nan |              -0.6879 |                  nan |       9.2908 |             9.1741 |                 0.1167 |                0.0655 |                   nan |                    nan |        -2.7234 |           -0.2242 |          9.2908 |                  0.5937 |         0.2552 |             0.9148 |         0.4893 |               0.1863 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.1753 |              nan |              1.0000 |           0.4939 |            0.0270 |               0.0021 |           1.2442 |       -0.0518 |         -0.2955 |             0.6525 |                 nan |           0.6696 |           0.1242 |           0.0653 |               nan |                1.4886 |                     nan |                  0.0007 |                 nan |           0.0041 |              3.0486 |               0.0463 |             0.9371 |        0 |
| RBW      | PLN        |        5.0999 |    10169 | 2007-12-14 00:00:00  |   2007 |      12 |         4 |         4 |           348 |             50 |              0 |                1 |             1 |      1.0013 |      1.0210 |      1.0442 |       1.1143 |       0.8965 |          nan |          nan |           nan |           nan |                  -0.0701 |                       nan |  5.0345 |   4.9599 |   4.7948 |      nan |       nan |       nan |   4.9530 |   4.9436 |   5.0122 |            1.0636 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0013 |                 0.0000 |          0.1450 |           0.0079 |           0.1461 |            0.0053 |           0.4359 |            0.0054 |           0.6160 |           -0.0029 |              nan |               nan |              0.1962 |               0.4904 |               1.0000 |                  nan |     9322.6000 |      6526.0000 |      9561.0500 |            nan |             1.5582 |             1.0636 |                nan |                       1 |                       1 |                 85.6667 |                 110.7899 |            5269.0000 |            -1640.0000 |                  0.7621 |        96811 |  35478.1000 |       5.0933 |       5.1710 |      5.0269 |  56.6058 | 73.7664 | -0.0261 |       -0.1011 |      0.0750 |   72.3132 |   70.0183 |      100.0000 |      100.0000 |     -13.9970 | 22.6462 |   18.3215 |    15.1794 | 134.9791 | 13.2115 |   5.4062 |  10.6397 |        0.2616 | 0.2162 | 4.2394 |     5.1854 |      5.0345 |     4.8835 |     0.0600 |        0.7167 | 173449.0000 | 36936.7698 | 82.0735 |          5.0993 |           5.0994 |         5.0989 |    4.8692 |       nan |     4.8010 |        100 |            0 |               0 |                  0 |                  0 |          0.0013 |          0.0392 |           0.1011 |              nan |              -0.1092 |                  nan |                   nan |              -0.8304 |                  nan |       9.2272 |             9.1656 |                 0.0616 |                0.0617 |                   nan |                    nan |        -2.8139 |           -0.3331 |          9.2272 |                  0.3991 |         0.2658 |             0.9601 |         0.4935 |               0.1979 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.2554 |              nan |              1.0000 |           0.4939 |            0.0270 |               0.0019 |           1.2399 |       -0.0085 |         -0.4644 |             0.3920 |                 nan |           0.6790 |           0.1210 |           0.0646 |               nan |                1.0094 |                     nan |                  0.0007 |                 nan |           0.0041 |              3.0486 |               0.0432 |             0.9962 |        0 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
