# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:30:36  
**Symbol**: DVL  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 184 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 4,485 rows × 193 columns
- **Memory Usage**: 6.83 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: DVL(4485) |
| currency | object | 0 | 0.0% |  | Examples: PLN(4485) |
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
| wavelet_total_energy_60 | float64 | 4485 | 100.0% |  |
| wavelet_entropy_60 | float64 | 4485 | 100.0% |  |
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
| wavelet_total_energy_120 | float64 | 4485 | 100.0% |  |
| wavelet_entropy_120 | float64 | 4485 | 100.0% |  |
| lyapunov_exponent | float64 | 3 | 0.1% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 856 | 19.1% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 1768 | 39.4% |  |
| standing_waves | float64 | 2 | 0.0% |  |
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
- **Mean**: 1.5745
- **Std**: 1.5003
- **Min**: 0.2219
- **Max**: 8.7000

### volume
- **Mean**: 863878.8760
- **Std**: 2140767.4622
- **Min**: 2488.0000
- **Max**: 42517837.0000

### growth_1d
- **Mean**: 1.0007
- **Std**: 0.0269
- **Min**: 0.7954
- **Max**: 1.2923

### growth_3d
- **Mean**: 1.0021
- **Std**: 0.0472
- **Min**: 0.7169
- **Max**: 1.4463

### growth_7d
- **Mean**: 1.0049
- **Std**: 0.0716
- **Min**: 0.6154
- **Max**: 1.5202

### growth_14d
- **Mean**: 1.0099
- **Std**: 0.1005
- **Min**: 0.5161
- **Max**: 1.7144

### growth_30d
- **Mean**: 1.0212
- **Std**: 0.1547
- **Min**: 0.3810
- **Max**: 2.0554

### growth_60d
- **Mean**: 1.0428
- **Std**: 0.2320
- **Min**: 0.3404
- **Max**: 2.7594

### growth_90d
- **Mean**: 1.0661
- **Std**: 0.2856
- **Min**: 0.2415
- **Max**: 2.5471

