# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:32:18  
**Symbol**: ELT  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 184 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 4,477 rows × 193 columns
- **Memory Usage**: 6.82 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: ELT(4477) |
| currency | object | 0 | 0.0% |  | Examples: PLN(4477) |
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
| growth_180d | float64 | 135 | 3.0% |  |
| growth_365d | float64 | 320 | 7.1% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.3% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 1.2% |  |
| sma_200 | float64 | 154 | 3.4% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 3.4% |  |
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
| bb_position | float64 | 7 | 0.2% |  |
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
| cum_log_return_180d | float64 | 135 | 3.0% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.3% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.1% |  |
| log_price_to_sma_200 | float64 | 154 | 3.4% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 7 | 0.2% |  |
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
| wavelet_total_energy_60 | float64 | 4477 | 100.0% |  |
| wavelet_entropy_60 | float64 | 4477 | 100.0% |  |
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
| wavelet_total_energy_120 | float64 | 4477 | 100.0% |  |
| wavelet_entropy_120 | float64 | 4477 | 100.0% |  |
| lyapunov_exponent | float64 | 8 | 0.2% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 471 | 10.5% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 2079 | 46.4% |  |
| standing_waves | float64 | 16 | 0.4% |  |
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
- **Mean**: 9.1654
- **Std**: 8.8799
- **Min**: 2.4532
- **Max**: 53.0000

### volume
- **Mean**: 20303.3183
- **Std**: 62588.9042
- **Min**: 1.0000
- **Max**: 2139831.0000

### growth_1d
- **Mean**: 1.0006
- **Std**: 0.0280
- **Min**: 0.8111
- **Max**: 1.3729

### growth_3d
- **Mean**: 1.0019
- **Std**: 0.0506
- **Min**: 0.7344
- **Max**: 1.5882

### growth_7d
- **Mean**: 1.0047
- **Std**: 0.0783
- **Min**: 0.5962
- **Max**: 1.5463

### growth_14d
- **Mean**: 1.0094
- **Std**: 0.1092
- **Min**: 0.5320
- **Max**: 1.5150

### growth_30d
- **Mean**: 1.0201
- **Std**: 0.1579
- **Min**: 0.4701
- **Max**: 1.7550

### growth_60d
- **Mean**: 1.0406
- **Std**: 0.2306
- **Min**: 0.4112
- **Max**: 2.1534

### growth_90d
- **Mean**: 1.0588
- **Std**: 0.2783
- **Min**: 0.3674
- **Max**: 2.2405

