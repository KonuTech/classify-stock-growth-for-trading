# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:35:37  
**Symbol**: KTY  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 7,335 rows × 193 columns
- **Memory Usage**: 11.17 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: KTY(7335) |
| currency | object | 0 | 0.0% |  | Examples: PLN(7335) |
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
| growth_60d | float64 | 15 | 0.2% |  |
| growth_90d | float64 | 45 | 0.6% |  |
| growth_180d | float64 | 135 | 1.8% |  |
| growth_365d | float64 | 320 | 4.4% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.2% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 0.7% |  |
| sma_200 | float64 | 154 | 2.1% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 2.1% |  |
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
| volatility_60d | float64 | 15 | 0.2% |  |
| return_mean_60d | float64 | 15 | 0.2% |  |
| price_momentum_5d | float64 | 0 | 0.0% |  |
| price_momentum_20d | float64 | 0 | 0.0% |  |
| price_position_20d | float64 | 0 | 0.0% |  |
| price_position_60d | float64 | 14 | 0.2% |  |
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
| bb_position | float64 | 3 | 0.0% |  |
| obv | float64 | 0 | 0.0% |  |
| ad_line | float64 | 0 | 0.0% |  |
| mfi | float64 | 0 | 0.0% |  |
| typical_price | float64 | 0 | 0.0% |  |
| weighted_close | float64 | 0 | 0.0% |  |
| median_price | float64 | 0 | 0.0% |  |
| dema_20 | float64 | 0 | 0.0% |  |
| tema_20 | float64 | 12 | 0.2% |  |
| trima_20 | float64 | 0 | 0.0% |  |
| cdl_doji | int32 | 0 | 0.0% |  |
| cdl_hammer | int32 | 0 | 0.0% |  |
| cdl_engulfing | int32 | 0 | 0.0% |  |
| cdl_morning_star | int32 | 0 | 0.0% |  |
| cdl_evening_star | int32 | 0 | 0.0% |  |
| log_return_1d | float64 | 0 | 0.0% |  |
| log_return_5d | float64 | 0 | 0.0% |  |
| log_return_20d | float64 | 0 | 0.0% |  |
| log_return_60d | float64 | 15 | 0.2% |  |
| cum_log_return_30d | float64 | 0 | 0.0% |  |
| cum_log_return_60d | float64 | 15 | 0.2% |  |
| cum_log_return_180d | float64 | 135 | 1.8% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.2% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.1% |  |
| log_price_to_sma_200 | float64 | 154 | 2.1% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 3 | 0.0% |  |
| volume_boxcox | float64 | 0 | 0.0% |  |
| price_momentum_boxcox | float64 | 0 | 0.0% |  |
| rsi_log_odds | float64 | 0 | 0.0% |  |
| stoch_k_log_odds | float64 | 0 | 0.0% |  |
| macd_sigmoid | float64 | 0 | 0.0% |  |
| williams_r_sigmoid | float64 | 0 | 0.0% |  |
| fft_dominant_power_1_60 | float64 | 15 | 0.2% |  |
| fft_dominant_power_2_60 | float64 | 15 | 0.2% |  |
| fft_dominant_freq_1_60 | float64 | 15 | 0.2% |  |
| fft_spectral_centroid_60 | float64 | 15 | 0.2% |  |
| fft_spectral_rolloff_60 | float64 | 15 | 0.2% |  |
| fft_spectral_bandwidth_60 | float64 | 15 | 0.2% |  |
| dct_trend_strength_60 | float64 | 15 | 0.2% |  |
| dct_price_vs_trend_60 | float64 | 15 | 0.2% |  |
| dct_trend_slope_60 | float64 | 15 | 0.2% |  |
| wavelet_energy_scale_2_60 | float64 | 15 | 0.2% |  |
| wavelet_energy_scale_4_60 | float64 | 15 | 0.2% |  |
| wavelet_energy_scale_8_60 | float64 | 15 | 0.2% |  |
| wavelet_energy_scale_16_60 | float64 | 15 | 0.2% |  |
| wavelet_total_energy_60 | float64 | 7335 | 100.0% |  |
| wavelet_entropy_60 | float64 | 7335 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 1.0% |  |
| fft_dominant_power_2_120 | float64 | 75 | 1.0% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 1.0% |  |
| fft_spectral_centroid_120 | float64 | 75 | 1.0% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 1.0% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 1.0% |  |
| dct_trend_strength_120 | float64 | 75 | 1.0% |  |
| dct_price_vs_trend_120 | float64 | 75 | 1.0% |  |
| dct_trend_slope_120 | float64 | 75 | 1.0% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 1.0% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 1.0% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 1.0% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 1.0% |  |
| wavelet_total_energy_120 | float64 | 7335 | 100.0% |  |
| wavelet_entropy_120 | float64 | 7335 | 100.0% |  |
| lyapunov_exponent | float64 | 5 | 0.1% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 1194 | 16.3% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 2864 | 39.0% |  |
| standing_waves | float64 | 5 | 0.1% |  |
| electric_field | float64 | 0 | 0.0% |  |
| magnetic_field | float64 | 0 | 0.0% |  |
| wave_dispersion | float64 | 15 | 0.2% |  |
| resonance_frequency | float64 | 0 | 0.0% |  |
| random_walk_deviation | float64 | 5 | 0.1% |  |
| diffusion_coefficient | float64 | 0 | 0.0% |  |
| ou_mean_reversion | float64 | 15 | 0.2% |  |
| jump_diffusion | float64 | 0 | 0.0% |  |
| levy_flight_tails | float64 | 0 | 0.0% |  |
| partition_function | float64 | 0 | 0.0% |  |
| growth_future_7d | float64 | 0 | 0.0% |  |
| target | int64 | 0 | 0.0% |  |

