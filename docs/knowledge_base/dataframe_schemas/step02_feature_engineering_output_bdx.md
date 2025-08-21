# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:27:19  
**Symbol**: BDX  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable. This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 7,489 rows × 193 columns
- **Memory Usage**: 11.41 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: BDX(7489) |
| currency | object | 0 | 0.0% |  | Examples: PLN(7489) |
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
| growth_365d | float64 | 320 | 4.3% |  |
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
| bb_position | float64 | 2 | 0.0% |  |
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
| log_bb_position | float64 | 2 | 0.0% |  |
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
| wavelet_total_energy_60 | float64 | 7489 | 100.0% |  |
| wavelet_entropy_60 | float64 | 7489 | 100.0% |  |
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
| wavelet_total_energy_120 | float64 | 7489 | 100.0% |  |
| wavelet_entropy_120 | float64 | 7489 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.1% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 988 | 13.2% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 3270 | 43.7% |  |
| standing_waves | float64 | 23 | 0.3% |  |
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
| growth_future_30d | float64 | 0 | 0.0% |  |
| target | int64 | 0 | 0.0% |  |

## Key Feature Statistics

### close_price
- **Mean**: 89.7345
- **Std**: 139.3081
- **Min**: 3.2301
- **Max**: 729.9700

### volume
- **Mean**: 89602.0570
- **Std**: 172061.9129
- **Min**: 0.0000
- **Max**: 2874289.0000

### growth_1d
- **Mean**: 1.0009
- **Std**: 0.0253
- **Min**: 0.8088
- **Max**: 1.2341

### growth_3d
- **Mean**: 1.0029
- **Std**: 0.0443
- **Min**: 0.6974
- **Max**: 1.5308

### growth_7d
- **Mean**: 1.0068
- **Std**: 0.0675
- **Min**: 0.6087
- **Max**: 1.6956

### growth_14d
- **Mean**: 1.0139
- **Std**: 0.0955
- **Min**: 0.5228
- **Max**: 1.7625

### growth_30d
- **Mean**: 1.0307
- **Std**: 0.1438
- **Min**: 0.5297
- **Max**: 2.1648

### growth_60d
- **Mean**: 1.0610
- **Std**: 0.2076
- **Min**: 0.4464
- **Max**: 3.2793

### growth_90d
- **Mean**: 1.0872
- **Std**: 0.2370
- **Min**: 0.4422
- **Max**: 2.4862

