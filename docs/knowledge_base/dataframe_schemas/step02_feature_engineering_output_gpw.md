# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:33:59  
**Symbol**: GPW  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 3,640 rows × 193 columns
- **Memory Usage**: 5.54 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: GPW(3640) |
| currency | object | 0 | 0.0% |  | Examples: PLN(3640) |
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
| growth_180d | float64 | 135 | 3.7% |  |
| growth_365d | float64 | 320 | 8.8% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.4% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.1% |  |
| sma_100 | float64 | 54 | 1.5% |  |
| sma_200 | float64 | 154 | 4.2% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.1% |  |
| price_to_sma_200 | float64 | 154 | 4.2% |  |
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
| cum_log_return_180d | float64 | 135 | 3.7% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.4% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.1% |  |
| log_price_to_sma_200 | float64 | 154 | 4.2% |  |
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
| wavelet_total_energy_60 | float64 | 3640 | 100.0% |  |
| wavelet_entropy_60 | float64 | 3640 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 2.1% |  |
| fft_dominant_power_2_120 | float64 | 75 | 2.1% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 2.1% |  |
| fft_spectral_centroid_120 | float64 | 75 | 2.1% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 2.1% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 2.1% |  |
| dct_trend_strength_120 | float64 | 75 | 2.1% |  |
| dct_price_vs_trend_120 | float64 | 75 | 2.1% |  |
| dct_trend_slope_120 | float64 | 75 | 2.1% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 2.1% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 2.1% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 2.1% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 2.1% |  |
| wavelet_total_energy_120 | float64 | 3640 | 100.0% |  |
| wavelet_entropy_120 | float64 | 3640 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 417 | 11.5% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 1556 | 42.7% |  |
| standing_waves | float64 | 0 | 0.0% |  |
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
- **Mean**: 26.7402
- **Std**: 7.3854
- **Min**: 15.5262
- **Max**: 57.7000

### volume
- **Mean**: 99425.8453
- **Std**: 115352.3531
- **Min**: 4211.0000
- **Max**: 1629739.0000

### growth_1d
- **Mean**: 1.0004
- **Std**: 0.0151
- **Min**: 0.8707
- **Max**: 1.1388

### growth_3d
- **Mean**: 1.0012
- **Std**: 0.0260
- **Min**: 0.8073
- **Max**: 1.1619

### growth_7d
- **Mean**: 1.0026
- **Std**: 0.0378
- **Min**: 0.7359
- **Max**: 1.2050

### growth_14d
- **Mean**: 1.0049
- **Std**: 0.0525
- **Min**: 0.7131
- **Max**: 1.2231

### growth_30d
- **Mean**: 1.0100
- **Std**: 0.0757
- **Min**: 0.7072
- **Max**: 1.3305

### growth_60d
- **Mean**: 1.0186
- **Std**: 0.0976
- **Min**: 0.7341
- **Max**: 1.3740

### growth_90d
- **Mean**: 1.0268
- **Std**: 0.1135
- **Min**: 0.6689
- **Max**: 1.5359

