# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:40:51  
**Symbol**: XTB  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 2,255 rows × 193 columns
- **Memory Usage**: 3.43 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: XTB(2255) |
| currency | object | 0 | 0.0% |  | Examples: PLN(2255) |
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
| growth_60d | float64 | 15 | 0.7% |  |
| growth_90d | float64 | 45 | 2.0% |  |
| growth_180d | float64 | 135 | 6.0% |  |
| growth_365d | float64 | 320 | 14.2% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.7% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.2% |  |
| sma_100 | float64 | 54 | 2.4% |  |
| sma_200 | float64 | 154 | 6.8% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.2% |  |
| price_to_sma_200 | float64 | 154 | 6.8% |  |
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
| volatility_60d | float64 | 15 | 0.7% |  |
| return_mean_60d | float64 | 15 | 0.7% |  |
| price_momentum_5d | float64 | 0 | 0.0% |  |
| price_momentum_20d | float64 | 0 | 0.0% |  |
| price_position_20d | float64 | 0 | 0.0% |  |
| price_position_60d | float64 | 14 | 0.6% |  |
| volume_ma_5 | float64 | 0 | 0.0% |  |
| volume_ma_10 | float64 | 0 | 0.0% |  |
| volume_ma_20 | float64 | 0 | 0.0% |  |
| volume_ma_50 | float64 | 4 | 0.2% |  |
| volume_ratio_10d | float64 | 0 | 0.0% |  |
| volume_ratio_20d | float64 | 0 | 0.0% |  |
| volume_ratio_50d | float64 | 4 | 0.2% |  |
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
| bb_position | float64 | 3 | 0.1% |  |
| obv | float64 | 0 | 0.0% |  |
| ad_line | float64 | 0 | 0.0% |  |
| mfi | float64 | 0 | 0.0% |  |
| typical_price | float64 | 0 | 0.0% |  |
| weighted_close | float64 | 0 | 0.0% |  |
| median_price | float64 | 0 | 0.0% |  |
| dema_20 | float64 | 0 | 0.0% |  |
| tema_20 | float64 | 12 | 0.5% |  |
| trima_20 | float64 | 0 | 0.0% |  |
| cdl_doji | int32 | 0 | 0.0% |  |
| cdl_hammer | int32 | 0 | 0.0% |  |
| cdl_engulfing | int32 | 0 | 0.0% |  |
| cdl_morning_star | int32 | 0 | 0.0% |  |
| cdl_evening_star | int32 | 0 | 0.0% |  |
| log_return_1d | float64 | 0 | 0.0% |  |
| log_return_5d | float64 | 0 | 0.0% |  |
| log_return_20d | float64 | 0 | 0.0% |  |
| log_return_60d | float64 | 15 | 0.7% |  |
| cum_log_return_30d | float64 | 0 | 0.0% |  |
| cum_log_return_60d | float64 | 15 | 0.7% |  |
| cum_log_return_180d | float64 | 135 | 6.0% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.7% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.2% |  |
| log_price_to_sma_200 | float64 | 154 | 6.8% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 3 | 0.1% |  |
| volume_boxcox | float64 | 0 | 0.0% |  |
| price_momentum_boxcox | float64 | 0 | 0.0% |  |
| rsi_log_odds | float64 | 0 | 0.0% |  |
| stoch_k_log_odds | float64 | 0 | 0.0% |  |
| macd_sigmoid | float64 | 0 | 0.0% |  |
| williams_r_sigmoid | float64 | 0 | 0.0% |  |
| fft_dominant_power_1_60 | float64 | 15 | 0.7% |  |
| fft_dominant_power_2_60 | float64 | 15 | 0.7% |  |
| fft_dominant_freq_1_60 | float64 | 15 | 0.7% |  |
| fft_spectral_centroid_60 | float64 | 15 | 0.7% |  |
| fft_spectral_rolloff_60 | float64 | 15 | 0.7% |  |
| fft_spectral_bandwidth_60 | float64 | 15 | 0.7% |  |
| dct_trend_strength_60 | float64 | 15 | 0.7% |  |
| dct_price_vs_trend_60 | float64 | 15 | 0.7% |  |
| dct_trend_slope_60 | float64 | 15 | 0.7% |  |
| wavelet_energy_scale_2_60 | float64 | 15 | 0.7% |  |
| wavelet_energy_scale_4_60 | float64 | 15 | 0.7% |  |
| wavelet_energy_scale_8_60 | float64 | 15 | 0.7% |  |
| wavelet_energy_scale_16_60 | float64 | 15 | 0.7% |  |
| wavelet_total_energy_60 | float64 | 2255 | 100.0% |  |
| wavelet_entropy_60 | float64 | 2255 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 3.3% |  |
| fft_dominant_power_2_120 | float64 | 75 | 3.3% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 3.3% |  |
| fft_spectral_centroid_120 | float64 | 75 | 3.3% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 3.3% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 3.3% |  |
| dct_trend_strength_120 | float64 | 75 | 3.3% |  |
| dct_price_vs_trend_120 | float64 | 75 | 3.3% |  |
| dct_trend_slope_120 | float64 | 75 | 3.3% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 3.3% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 3.3% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 3.3% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 3.3% |  |
| wavelet_total_energy_120 | float64 | 2255 | 100.0% |  |
| wavelet_entropy_120 | float64 | 2255 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.2% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 247 | 11.0% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 904 | 40.1% |  |
| standing_waves | float64 | 0 | 0.0% |  |
| electric_field | float64 | 0 | 0.0% |  |
| magnetic_field | float64 | 0 | 0.0% |  |
| wave_dispersion | float64 | 15 | 0.7% |  |
| resonance_frequency | float64 | 0 | 0.0% |  |
| random_walk_deviation | float64 | 5 | 0.2% |  |
| diffusion_coefficient | float64 | 0 | 0.0% |  |
| ou_mean_reversion | float64 | 15 | 0.7% |  |
| jump_diffusion | float64 | 0 | 0.0% |  |
| levy_flight_tails | float64 | 0 | 0.0% |  |
| partition_function | float64 | 0 | 0.0% |  |
| growth_future_7d | float64 | 0 | 0.0% |  |
| target | int64 | 0 | 0.0% |  |

