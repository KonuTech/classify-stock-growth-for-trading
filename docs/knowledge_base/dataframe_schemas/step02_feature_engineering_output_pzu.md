# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:38:18  
**Symbol**: PZU  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 3,767 rows × 193 columns
- **Memory Usage**: 5.74 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: PZU(3767) |
| currency | object | 0 | 0.0% |  | Examples: PLN(3767) |
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
| growth_60d | float64 | 15 | 0.4% |  |
| growth_90d | float64 | 45 | 1.2% |  |
| growth_180d | float64 | 135 | 3.6% |  |
| growth_365d | float64 | 320 | 8.5% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.4% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 1.4% |  |
| sma_200 | float64 | 154 | 4.1% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 4.1% |  |
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
| volatility_60d | float64 | 15 | 0.4% |  |
| return_mean_60d | float64 | 15 | 0.4% |  |
| price_momentum_5d | float64 | 0 | 0.0% |  |
| price_momentum_20d | float64 | 0 | 0.0% |  |
| price_position_20d | float64 | 0 | 0.0% |  |
| price_position_60d | float64 | 14 | 0.4% |  |
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
| bb_position | float64 | 0 | 0.0% |  |
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
| log_return_60d | float64 | 15 | 0.4% |  |
| cum_log_return_30d | float64 | 0 | 0.0% |  |
| cum_log_return_60d | float64 | 15 | 0.4% |  |
| cum_log_return_180d | float64 | 135 | 3.6% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.4% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.1% |  |
| log_price_to_sma_200 | float64 | 154 | 4.1% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 0 | 0.0% |  |
| volume_boxcox | float64 | 0 | 0.0% |  |
| price_momentum_boxcox | float64 | 0 | 0.0% |  |
| rsi_log_odds | float64 | 0 | 0.0% |  |
| stoch_k_log_odds | float64 | 0 | 0.0% |  |
| macd_sigmoid | float64 | 0 | 0.0% |  |
| williams_r_sigmoid | float64 | 0 | 0.0% |  |
| fft_dominant_power_1_60 | float64 | 15 | 0.4% |  |
| fft_dominant_power_2_60 | float64 | 15 | 0.4% |  |
| fft_dominant_freq_1_60 | float64 | 15 | 0.4% |  |
| fft_spectral_centroid_60 | float64 | 15 | 0.4% |  |
| fft_spectral_rolloff_60 | float64 | 15 | 0.4% |  |
| fft_spectral_bandwidth_60 | float64 | 15 | 0.4% |  |
| dct_trend_strength_60 | float64 | 15 | 0.4% |  |
| dct_price_vs_trend_60 | float64 | 15 | 0.4% |  |
| dct_trend_slope_60 | float64 | 15 | 0.4% |  |
| wavelet_energy_scale_2_60 | float64 | 15 | 0.4% |  |
| wavelet_energy_scale_4_60 | float64 | 15 | 0.4% |  |
| wavelet_energy_scale_8_60 | float64 | 15 | 0.4% |  |
| wavelet_energy_scale_16_60 | float64 | 15 | 0.4% |  |
| wavelet_total_energy_60 | float64 | 3767 | 100.0% |  |
| wavelet_entropy_60 | float64 | 3767 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 2.0% |  |
| fft_dominant_power_2_120 | float64 | 75 | 2.0% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 2.0% |  |
| fft_spectral_centroid_120 | float64 | 75 | 2.0% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 2.0% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 2.0% |  |
| dct_trend_strength_120 | float64 | 75 | 2.0% |  |
| dct_price_vs_trend_120 | float64 | 75 | 2.0% |  |
| dct_trend_slope_120 | float64 | 75 | 2.0% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 2.0% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 2.0% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 2.0% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 2.0% |  |
| wavelet_total_energy_120 | float64 | 3767 | 100.0% |  |
| wavelet_entropy_120 | float64 | 3767 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 789 | 20.9% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 1305 | 34.6% |  |
| standing_waves | float64 | 3 | 0.1% |  |
| electric_field | float64 | 0 | 0.0% |  |
| magnetic_field | float64 | 0 | 0.0% |  |
| wave_dispersion | float64 | 15 | 0.4% |  |
| resonance_frequency | float64 | 0 | 0.0% |  |
| random_walk_deviation | float64 | 5 | 0.1% |  |
| diffusion_coefficient | float64 | 0 | 0.0% |  |
| ou_mean_reversion | float64 | 15 | 0.4% |  |
| jump_diffusion | float64 | 0 | 0.0% |  |
| levy_flight_tails | float64 | 0 | 0.0% |  |
| partition_function | float64 | 0 | 0.0% |  |
| growth_future_7d | float64 | 0 | 0.0% |  |
| target | int64 | 0 | 0.0% |  |