## Key Feature Statistics

### close_price
- **Mean**: 150.8200
- **Std**: 194.2917
- **Min**: 6.1292
- **Max**: 862.9700

### volume
- **Mean**: 29761.0769
- **Std**: 78689.2987
- **Min**: 0.0000
- **Max**: 3839702.0000

### growth_1d
- **Mean**: 1.0008
- **Std**: 0.0216
- **Min**: 0.8286
- **Max**: 1.1931

### growth_3d
- **Mean**: 1.0023
- **Std**: 0.0364
- **Min**: 0.7401
- **Max**: 1.3588

### growth_7d
- **Mean**: 1.0053
- **Std**: 0.0552
- **Min**: 0.5476
- **Max**: 1.4452

### growth_14d
- **Mean**: 1.0106
- **Std**: 0.0760
- **Min**: 0.4315
- **Max**: 1.4942

### growth_30d
- **Mean**: 1.0234
- **Std**: 0.1133
- **Min**: 0.3927
- **Max**: 1.6518

### growth_60d
- **Mean**: 1.0482
- **Std**: 0.1664
- **Min**: 0.3460
- **Max**: 1.7793

### growth_90d
- **Mean**: 1.0727
- **Std**: 0.2077
- **Min**: 0.3039
- **Max**: 1.9367