### growth_180d
- **Mean**: 1.1397
- **Std**: 0.4301
- **Min**: 0.1590
- **Max**: 3.6538


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |      obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |    macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |       cci |      cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |          obv |       ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|---------------:|-------------:|-------------:|------------:|---------:|--------:|--------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|----------:|---------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-------------:|--------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| DVL      | PLN        |        1.8273 |   601576 | 2007-09-03 00:00:00  |   2007 |       9 |         0 |         3 |           246 |             36 |              0 |                1 |             0 |      1.0000 |      0.9790 |      1.0269 |       1.0371 |       0.7678 |          nan |          nan |           nan |           nan |                  -0.0102 |                       nan |  1.8351 |   1.8125 |   1.7820 |      nan |       nan |       nan |   1.8193 |   1.8818 |   1.9655 |            1.0254 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0000 |                 0.0000 |          0.4247 |          -0.0039 |           0.3733 |            0.0059 |           0.8418 |           -0.0053 |           0.7141 |           -0.0078 |              nan |               nan |             -0.0392 |              -0.2610 |               0.6001 |                  nan |  1524245.6000 |   2356025.4000 |   3095825.3000 |            nan |             0.2553 |             0.1943 |                nan |                       0 |                       0 |             -24096.8558 |              -11271.6893 |        -1669818.0000 |            85127.0000 |                  0.5434 |    -22267750 | -28060982.0500 |       1.8273 |       1.8821 |      1.7680 |  43.3447 | 50.9215 | -0.0922 |       -0.1284 |      0.0362 |   45.6816 |   51.6242 |       68.4298 |       45.6199 |     -24.3212 | 45.6312 |   12.9943 |    26.6828 |   56.6542 | -13.3105 |   5.7991 | -12.4989 |        0.1002 | 0.1101 | 6.0239 |     1.9033 |      1.8351 |     1.7670 |     0.0742 |        0.4427 | 5872927.0000 | -9318783.5087 | 75.5323 |          1.8258 |           1.8262 |         1.8250 |    1.7123 |       nan |     1.7535 |        100 |            0 |               0 |                  0 |                  0 |          0.0000 |         -0.0212 |          -0.1335 |              nan |              -0.2642 |                  nan |                   nan |              -0.1722 |                  nan |      13.3073 |            14.9456 |                -1.6383 |                0.0251 |                   nan |                    nan |        -2.6004 |           -0.8148 |         13.3073 |                  0.2319 |        -0.2678 |            -0.1732 |         0.4770 |               0.0808 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0622 |              nan |              1.1044 |           1.6631 |            0.0067 |               0.0043 |           1.3440 |        0.0153 |         -0.1504 |             0.1508 |                 nan |           0.8857 |           0.0567 |           0.0486 |               nan |                1.7539 |                     nan |                  0.0011 |                 nan |           0.0000 |              3.6846 |               0.0946 |             0.8857 |        0 |
| DVL      | PLN        |        1.7925 |   968666 | 2007-09-04 00:00:00  |   2007 |       9 |         1 |         3 |           247 |             36 |              0 |                1 |             0 |      0.9809 |      1.0073 |      0.9903 |       1.0326 |       0.7629 |          nan |          nan |           nan |           nan |                  -0.0423 |                       nan |  1.8186 |   1.8199 |   1.7716 |      nan |       nan |       nan |   1.8151 |   1.8750 |   1.9575 |            1.0118 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0191 |                 0.0004 |          0.4279 |          -0.0087 |           0.3911 |            0.0045 |           0.8327 |           -0.0042 |           0.7147 |           -0.0080 |              nan |               nan |             -0.0826 |              -0.2089 |               0.7324 |                  nan |  1441178.6000 |   2302995.2000 |   3075844.1000 |            nan |             0.4206 |             0.3149 |                nan |                       0 |                       0 |             -29070.2127 |               -9345.4005 |         -415335.0000 |          -399624.0000 |                  0.5546 |    -23236416 | -27900003.2500 |       1.8273 |       1.8324 |      1.7354 |  41.3470 | 45.0282 | -0.0875 |       -0.1202 |      0.0327 |   49.6136 |   48.6989 |       31.6094 |       56.1563 |     -33.0812 | 45.0907 |   12.1660 |    27.1196 |    9.4895 | -17.3060 |   4.3032 | -10.4371 |        0.0740 | 0.1091 | 6.0888 |     1.8797 |      1.8186 |     1.7575 |     0.0672 |        0.2858 | 4904261.0000 | -9148112.1571 | 70.0367 |          1.7868 |           1.7882 |         1.7839 |    1.7140 |       nan |     1.7597 |          0 |            0 |             -80 |                  0 |                  0 |         -0.0193 |         -0.0451 |          -0.1102 |              nan |              -0.2706 |                  nan |                   nan |              -0.1831 |                  nan |      13.7837 |            14.9391 |                -1.1554 |                0.0117 |                   nan |                    nan |        -2.7007 |           -1.2524 |         13.7837 |                  0.1897 |        -0.3496 |            -0.0155 |         0.4781 |               0.0353 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0054 |              nan |              1.1136 |           1.9434 |            0.0081 |               0.0029 |           1.3428 |        0.0394 |         -0.2390 |             0.1823 |                 nan |           0.8857 |           0.0573 |           0.0434 |               nan |                1.2225 |                     nan |                  0.0011 |                 nan |           0.0000 |              3.6846 |               0.0873 |             0.9684 |        0 |
| DVL      | PLN        |        1.6881 |  1748287 | 2007-09-05 00:00:00  |   2007 |       9 |         2 |         3 |           248 |             36 |              0 |                1 |             0 |      0.9418 |      0.9238 |      0.9044 |       1.0778 |       0.7476 |          nan |          nan |           nan |           nan |                  -0.1734 |                       nan |  1.7829 |   1.8112 |   1.7640 |      nan |       nan |       nan |   1.7956 |   1.8608 |   1.9451 |            0.9570 |               nan |                nan |                 1 |                 0 |                  0 |                    0 |                    0 |        -0.0582 |                 0.0034 |          0.5481 |          -0.0194 |           0.4661 |           -0.0046 |           0.8090 |           -0.0031 |           0.7241 |           -0.0086 |              nan |               nan |             -0.1784 |              -0.1522 |               0.3945 |                  nan |  1464626.8000 |   2017001.2000 |   3052165.1500 |            nan |             0.8668 |             0.5728 |                nan |                       0 |                       0 |             -47931.8122 |               -5494.4396 |          117241.0000 |          -473579.0000 |                  0.5641 |    -24984703 | -27715345.5000 |       1.7925 |       1.7925 |      1.6385 |  36.0006 | 32.0718 | -0.0913 |       -0.1144 |      0.0232 |   38.6132 |   44.6361 |        0.0000 |       33.3464 |     -65.9590 | 45.2470 |   10.9699 |    30.6449 | -110.0038 | -27.9988 |  -4.8996 |  -8.2694 |       -0.0870 | 0.1123 | 6.6549 |     1.8851 |      1.7829 |     1.6808 |     0.1146 |        0.0357 | 3155974.0000 | -9769754.2632 | 73.3015 |          1.7063 |           1.7018 |         1.7155 |    1.6971 |       nan |     1.7677 |          0 |            0 |               0 |                  0 |                  0 |         -0.0600 |         -0.1005 |          -0.0863 |              nan |              -0.2909 |                  nan |                   nan |              -0.2119 |                  nan |      14.3741 |            14.9314 |                -0.5572 |               -0.0440 |                   nan |                    nan |        -2.1665 |           -3.3319 |         14.3741 |                  0.1417 |        -0.5753 |            -0.4636 |         0.4772 |               0.0014 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.2473 |              nan |              1.1044 |           2.5676 |            0.0067 |               0.0022 |           1.3447 |        0.0923 |         -0.3541 |             0.1544 |                 nan |           0.8889 |           0.0544 |           0.0458 |               nan |                1.3883 |                     nan |                  0.0011 |                 nan |           0.0000 |              3.6846 |               0.0795 |             0.9845 |        0 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