## Key Feature Statistics

### close_price
- **Mean**: 25.7000
- **Std**: 10.2444
- **Min**: 12.0845
- **Max**: 65.7200

### volume
- **Mean**: 3345498.8612
- **Std**: 2590838.0768
- **Min**: 470158.0000
- **Max**: 43382693.0000

### growth_1d
- **Mean**: 1.0006
- **Std**: 0.0165
- **Min**: 0.8887
- **Max**: 1.0857

### growth_3d
- **Mean**: 1.0016
- **Std**: 0.0274
- **Min**: 0.8489
- **Max**: 1.1627

### growth_7d
- **Mean**: 1.0037
- **Std**: 0.0401
- **Min**: 0.7353
- **Max**: 1.1688

### growth_14d
- **Mean**: 1.0074
- **Std**: 0.0566
- **Min**: 0.6739
- **Max**: 1.2603

### growth_30d
- **Mean**: 1.0159
- **Std**: 0.0840
- **Min**: 0.6586
- **Max**: 1.4146

### growth_60d
- **Mean**: 1.0319
- **Std**: 0.1224
- **Min**: 0.6869
- **Max**: 1.5613

### growth_90d
- **Mean**: 1.0473
- **Std**: 0.1524
- **Min**: 0.6967
- **Max**: 1.6058