## Key Feature Statistics

### close_price
- **Mean**: 19.1576
- **Std**: 21.6162
- **Min**: 1.7470
- **Max**: 83.9603

### volume
- **Mean**: 370165.7410
- **Std**: 745913.7920
- **Min**: 1.0000
- **Max**: 11862815.0000

### growth_1d
- **Mean**: 1.0015
- **Std**: 0.0317
- **Min**: 0.5974
- **Max**: 1.3578

### growth_3d
- **Mean**: 1.0045
- **Std**: 0.0543
- **Min**: 0.5857
- **Max**: 1.4845

### growth_7d
- **Mean**: 1.0104
- **Std**: 0.0842
- **Min**: 0.6160
- **Max**: 1.7285

### growth_14d
- **Mean**: 1.0208
- **Std**: 0.1233
- **Min**: 0.6268
- **Max**: 2.0542

### growth_30d
- **Mean**: 1.0472
- **Std**: 0.2025
- **Min**: 0.5792
- **Max**: 2.4495

### growth_60d
- **Mean**: 1.1080
- **Std**: 0.3766
- **Min**: 0.4736
- **Max**: 3.9390

### growth_90d
- **Mean**: 1.1846
- **Std**: 0.6158
- **Min**: 0.4389
- **Max**: 7.9033

