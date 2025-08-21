# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:53:55  
**Symbol**: CDR  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 7,664 rows × 193 columns
- **Memory Usage**: 11.67 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: CDR(7664) |
| currency | object | 0 | 0.0% |  | Examples: PLN(7664) |
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
| growth_365d | float64 | 320 | 4.2% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.2% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 0.7% |  |
| sma_200 | float64 | 154 | 2.0% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 2.0% |  |
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
| bb_position | float64 | 1 | 0.0% |  |
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
| log_price_to_sma_200 | float64 | 154 | 2.0% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 1 | 0.0% |  |
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
| wavelet_total_energy_60 | float64 | 7664 | 100.0% |  |
| wavelet_entropy_60 | float64 | 7664 | 100.0% |  |
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
| wavelet_total_energy_120 | float64 | 7664 | 100.0% |  |
| wavelet_entropy_120 | float64 | 7664 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 952 | 12.4% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 3440 | 44.9% |  |
| standing_waves | float64 | 6 | 0.1% |  |
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
- **Mean**: 55.5404
- **Std**: 85.2197
- **Min**: 0.6020
- **Max**: 435.1330

### volume
- **Mean**: 356926.2334
- **Std**: 566709.5373
- **Min**: 0.0000
- **Max**: 10632589.0000

### growth_1d
- **Mean**: 1.0011
- **Std**: 0.0355
- **Min**: 0.7605
- **Max**: 1.4750

### growth_3d
- **Mean**: 1.0034
- **Std**: 0.0632
- **Min**: 0.7047
- **Max**: 1.7848

### growth_7d
- **Mean**: 1.0079
- **Std**: 0.0970
- **Min**: 0.5793
- **Max**: 1.7478

### growth_14d
- **Mean**: 1.0162
- **Std**: 0.1425
- **Min**: 0.5480
- **Max**: 2.1064

### growth_30d
- **Mean**: 1.0378
- **Std**: 0.2394
- **Min**: 0.4217
- **Max**: 3.5584

### growth_60d
- **Mean**: 1.0818
- **Std**: 0.3983
- **Min**: 0.2721
- **Max**: 5.2717

### growth_90d
- **Mean**: 1.1338
- **Std**: 0.5521
- **Min**: 0.2432
- **Max**: 7.1557