### growth_180d
- **Mean**: 1.0484
- **Std**: 0.1583
- **Min**: 0.6738
- **Max**: 1.6426


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |     obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |    macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |      cci |      cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |           obv |      ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|--------------:|-------------:|-------------:|------------:|---------:|--------:|--------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|---------:|---------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|--------------:|-------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| GPW      | PLN        |       21.3916 |   230495 | 2011-01-14 00:00:00  |   2011 |       1 |         4 |         1 |            14 |              2 |              0 |                0 |             0 |      1.0145 |      1.0293 |      0.9884 |       0.9858 |       0.9444 |          nan |          nan |           nan |           nan |                   0.0025 |                       nan | 21.0291 |  21.2189 |  21.4733 |      nan |       nan |       nan |  21.2943 |  21.5222 |  21.7022 |            0.9962 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |         0.0145 |                 0.0002 |          0.3825 |           0.0026 |           0.2898 |           -0.0008 |           0.2161 |           -0.0014 |           0.1913 |           -0.0018 |              nan |               nan |              0.2523 |              -0.6289 |               0.5945 |                  nan |   426412.6000 |    360602.8000 |    334062.8000 |            nan |             0.6392 |             0.6900 |                nan |                       0 |                       0 |               -679.7143 |                -744.6293 |         -226424.0000 |             2799.0000 |                  0.5705 |     -3061806 | -2171078.1000 |      21.0866 |      21.5561 |     21.0866 |  46.0111 | 52.0026 | -0.2637 |       -0.2630 |     -0.0007 |   74.3416 |   56.3630 |      100.0000 |       92.8682 |     -33.3207 | 29.4164 |   22.4751 |    26.2056 |   7.9043 |  -7.9777 |  -0.9075 |  -2.8560 |       -0.1959 | 0.4322 | 2.0202 |    21.7241 |     21.0291 |    20.3341 |     0.0661 |        0.7608 | 22439916.0000 | 3149832.2138 | 36.9961 |         21.3448 |          21.3565 |        21.3214 |   21.0774 |       nan |    21.4608 |          0 |            0 |              80 |                  0 |                  0 |          0.0144 |          0.0119 |          -0.0290 |              nan |              -0.0572 |                  nan |                   nan |              -1.5320 |                  nan |      12.3480 |            12.7191 |                -0.3711 |               -0.0038 |                   nan |                    nan |        -2.7166 |           -0.2734 |         12.3480 |                  0.4879 |        -0.1599 |             1.0638 |         0.4345 |               0.0345 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0048 |              nan |              1.1103 |           2.0080 |            0.0040 |               0.0003 |           1.2906 |        0.0292 |          0.6409 |             0.1045 |                 nan |           0.7805 |           0.1819 |           0.1077 |               nan |                2.0623 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.6455 |               0.0167 |             0.9786 |        0 |
| GPW      | PLN        |       21.0295 |   152742 | 2011-01-17 00:00:00  |   2011 |       1 |         0 |         1 |            17 |              3 |              0 |                0 |             0 |      0.9831 |      0.9833 |      0.9772 |       0.9801 |       0.9293 |          nan |          nan |           nan |           nan |                  -0.0029 |                       nan | 21.1351 |  21.1912 |  21.4247 |      nan |       nan |       nan |  21.2536 |  21.4847 |  21.6710 |            0.9816 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |        -0.0169 |                 0.0003 |          0.3163 |           0.0053 |           0.2950 |           -0.0012 |           0.2230 |           -0.0022 |           0.1962 |           -0.0024 |              nan |               nan |              0.5300 |              -0.9705 |               0.3642 |                  nan |   387646.6000 |    356820.3000 |    333697.3500 |            nan |             0.4281 |             0.4577 |                nan |                       0 |                       0 |                901.0496 |                -866.4541 |         -193830.0000 |            -7309.0000 |                  0.5722 |     -3214548 | -2287124.5500 |      21.3916 |      21.3916 |     20.8518 |  41.7236 | 43.5526 | -0.2655 |       -0.2635 |     -0.0020 |   64.2548 |   64.8026 |       63.7314 |       80.7786 |     -57.3470 | 28.3889 |   20.4868 |    27.7357 | -56.4293 | -16.5529 |  -1.2987 |  -4.4114 |       -0.2767 | 0.4399 | 2.0916 |    21.5974 |     21.1351 |    20.6728 |     0.0438 |        0.3858 | 22287174.0000 | 3097668.0945 | 37.8444 |         21.0910 |          21.0756 |        21.1217 |   21.0363 |       nan |    21.4121 |          0 |            0 |             -80 |                  0 |                  0 |         -0.0171 |          0.0255 |          -0.0451 |              nan |              -0.0734 |                  nan |                   nan |              -1.5004 |                  nan |      11.9365 |            12.7180 |                -0.7815 |               -0.0186 |                   nan |                    nan |        -3.1293 |           -0.9524 |         11.9365 |                  0.6783 |        -0.3341 |             0.5864 |         0.4340 |               0.0032 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.2230 |              nan |              1.1036 |           2.0080 |            0.0027 |               0.0003 |           1.3320 |        0.0109 |          0.5611 |             0.0593 |                 nan |           0.7712 |           0.1836 |           0.0871 |               nan |                0.6418 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.7558 |               0.0158 |             1.0027 |        1 |
| GPW      | PLN        |       21.1247 |   186619 | 2011-01-18 00:00:00  |   2011 |       1 |         1 |         1 |            18 |              3 |              0 |                0 |             0 |      1.0045 |      1.0018 |      0.9993 |       0.9875 |       0.9398 |          nan |          nan |           nan |           nan |                   0.0118 |                       nan | 21.2037 |  21.1603 |  21.3886 |      nan |       nan |       nan |  21.2337 |  21.4574 |  21.6459 |            0.9877 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |         0.0045 |                 0.0000 |          0.3073 |           0.0034 |           0.2941 |           -0.0013 |           0.2235 |           -0.0016 |           0.1968 |           -0.0020 |              nan |               nan |              0.3430 |              -0.7235 |               0.4296 |                  nan |   354257.2000 |    349576.0000 |    336865.4000 |            nan |             0.5338 |             0.5540 |                nan |                       0 |                       0 |                 96.5622 |                -781.6891 |         -166947.0000 |            63361.0000 |                  0.5574 |     -3027929 | -2387677.1500 |      21.0295 |      21.2758 |     20.9667 |  43.2216 | 46.2324 | -0.2563 |       -0.2620 |      0.0057 |   59.0340 |   65.8768 |       40.8819 |       68.2044 |     -51.0303 | 27.4349 |   19.4271 |    26.3011 | -41.1599 | -13.5568 |  -1.4407 |  -3.3115 |       -0.3088 | 0.4305 | 2.0379 |    21.5121 |     21.2037 |    20.8953 |     0.0291 |        0.3719 | 22473793.0000 | 3101821.6963 | 45.3534 |         21.1224 |          21.1230 |        21.1213 |   21.0199 |       nan |    21.3668 |          0 |            0 |               0 |                  0 |                  0 |          0.0045 |          0.0164 |          -0.0337 |              nan |              -0.0621 |                  nan |                   nan |              -1.4983 |                  nan |      12.1368 |            12.7274 |                -0.5906 |               -0.0124 |                   nan |                    nan |        -3.5374 |           -0.9891 |         12.1368 |                  0.5444 |        -0.2728 |             0.3654 |         0.4363 |               0.0060 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0601 |              nan |              1.1118 |           2.1258 |            0.0027 |               0.0003 |           1.3330 |        0.0246 |          0.5070 |             0.0048 |                 nan |           0.7712 |           0.1873 |           0.0885 |               nan |                1.7556 |                     nan |                  0.0000 |                 nan |           0.0000 |              3.6781 |               0.0152 |             1.0044 |        1 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