### growth_180d
- **Mean**: 1.4455
- **Std**: 1.0083
- **Min**: 0.3674
- **Max**: 8.3606


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |    obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |   macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |      cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |          obv |     ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|-------------:|-------------:|-------------:|------------:|---------:|--------:|-------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|---------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-------------:|------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| XTB      | PLN        |        7.8841 |     4719 | 2016-07-11 00:00:00  |   2016 |       7 |         0 |         3 |           193 |             28 |              0 |                0 |             0 |      1.0095 |      1.0234 |      0.9827 |       1.0715 |       0.9965 |          nan |          nan |           nan |           nan |                  -0.0888 |                       nan |  7.7888 |   7.8660 |   7.6434 |      nan |       nan |       nan |   7.7792 |   7.6605 |   7.5592 |            1.0315 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0095 |                 0.0001 |          0.2200 |          -0.0021 |           0.1943 |           -0.0010 |           0.2233 |            0.0041 |           0.2387 |           -0.0000 |              nan |               nan |             -0.0862 |               0.6051 |               0.8376 |                  nan |    54371.8000 |     58534.9000 |     63995.0000 |            nan |             0.0806 |             0.0737 |                nan |                       0 |                       0 |               -759.5564 |                 386.4995 |          -10487.0000 |           -16244.0000 |                  1.0281 |      1354338 | 1330861.1500 |       7.8101 |       7.9467 |      7.8101 |  63.0406 | 61.1206 | 0.1614 |        0.1819 |     -0.0205 |   44.1265 |   27.5537 |      100.0000 |       45.2208 |     -27.7816 | 36.7675 |   32.3626 |    16.2082 |  42.6304 | 26.0813 |  -1.0818 |   8.3133 |       -0.0862 | 0.1678 | 2.1284 |     7.9128 |      7.7888 |     7.6648 |     0.0318 |        0.8840 | 4061881.0000 | 934253.1830 | 67.0703 |          7.8803 |           7.8812 |         7.8784 |    7.8998 |       nan |     7.7096 |          0 |            0 |               0 |                  0 |                  0 |          0.0094 |         -0.0109 |           0.0799 |              nan |              -0.0035 |                  nan |                   nan |              -1.4994 |                  nan |       8.4596 |            11.0666 |                -2.6072 |                0.0310 |                   nan |                    nan |        -3.4469 |           -0.1233 |          8.4596 |                  0.4732 |         0.5340 |            -0.2360 |         0.5403 |               0.0585 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.3633 |              nan |              1.0000 |           1.3755 |            0.0081 |               0.0014 |           1.2355 |        0.0271 |         -0.1590 |             0.0663 |                 nan |           0.7851 |           0.0885 |           0.0585 |               nan |                1.9961 |                     nan |                  0.0003 |                 nan |           0.0016 |              3.5103 |               0.0294 |             0.9502 |        0 |
| XTB      | PLN        |        7.8841 |    40984 | 2016-07-12 00:00:00  |   2016 |       7 |         1 |         3 |           194 |             28 |              0 |                0 |             0 |      1.0000 |      1.0184 |      0.9933 |       1.0599 |       1.0102 |          nan |          nan |           nan |           nan |                  -0.0666 |                       nan |  7.8047 |   7.8632 |   7.6736 |      nan |       nan |       nan |   7.7954 |   7.6775 |   7.5742 |            1.0274 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0000 |                 0.0000 |          0.1458 |           0.0021 |           0.1911 |           -0.0003 |           0.2233 |            0.0041 |           0.2352 |            0.0004 |              nan |               nan |              0.0794 |               0.6051 |               0.8376 |                  nan |    50681.6000 |     56379.4000 |     64453.6000 |            nan |             0.7269 |             0.6359 |                nan |                       0 |                       0 |               -512.5932 |                 386.4995 |          -18451.0000 |             9172.0000 |                  1.0176 |      1354338 | 1339571.2500 |       7.8841 |       7.9312 |      7.8121 |  63.0406 | 61.1206 | 0.1575 |        0.1770 |     -0.0195 |   63.2090 |   43.4629 |      100.0000 |       75.4448 |     -31.2175 | 36.5170 |   30.6721 |    15.3616 |  31.2938 | 26.0813 |  -0.3472 |   8.3133 |       -0.0275 | 0.1643 | 2.0843 |     7.9511 |      7.8047 |     7.6583 |     0.0375 |        0.7711 | 4061881.0000 | 942830.0853 | 62.7130 |          7.8758 |           7.8778 |         7.8716 |    7.9156 |       nan |     7.7499 |        100 |            0 |               0 |                  0 |                  0 |          0.0000 |          0.0101 |           0.0799 |              nan |               0.0101 |                  nan |                   nan |              -1.4994 |                  nan |      10.6210 |            11.0737 |                -0.4528 |                0.0271 |                   nan |                    nan |        -3.2831 |           -0.2600 |         10.6210 |                  0.4732 |         0.5340 |             0.5412 |         0.5393 |               0.0422 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.5082 |              nan |              1.0000 |           1.3755 |            0.0081 |               0.0014 |           1.2444 |        0.0375 |         -0.0154 |             0.0972 |                 nan |           0.8016 |           0.0887 |           0.0587 |               nan |                1.3737 |                     nan |                  0.0002 |                 nan |           0.0016 |              3.5103 |               0.0285 |             0.9758 |        0 |
| XTB      | PLN        |        7.8047 |    67658 | 2016-07-13 00:00:00  |   2016 |       7 |         2 |         3 |           195 |             28 |              0 |                0 |             0 |      0.9899 |      0.9993 |      0.9792 |       1.0345 |       1.0200 |          nan |          nan |           nan |           nan |                  -0.0553 |                       nan |  7.8249 |   7.8564 |   7.7028 |      nan |       nan |       nan |   7.7968 |   7.6872 |   7.5848 |            1.0132 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0101 |                 0.0001 |          0.1277 |           0.0026 |           0.1963 |           -0.0008 |           0.2249 |            0.0040 |           0.2297 |            0.0008 |              nan |               nan |              0.1007 |               0.5841 |               0.7449 |                  nan |    23431.0000 |     57090.9000 |     62491.6500 |            nan |             1.1851 |             1.0827 |                nan |                       1 |                       1 |               -122.5215 |                 395.2598 |         -136253.0000 |           -39239.0000 |                  1.0375 |      1286680 | 1350243.3000 |       7.8841 |       7.8841 |      7.7395 |  58.8691 | 51.9040 | 0.1463 |        0.1709 |     -0.0246 |   65.0587 |   57.4647 |        4.8831 |       68.2944 |     -51.9773 | 35.6250 |   28.7119 |    17.5867 | -33.9801 | 17.7382 |  -0.8723 |   8.0888 |       -0.0687 | 0.1629 | 2.0874 |     7.9330 |      7.8249 |     7.7167 |     0.0276 |        0.4068 | 3994223.0000 | 936187.2456 | 58.0651 |          7.8094 |           7.8082 |         7.8118 |    7.9137 |       nan |     7.7837 |          0 |            0 |             -80 |                  0 |                  0 |         -0.0101 |          0.0130 |           0.0778 |              nan |               0.0198 |                  nan |                   nan |              -1.4923 |                  nan |      11.1222 |            11.0428 |                 0.0794 |                0.0131 |                   nan |                    nan |        -3.5888 |           -0.8995 |         11.1222 |                  0.4600 |         0.3586 |             0.6216 |         0.5365 |               0.0055 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.7630 |              nan |              1.0000 |           1.3755 |            0.0081 |               0.0013 |           1.2166 |        0.0652 |          0.0469 |             0.1843 |                 nan |           0.8016 |           0.0879 |           0.0548 |               nan |                0.9824 |                     nan |                  0.0002 |                 nan |           0.0016 |              3.5103 |               0.0286 |             0.9774 |        0 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