### growth_180d
- **Mean**: 1.2898
- **Std**: 0.8289
- **Min**: 0.2054
- **Max**: 7.9319


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |   obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |    macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |     cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |         obv |     ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|------------:|-------------:|-------------:|------------:|---------:|--------:|--------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|--------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|------------:|------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| CDR      | PLN        |        6.4468 |    95051 | 1994-10-18 00:00:00  |   1994 |      10 |         1 |         4 |           291 |             42 |              0 |                0 |             0 |      1.0311 |      1.1817 |      0.9971 |       1.2913 |       0.7573 |          nan |          nan |           nan |           nan |                  -0.2941 |                       nan |  6.0375 |   6.1847 |   5.8670 |      nan |       nan |       nan |   6.0948 |   6.2938 |   6.6266 |            1.0988 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0311 |                 0.0010 |          1.1496 |           0.0147 |           0.9714 |            0.0112 |           0.9890 |            0.0014 |           1.0529 |           -0.0071 |              nan |               nan |              0.3890 |              -0.0556 |               0.9751 |                  nan |    93890.6000 |     85978.4000 |     84017.7500 |            nan |             1.1055 |             1.1313 |                nan |                       1 |                       1 |               2187.2263 |                 671.9259 |           37428.0000 |            53397.0000 |                  0.3110 |       246751 | -26357.4000 |       6.2523 |       6.6738 |      6.2523 |  51.8878 | 59.9493 | -0.3632 |       -0.5542 |      0.1910 |   75.6062 |   53.4346 |      100.0000 |       90.2476 |     -15.1435 | 14.7855 |   23.8576 |    24.7517 | 90.5952 |  3.7757 |   9.9511 |  -0.8545 |        0.5835 | 0.5715 | 8.8648 |     6.7047 |      6.0375 |     5.3702 |     0.2210 |        0.8068 | 614337.0000 | 168728.6616 | 72.5403 |          6.4576 |           6.4549 |         6.4631 |    5.6936 |       nan |     5.8568 |          0 |            0 |               0 |                  0 |                  0 |          0.0306 |          0.0622 |          -0.0086 |              nan |              -0.2779 |                  nan |                   nan |              -0.0111 |                  nan |      11.4622 |            11.3388 |                 0.1234 |                0.0942 |                   nan |                    nan |        -1.5094 |           -0.2147 |         11.4622 |                  0.0541 |         0.0755 |             1.1312 |         0.4102 |               0.1803 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.1500 |              nan |              1.0814 |           1.6333 |            0.0067 |               0.0071 |           1.3797 |       -0.0357 |         -0.6163 |             0.2582 |                 nan |           0.6566 |           0.3241 |           0.1841 |               nan |                1.0120 |                     nan |                  0.0026 |                 nan |           0.0000 |              3.5430 |               0.0738 |             0.8190 |        0 |
| CDR      | PLN        |        6.3450 |    46771 | 1994-10-19 00:00:00  |   1994 |      10 |         2 |         4 |           292 |             42 |              0 |                0 |             0 |      0.9842 |      1.0620 |      1.0000 |       1.2709 |       0.7919 |          nan |          nan |           nan |           nan |                  -0.2709 |                       nan |  6.0949 |   6.1746 |   5.8601 |      nan |       nan |       nan |   6.1333 |   6.2977 |   6.6136 |            1.0828 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0158 |                 0.0002 |          1.1676 |           0.0115 |           0.8417 |           -0.0003 |           0.9908 |            0.0008 |           1.0419 |           -0.0057 |              nan |               nan |              0.2872 |              -0.1389 |               0.9183 |                  nan |    93038.6000 |     82169.4000 |     83448.6000 |            nan |             0.5692 |             0.5605 |                nan |                       0 |                       0 |               2039.5026 |                 643.2409 |           -4260.0000 |           -11383.0000 |                  0.3216 |       199980 | -14154.7000 |       6.4468 |       6.5132 |      6.1642 |  50.7242 | 56.6661 | -0.3165 |       -0.5066 |      0.1902 |   82.6191 |   70.1994 |       89.5721 |       96.5240 |     -22.2218 | 14.0293 |   22.7775 |    24.7744 | 62.7171 |  1.4484 |  -1.5792 |  -2.1427 |       -0.1018 | 0.5556 | 8.7565 |     6.8072 |      6.0949 |     5.3826 |     0.2337 |        0.6756 | 567566.0000 | 170423.2247 | 74.9382 |          6.3408 |           6.3419 |         6.3387 |    5.7652 |       nan |     5.9136 |          0 |            0 |               0 |                  0 |                  0 |         -0.0159 |          0.0463 |          -0.0217 |              nan |              -0.2333 |                  nan |                   nan |              -0.0093 |                  nan |      10.7530 |            11.3320 |                -0.5790 |                0.0795 |                   nan |                    nan |        -1.4535 |           -0.3922 |         10.7530 |                  0.1301 |         0.0290 |             1.5589 |         0.4215 |               0.0978 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.2618 |              nan |              1.0676 |           1.3148 |            0.0054 |               0.0070 |           1.3747 |       -0.1006 |         -0.6224 |             0.2838 |                 nan |           0.6566 |           0.3073 |           0.2028 |               nan |                1.3203 |                     nan |                  0.0025 |                 nan |           0.0000 |              3.5430 |               0.0685 |             0.8146 |        0 |
| CDR      | PLN        |        6.2339 |   124649 | 1994-10-20 00:00:00  |   1994 |      10 |         3 |         4 |           293 |             42 |              0 |                0 |             0 |      0.9825 |      0.9971 |      1.0291 |       1.1807 |       0.7974 |          nan |          nan |           nan |           nan |                  -0.1517 |                       nan |  6.2505 |   6.1634 |   5.8795 |      nan |       nan |       nan |   6.1488 |   6.2928 |   6.5961 |            1.0603 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0175 |                 0.0003 |          0.7464 |           0.0279 |           0.8427 |           -0.0005 |           0.9224 |            0.0048 |           1.0410 |           -0.0054 |              nan |               nan |              0.7782 |               0.3892 |               0.8428 |                  nan |    99368.0000 |     84059.1000 |     86331.5500 |            nan |             1.4829 |             1.4438 |                nan |                       1 |                       1 |               3451.7148 |                 864.3080 |           31647.0000 |            57659.0000 |                  0.3249 |        75331 |  -4834.9500 |       6.3450 |       6.4179 |      6.0219 |  49.4214 | 52.9716 | -0.2852 |       -0.4623 |      0.1772 |   75.0456 |   77.7570 |       50.9784 |       80.1835 |     -33.3535 | 13.6018 |   21.5834 |    25.3596 | 25.7765 | -1.1572 |  -1.7514 |   6.6588 |       -0.1111 | 0.5442 | 8.7298 |     6.5654 |      6.2505 |     5.9356 |     0.1008 |        0.4736 | 442917.0000 | 179236.0482 | 66.5406 |          6.2246 |           6.2269 |         6.2199 |    5.8088 |       nan |     5.9698 |          0 |            0 |               0 |                  0 |                  0 |         -0.0177 |          0.1333 |           0.0645 |              nan |              -0.2264 |                  nan |                   nan |              -0.0808 |                  nan |      11.7333 |            11.3660 |                 0.3673 |                0.0585 |                   nan |                    nan |        -2.2951 |           -0.7474 |         11.7333 |                  0.3287 |        -0.0231 |             1.1010 |         0.4292 |               0.0344 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0552 |              nan |              1.0000 |           1.0272 |            0.0067 |               0.0068 |           1.3731 |       -0.0256 |         -0.6303 |             0.2004 |                 nan |           0.6551 |           0.3075 |           0.1968 |               nan |                1.7247 |                     nan |                  0.0025 |                 nan |           0.0000 |              3.5430 |               0.0656 |             0.9123 |        0 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