### growth_180d
- **Mean**: 1.1523
- **Std**: 0.3275
- **Min**: 0.3505
- **Max**: 2.4745


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |    obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |   macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |       cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |          obv |      ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|-------------:|-------------:|-------------:|------------:|---------:|--------:|-------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|----------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-------------:|-------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| KTY      | PLN        |       15.4197 |    17706 | 1996-04-02 00:00:00  |   1996 |       4 |         1 |         2 |            93 |             14 |              0 |                0 |             0 |      0.9892 |      0.9872 |      0.9748 |       1.0742 |       1.3042 |          nan |          nan |           nan |           nan |                  -0.0993 |                       nan | 15.5400 |  15.6229 |  15.0749 |      nan |       nan |       nan |  15.3211 |  14.6516 |  14.0102 |            1.0229 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0108 |                 0.0001 |          0.1423 |          -0.0008 |           0.2479 |            0.0012 |           0.5509 |            0.0063 |           0.5000 |            0.0094 |              nan |               nan |             -0.0670 |               1.6641 |               0.7697 |                  nan |    20689.2000 |     79824.8000 |     71461.9500 |            nan |             0.2218 |             0.2478 |                nan |                       0 |                       0 |                 12.1654 |                 291.4438 |            3246.0000 |          -122499.0000 |                  0.9642 |      1234502 | 1386963.6000 |      15.5873 |      15.7220 |     15.2178 |  65.8183 | 56.3850 | 0.8577 |        0.9792 |     -0.1214 |   48.6647 |   49.6344 |        0.0000 |       20.5640 |     -32.2126 | 62.1565 |   31.5324 |    10.3642 |   19.7529 | 31.6367 |   1.0849 |  12.0976 |        0.1655 | 0.5994 | 3.8870 |    15.7410 |     15.5400 |    15.3390 |     0.0259 |        0.2007 | 1557276.0000 | 1184169.6605 | 37.1447 |         15.4532 |          15.4448 |        15.4699 |   16.1034 |       nan |    15.1211 |          0 |            0 |               0 |                  0 |                  0 |         -0.0108 |         -0.0043 |           0.1142 |              nan |               0.2656 |                  nan |                   nan |              -0.5963 |                  nan |       9.7817 |            11.1769 |                -1.3953 |                0.0226 |                   nan |                    nan |        -3.6548 |           -1.6060 |          9.7817 |                  0.9799 |         0.6552 |            -0.0534 |         0.7022 |               0.0384 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.1147 |              nan |              1.0796 |           0.4641 |            0.0256 |               0.0023 |           0.9689 |        0.2242 |         -0.2105 |             0.6522 |                 nan |           0.6369 |           0.3249 |           0.1627 |               nan |                0.4795 |                     nan |                  0.0007 |                 nan |           0.0055 |              3.5773 |               0.0863 |             0.9850 |        0 |
| KTY      | PLN        |       15.2542 |    22747 | 1996-04-03 00:00:00  |   1996 |       4 |         2 |         2 |            94 |             14 |              0 |                0 |             0 |      0.9893 |      0.9744 |      0.9684 |       1.0752 |       1.2902 |          nan |          nan |           nan |           nan |                  -0.1068 |                       nan | 15.5069 |  15.5665 |  15.1283 |      nan |       nan |       nan |  15.3108 |  14.6975 |  14.0678 |            1.0083 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0107 |                 0.0001 |          0.1586 |          -0.0021 |           0.1524 |           -0.0036 |           0.5457 |            0.0042 |           0.5028 |            0.0090 |              nan |               nan |             -0.1655 |               1.0674 |               0.6740 |                  nan |    22061.8000 |     69653.5000 |     68850.5500 |            nan |             0.3266 |             0.3304 |                nan |                       0 |                       0 |                -22.9197 |                 161.7236 |            6863.0000 |           -52228.0000 |                  1.0130 |      1211755 | 1377013.0500 |      15.4197 |      15.4769 |     15.0528 |  62.8172 | 49.5176 | 0.7893 |        0.9412 |     -0.1519 |   35.7086 |   46.0237 |        0.0000 |        9.5358 |     -44.1567 | 60.8056 |   29.8959 |    11.8455 |  -35.1971 | 25.6344 |  -3.5649 |   7.5239 |       -0.5639 | 0.5868 | 3.8471 |    15.8066 |     15.5069 |    15.2073 |     0.0386 |        0.0783 | 1534529.0000 | 1183029.6688 | 37.7774 |         15.2613 |          15.2595 |        15.2648 |   16.0573 |       nan |    15.2156 |          0 |            0 |               0 |                  0 |                  0 |         -0.0108 |         -0.0108 |           0.0725 |              nan |               0.2548 |                  nan |                   nan |              -0.6057 |                  nan |      10.0322 |            11.1397 |                -1.1075 |                0.0083 |                   nan |                    nan |        -3.2533 |           -2.5472 |         10.0322 |                  0.7263 |         0.5244 |            -0.5880 |         0.6877 |               0.0119 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0287 |              nan |              1.0703 |           0.4114 |            0.0243 |               0.0019 |           0.9933 |        0.2245 |         -0.2645 |             0.9462 |                 nan |           0.6369 |           0.3310 |           0.1636 |               nan |                0.6845 |                     nan |                  0.0007 |                 nan |           0.0055 |              3.5773 |               0.0797 |             1.0108 |        1 |
| KTY      | PLN        |       15.0874 |    26675 | 1996-04-04 00:00:00  |   1996 |       4 |         3 |         2 |            95 |             14 |              0 |                0 |             0 |      0.9891 |      0.9679 |      0.9742 |       1.0536 |       1.2412 |          nan |          nan |           nan |           nan |                  -0.0794 |                       nan | 15.4006 |  15.5098 |  15.1017 |      nan |       nan |       nan |  15.2764 |  14.7271 |  14.1146 |            0.9991 |               nan |                nan |                 1 |                 0 |                  0 |                    0 |                    0 |        -0.0109 |                 0.0001 |          0.0927 |          -0.0069 |           0.1532 |           -0.0036 |           0.4103 |           -0.0014 |           0.5026 |            0.0077 |              nan |               nan |             -0.5318 |              -0.5318 |               0.5776 |                  nan |    22255.8000 |     48405.6000 |     66248.6000 |            nan |             0.5511 |             0.4027 |                nan |                       0 |                       0 |               -147.7705 |                -250.2367 |             970.0000 |           -52039.0000 |                  1.0616 |      1185080 | 1361793.0500 |      15.2542 |      15.2855 |     14.9668 |  59.8549 | 43.3146 | 0.7134 |        0.8957 |     -0.1822 |   22.0521 |   35.4751 |        0.0000 |       -0.0000 |     -58.1272 | 59.2809 |   28.6912 |    12.4548 | -105.6325 | 19.7098 |  -3.6208 |  -3.4048 |       -0.5668 | 0.5677 | 3.7627 |    15.8192 |     15.4006 |    14.9819 |     0.0544 |        0.1260 | 1507854.0000 | 1176540.5418 | 35.9074 |         15.1132 |          15.1068 |        15.1262 |   15.9821 |       nan |    15.2901 |          0 |            0 |               0 |                  0 |                  0 |         -0.0110 |         -0.0346 |          -0.0346 |              nan |               0.2161 |                  nan |                   nan |              -0.8910 |                  nan |      10.1915 |            11.1012 |                -0.9097 |               -0.0009 |                   nan |                    nan |        -2.9120 |           -2.0717 |         10.1915 |                  0.4264 |         0.3994 |            -1.2626 |         0.6712 |               0.0030 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.3401 |              nan |              1.0703 |           0.3775 |            0.0162 |               0.0017 |           1.0018 |        0.1768 |         -0.2495 |             0.2149 |                 nan |           0.6207 |           0.3261 |           0.1578 |               nan |                0.8153 |                     nan |                  0.0006 |                 nan |           0.0055 |              3.5773 |               0.0739 |             1.0220 |        1 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