### growth_180d
- **Mean**: 1.1749
- **Std**: 0.3590
- **Min**: 0.3180
- **Max**: 3.2588


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |    obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |   macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |      cci |     cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |          obv |      ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_30d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|-------------:|-------------:|-------------:|------------:|---------:|--------:|-------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|---------:|--------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-------------:|-------------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|--------------------:|---------:|
| BDX      | PLN        |        4.8602 |   630936 | 1995-07-28 00:00:00  |   1995 |       7 |         4 |         3 |           209 |             30 |              1 |                0 |             0 |      0.9471 |      1.1258 |      1.4375 |       1.7405 |       1.8721 |          nan |          nan |           nan |           nan |                  -0.3030 |                       nan |  4.5946 |   3.9939 |   3.4014 |      nan |       nan |       nan |   4.0286 |   3.5216 |   3.2538 |            1.4289 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0529 |                 0.0028 |          1.0708 |           0.0471 |           0.8100 |            0.0564 |           0.7304 |            0.0291 |           0.6557 |            0.0219 |              nan |               nan |              0.9659 |               2.0678 |               0.8861 |                  nan |   924532.8000 |    810833.3000 |    487330.4000 |            nan |             0.7781 |             1.2947 |                nan |                       0 |                       1 |              49200.3341 |               23675.3676 |         -482635.0000 |           449550.0000 |                  0.8745 |      8853471 | 3972334.9000 |       5.1317 |       5.1317 |      4.7742 |  82.0618 | 82.0030 | 0.5311 |        0.3226 |      0.2086 |   86.4870 |   91.3323 |        0.0000 |       66.6667 |     -14.4147 | 45.0847 |   61.3566 |     3.4132 | 124.6193 | 64.1236 |  71.2807 |  74.0501 |        2.0226 | 0.2206 | 4.5394 |     5.4460 |      4.5946 |     3.7431 |     0.3706 |        0.6560 | 9960575.0000 | 4045278.7012 | 89.2639 |          4.9220 |           4.9066 |         4.9530 |    4.3111 |       nan |     3.2124 |          0 |            0 |               0 |                  0 |                  0 |         -0.0544 |          0.2216 |           0.5542 |              nan |               0.6271 |                  nan |                   nan |              -0.3141 |                  nan |      13.3550 |            13.0967 |                 0.2583 |                0.3569 |                   nan |                    nan |        -0.9926 |           -0.4216 |         13.3550 |                  1.1210 |         1.5205 |             1.8563 |         0.6297 |               0.1913 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.1809 |              nan |              1.1246 |           0.1021 |            0.0742 |               0.0472 |           0.9229 |        0.6556 |          6.9317 |             0.7132 |                 nan |           0.7445 |           0.1651 |           0.1444 |               nan |                4.2247 |                     nan |                  0.0026 |                 nan |           0.0000 |              3.8129 |               0.1834 |              1.6086 |        1 |
| BDX      | PLN        |        4.3772 |   629281 | 1995-07-31 00:00:00  |   1995 |       7 |         0 |         3 |           212 |             31 |              1 |                0 |             0 |      0.9006 |      0.9236 |      1.1789 |       1.5761 |       1.7470 |          nan |          nan |           nan |           nan |                  -0.3972 |                       nan |  4.6851 |   4.1418 |   3.4769 |      nan |       nan |       nan |   4.0822 |   3.5868 |   3.3058 |            1.2590 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |        -0.0994 |                 0.0099 |          1.5020 |           0.0257 |           1.1228 |            0.0444 |           0.8612 |            0.0227 |           0.7271 |            0.0198 |              nan |               nan |              0.4527 |               1.5094 |               0.6836 |                  nan |   830178.2000 |    819362.2000 |    498587.6500 |            nan |             0.7680 |             1.2621 |                nan |                       0 |                       1 |              34987.7551 |               20002.9674 |         -471773.0000 |           225145.0000 |                  0.8561 |      8224190 | 4265841.3000 |       4.8602 |       4.8602 |      4.2762 |  66.8967 | 60.8655 | 0.5197 |        0.3620 |      0.1577 |   67.6709 |   82.6621 |        0.0000 |       33.3333 |     -33.8106 | 45.3863 |   50.9497 |    17.2983 |  72.8827 | 33.7934 |  51.0365 |  52.6323 |        1.4791 | 0.2466 | 5.6333 |     5.2940 |      4.6851 |     4.0763 |     0.2599 |        0.2471 | 9331294.0000 | 3633646.0198 | 83.1930 |          4.5046 |           4.4727 |         4.5682 |    4.3786 |       nan |     3.3336 |          0 |            0 |               0 |                  0 |                  0 |         -0.1047 |          0.1092 |           0.4229 |              nan |               0.5579 |                  nan |                   nan |              -0.1494 |                  nan |      13.3523 |            13.1195 |                 0.2328 |                0.2303 |                   nan |                    nan |        -1.3474 |           -1.3978 |         13.3523 |                  0.9200 |         0.7035 |             0.7387 |         0.6271 |               0.0329 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.1536 |              nan |              1.0966 |           0.0981 |            0.0958 |               0.0529 |           1.0759 |        0.5456 |          7.8681 |             0.5427 |                 nan |           0.7445 |           0.1567 |           0.1310 |               nan |                2.7153 |                     nan |                  0.0031 |                 nan |           0.0000 |              3.8129 |               0.2025 |              1.8000 |        1 |
| BDX      | PLN        |        4.3772 |   454512 | 1995-08-01 00:00:00  |   1995 |       8 |         1 |         3 |           213 |             31 |              0 |                0 |             0 |      1.0000 |      0.8530 |      1.1240 |       1.5934 |       1.7058 |          nan |          nan |           nan |           nan |                  -0.4694 |                       nan |  4.6972 |   4.2716 |   3.5539 |      nan |       nan |       nan |   4.1276 |   3.6468 |   3.3550 |            1.2317 |               nan |                nan |                 1 |                 0 |                  0 |                    1 |                    0 |         0.0000 |                 0.0000 |          1.3503 |           0.0057 |           1.1382 |            0.0381 |           0.8566 |            0.0233 |           0.7292 |            0.0190 |              nan |               nan |              0.0602 |               1.5397 |               0.6836 |                  nan |   779427.6000 |    787292.1000 |    505525.4000 |            nan |             0.5773 |             0.8991 |                nan |                       0 |                       0 |              20820.5782 |               20169.4989 |         -253753.0000 |           138755.0000 |                  0.8403 |      8224190 | 4575135.5500 |       4.3772 |       4.4972 |      4.2895 |  66.8967 | 60.8655 | 0.5049 |        0.3906 |      0.1143 |   39.8433 |   64.6671 |        0.0000 |        0.0000 |     -34.0582 | 45.6664 |   47.8409 |    16.2428 |  53.8111 | 33.7934 |  42.1531 |  54.2595 |        1.2980 | 0.2438 | 5.5699 |     5.2782 |      4.6972 |     4.1162 |     0.2474 |        0.2246 | 9331294.0000 | 3563114.7980 | 79.4301 |          4.3880 |           4.3853 |         4.3933 |    4.4338 |       nan |     3.4663 |        100 |            0 |               0 |                  0 |                  0 |          0.0000 |          0.0139 |           0.4335 |              nan |               0.5340 |                  nan |                   nan |              -0.1548 |                  nan |      13.0270 |            13.1334 |                -0.1064 |                0.2084 |                   nan |                    nan |        -1.3968 |           -1.4932 |         13.0270 |                  0.9320 |         0.7035 |            -0.4120 |         0.6236 |               0.0321 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.0012 |              nan |              1.0966 |           0.0922 |            0.1039 |               0.0529 |           1.1480 |        0.4013 |          7.5759 |             0.6188 |                 nan |           0.7122 |           0.1856 |           0.1400 |               nan |                2.0974 |                     nan |                  0.0033 |                 nan |           0.0000 |              3.8731 |               0.2106 |              1.7103 |        1 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