### growth_180d
- **Mean**: 1.0950
- **Std**: 0.2357
- **Min**: 0.5176
- **Max**: 1.8646


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |      obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |   macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |     cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |            obv |       ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|---------------:|-------------:|-------------:|------------:|---------:|--------:|-------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|--------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|---------------:|--------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| PZU      | PLN        |       13.7549 |  1069298 | 2010-07-15 00:00:00  |   2010 |       7 |         3 |         3 |           196 |             28 |              0 |                0 |             0 |      1.0000 |      0.9947 |      1.0318 |       1.0420 |       1.0587 |          nan |          nan |           nan |           nan |                  -0.0102 |                       nan | 13.7621 |  13.5043 |  13.3683 |      nan |       nan |       nan |  13.5332 |  13.3529 |  13.2435 |            1.0289 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0000 |                 0.0000 |          0.3040 |           0.0062 |           0.2316 |            0.0040 |           0.2062 |            0.0023 |           0.1959 |            0.0020 |              nan |               nan |              0.4120 |               0.6098 |               0.7150 |                  nan |  3846117.8000 |   4269871.6000 |   5981342.6000 |            nan |             0.2504 |             0.1788 |                nan |                       0 |                       0 |              52527.8931 |               36221.6562 |       -10292091.0000 |         -6961346.0000 |                  1.0546 |    -56106405 | -67776731.9500 |      13.7549 |      13.8559 |     13.6937 |  60.2808 | 63.6831 | 0.1936 |        0.1320 |      0.0617 |   64.4154 |   77.4957 |       25.7869 |       54.0830 |     -32.6577 | 22.6441 |   32.9572 |    14.4058 | 98.5969 | 20.5616 |   3.9290 |   4.6390 |        0.5200 | 0.2599 | 1.8898 |    14.1667 |     13.7621 |    13.3574 |     0.0588 |        0.4912 | 138251291.0000 | 32943592.5069 | 66.4051 |         13.7682 |          13.7648 |        13.7748 |   13.6514 |       nan |    13.2673 |        100 |            0 |               0 |                  0 |                  0 |          0.0000 |          0.0304 |           0.0453 |              nan |               0.0570 |                  nan |                   nan |              -1.5787 |                  nan |      13.8825 |            15.6042 |                -1.7216 |                0.0285 |                   nan |                    nan |        -2.8335 |           -0.7110 |         13.8825 |                  0.4761 |         0.4172 |             0.5934 |         0.5483 |               0.0368 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.2044 |              nan |              1.0000 |           1.3148 |            0.0067 |               0.0004 |           1.2113 |        0.0353 |          0.0442 |             0.5005 |                 nan |           0.6785 |           0.1372 |           0.0817 |               nan |                3.2774 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.0455 |               0.0154 |             1.0492 |        1 |
| PZU      | PLN        |       13.6811 |  1590475 | 2010-07-16 00:00:00  |   2010 |       7 |         4 |         3 |           197 |             28 |              0 |                0 |             0 |      0.9946 |      0.9737 |      1.0280 |       1.0455 |       1.0761 |          nan |          nan |           nan |           nan |                  -0.0175 |                       nan | 13.8142 |  13.5563 |  13.3879 |      nan |       nan |       nan |  13.5560 |  13.3779 |  13.2638 |            1.0219 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0054 |                 0.0000 |          0.3151 |           0.0040 |           0.2314 |            0.0040 |           0.2053 |            0.0015 |           0.1844 |            0.0025 |              nan |               nan |              0.2605 |               0.3906 |               0.6440 |                  nan |  3935882.0000 |   3967021.9000 |   4563317.6000 |            nan |             0.4009 |             0.3485 |                nan |                       0 |                       0 |              49491.5549 |               19230.3625 |          448821.0000 |        -28360500.0000 |                  0.6369 |    -57696880 | -67256449.3000 |      13.7549 |      13.7562 |     13.6029 |  57.9609 | 58.7492 | 0.1913 |        0.1438 |      0.0475 |   46.8240 |   63.3569 |        0.0000 |       20.7496 |     -38.5949 | 23.2854 |   31.5123 |    16.3709 | 64.1827 | 15.9218 |   3.9510 |   2.9389 |        0.5200 | 0.2523 | 1.8443 |    14.0688 |     13.8142 |    13.5595 |     0.0369 |        0.2388 | 136660816.0000 | 32975295.1478 | 66.6391 |         13.6801 |          13.6803 |        13.6796 |   13.6777 |       nan |    13.2967 |          0 |          100 |             -80 |                  0 |                  0 |         -0.0054 |          0.0192 |           0.0290 |              nan |               0.0733 |                  nan |                   nan |              -1.5834 |                  nan |      14.2795 |            15.3336 |                -1.0540 |                0.0217 |                   nan |                    nan |        -3.3003 |           -1.4322 |         14.2795 |                  0.3297 |         0.3212 |            -0.1272 |         0.5477 |               0.0206 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0743 |              nan |              1.0000 |           1.3148 |            0.0067 |               0.0004 |           1.1597 |        0.0385 |          0.0530 |             0.4468 |                 nan |           0.6785 |           0.1148 |           0.0743 |               nan |                1.9887 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.0455 |               0.0157 |             1.0438 |        1 |
| PZU      | PLN        |       13.8931 |  7074919 | 2010-07-19 00:00:00  |   2010 |       7 |         0 |         3 |           200 |             29 |              0 |                0 |             0 |      1.0155 |      1.0100 |      1.0412 |       1.0677 |       1.0992 |          nan |          nan |           nan |           nan |                  -0.0265 |                       nan | 13.8270 |  13.6366 |  13.4044 |      nan |       nan |       nan |  13.6079 |  13.4170 |  13.2927 |            1.0365 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0155 |                 0.0002 |          0.2468 |           0.0010 |           0.2314 |            0.0061 |           0.1999 |            0.0013 |           0.1863 |            0.0032 |              nan |               nan |              0.0643 |               0.3311 |               0.8480 |                  nan |  3982258.4000 |   4609688.8000 |   4452668.7000 |            nan |             1.5348 |             1.5889 |                nan |                       1 |                       1 |              29790.4396 |               15225.2334 |          231882.0000 |         -2212978.0000 |                  0.6188 |    -50621961 | -66846815.5500 |      13.6811 |      13.9820 |     13.6811 |  62.4334 | 67.2522 | 0.2041 |        0.1559 |      0.0483 |   45.8958 |   52.3784 |       37.2337 |       21.0069 |     -21.5395 | 24.5000 |   35.2026 |    14.9826 | 87.8680 | 24.8669 |   6.1385 |   2.4414 |        0.8035 | 0.2558 | 1.8411 |    14.0897 |     13.8270 |    13.5643 |     0.0380 |        0.6258 | 143735735.0000 | 35869817.2821 | 77.3007 |         13.8521 |          13.8623 |        13.8315 |   13.7378 |       nan |    13.3347 |          0 |            0 |              80 |                  0 |                  0 |          0.0154 |          0.0046 |           0.0241 |              nan |               0.0946 |                  nan |                   nan |              -1.6097 |                  nan |      15.7721 |            15.3090 |                 0.4631 |                0.0358 |                   nan |                    nan |        -3.2702 |           -0.4688 |         15.7721 |                  0.2860 |         0.5080 |            -0.1645 |         0.5509 |               0.1040 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.2227 |              nan |              1.0000 |           1.3148 |            0.0067 |               0.0005 |           1.1637 |        0.0254 |          0.1551 |             0.5837 |                 nan |           0.6785 |           0.1147 |           0.0760 |               nan |                0.8033 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.0455 |               0.0153 |             1.0145 |        1 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