### growth_180d
- **Mean**: 1.1339
- **Std**: 0.4472
- **Min**: 0.3120
- **Max**: 2.6115


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |   obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |   macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |      cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |          obv |      ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|------------:|-------------:|-------------:|------------:|---------:|--------:|-------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|---------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-------------:|-------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| ELT      | PLN        |       20.1223 |   134545 | 2007-06-18 00:00:00  |   2007 |       6 |         0 |         2 |           169 |             25 |              0 |                1 |             0 |      1.0101 |      1.1772 |      1.2753 |       1.2818 |       1.3780 |          nan |          nan |           nan |           nan |                  -0.0065 |                       nan | 18.4000 |  17.1550 |  16.4206 |      nan |       nan |       nan |  17.4493 |  16.3673 |  15.6810 |            1.2254 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0101 |                 0.0001 |          0.8008 |           0.0498 |           0.6889 |            0.0244 |           0.5201 |            0.0148 |           0.5894 |            0.0114 |              nan |               nan |              4.2679 |               4.9818 |               1.0000 |                  nan |   213278.6000 |    124348.4000 |     84279.9000 |            nan |             1.0820 |             1.5964 |                nan |                       1 |                       1 |              14465.8451 |                3702.5240 |          119649.0000 |            49070.0000 |                  1.1804 |      1485287 | 583707.6500 |      19.9218 |      20.4948 |     19.7241 |  84.4961 | 92.8829 | 1.2363 |        0.8660 |      0.3703 |   92.0087 |   85.1964 |      100.0000 |      100.0000 |      -7.5674 | 37.5205 |   46.7993 |     7.1523 | 192.3153 | 68.9922 |  26.2496 |  32.9038 |        4.1838 | 0.7948 | 3.9497 |    21.7865 |     18.4000 |    15.0136 |     0.3681 |        0.7543 | 3362361.0000 |  650130.8604 | 87.2718 |         20.1137 |          20.1159 |        20.1094 |   18.2283 |       nan |    16.0915 |          0 |            0 |               0 |                  0 |                  0 |          0.0100 |          0.2384 |           0.2845 |              nan |               0.3206 |                  nan |                   nan |              -0.6537 |                  nan |      11.8097 |            11.3419 |                 0.4678 |                0.2033 |                   nan |                    nan |        -0.9994 |           -0.2820 |         11.8097 |                  1.7887 |         1.6956 |             2.4435 |         0.7749 |               0.3194 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0295 |              nan |              1.1406 |           0.2494 |            0.0283 |               0.0054 |           1.1612 |        0.3599 |          0.3597 |             0.5277 |                 nan |           0.7222 |           0.4963 |           0.4461 |               nan |                2.8991 |                     nan |                  0.0004 |                 nan |           0.0032 |              3.0712 |               0.0768 |             1.0821 |        1 |
| ELT      | PLN        |       19.9218 |   251106 | 2007-06-19 00:00:00  |   2007 |       6 |         1 |         2 |           170 |             25 |              0 |                1 |             0 |      0.9900 |      1.0438 |      1.2499 |       1.2438 |       1.4084 |          nan |          nan |           nan |           nan |                   0.0061 |                       nan | 19.2288 |  17.5426 |  16.6467 |      nan |       nan |       nan |  17.8298 |  16.6379 |  15.8772 |            1.1967 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0100 |                 0.0001 |          0.8234 |           0.0488 |           0.7058 |            0.0227 |           0.5274 |            0.0135 |           0.5791 |            0.0121 |              nan |               nan |              4.1437 |               4.5226 |               0.9581 |                  nan |   258769.2000 |    147790.9000 |     95040.5500 |            nan |             1.6991 |             2.6421 |                nan |                       1 |                       1 |              13988.2038 |                3546.7576 |          227453.0000 |           215213.0000 |                  1.1094 |      1234181 | 626895.4000 |      20.1223 |      20.2029 |     19.6405 |  81.6801 | 87.4988 | 1.3421 |        0.9612 |      0.3809 |   91.4978 |   91.6641 |       75.9577 |       91.9859 |     -11.6404 | 39.9056 |   44.3720 |     7.5522 | 132.1477 | 63.3601 |  24.1582 |  29.3691 |        3.8763 | 0.7782 | 3.9061 |    21.4812 |     19.2288 |    16.9763 |     0.2343 |        0.6538 | 3111255.0000 |  650235.7030 | 72.4029 |         19.9217 |          19.9217 |        19.9217 |   18.6713 |       nan |    16.2603 |          0 |          100 |               0 |                  0 |                  0 |         -0.0100 |          0.2332 |           0.2575 |              nan |               0.3424 |                  nan |                   nan |              -0.6398 |                  nan |      12.4336 |            11.4621 |                 0.9716 |                0.1796 |                   nan |                    nan |        -1.4512 |           -0.4249 |         12.4336 |                  1.7088 |         1.4948 |             2.3760 |         0.7928 |               0.2379 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0245 |              nan |              1.1053 |           0.2286 |            0.0324 |               0.0077 |           1.1682 |        0.3277 |          1.0234 |             0.5460 |                 nan |           0.7222 |           0.4734 |           0.4136 |               nan |                1.1256 |                     nan |                  0.0005 |                 nan |           0.0032 |              2.9659 |               0.0839 |             1.1180 |        1 |
| ELT      | PLN        |       21.1170 |  1523813 | 2007-06-20 00:00:00  |   2007 |       6 |         2 |         2 |           171 |             25 |              0 |                1 |             0 |      1.0600 |      1.0600 |      1.3319 |       1.3168 |       1.5151 |          nan |          nan |           nan |           nan |                   0.0151 |                       nan | 20.0336 |  18.0610 |  16.9187 |      nan |       nan |       nan |  18.3357 |  16.9781 |  16.1180 |            1.2481 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0600 |                 0.0036 |          0.7771 |           0.0441 |           0.7069 |            0.0294 |           0.5526 |            0.0155 |           0.5895 |            0.0146 |              nan |               nan |              4.0242 |               5.4387 |               1.0000 |                  nan |   506552.0000 |    299523.4000 |    169313.5000 |            nan |             5.0875 |             8.9999 |                nan |                       1 |                       1 |              27524.5026 |                8083.0266 |         1238914.0000 |          1485459.0000 |                  1.9817 |      2757994 | 744356.1000 |      19.9218 |      21.4905 |     19.9218 |  84.9088 | 91.0905 | 1.5051 |        1.0700 |      0.4351 |   90.5972 |   91.3679 |      100.0000 |       91.9859 |      -6.3103 | 42.5308 |   49.4553 |     6.5341 | 131.4560 | 69.8176 |  32.5362 |  34.6893 |        5.1840 | 0.8346 | 3.9524 |    21.3316 |     20.0336 |    18.7356 |     0.1296 |        0.9173 | 4635068.0000 | 1448472.1949 | 86.3981 |         20.8431 |          20.9116 |        20.7061 |   19.2621 |       nan |    16.4703 |          0 |            0 |              80 |                  0 |                  0 |          0.0583 |          0.2114 |           0.2978 |              nan |               0.4155 |                  nan |                   nan |              -0.5931 |                  nan |      14.2367 |            12.0395 |                 2.1972 |                0.2217 |                   nan |                    nan |        -2.0434 |           -0.0863 |         14.2367 |                  1.8623 |         1.7275 |             2.2654 |         0.8183 |               0.3473 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0176 |              nan |              1.0966 |           0.2270 |            0.0364 |               0.0093 |           1.1783 |        0.3691 |          2.0617 |             0.8738 |                 nan |           0.7222 |           0.4755 |           0.3981 |               nan |                1.3556 |                     nan |                  0.0006 |                 nan |           0.0032 |              2.9514 |               0.0931 |             1.0170 |        1 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
