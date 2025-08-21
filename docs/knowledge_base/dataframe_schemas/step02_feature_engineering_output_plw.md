# Step02 Feature Engineering Output DataFrame Schema

**Generated**: 2025-08-20 18:36:59  
**Symbol**: PLW  
**Pipeline Step**: Feature Engineering  
**Description**: STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with 183 engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.

## Overview

- **Shape**: 2,155 rows × 193 columns
- **Memory Usage**: 3.28 MB
- **Total Features**: 190
- **Technical Indicators**: 33

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
| symbol | object | 0 | 0.0% |  | Examples: PLW(2155) |
| currency | object | 0 | 0.0% |  | Examples: PLN(2155) |
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
| growth_90d | float64 | 45 | 2.1% |  |
| growth_180d | float64 | 135 | 6.3% |  |
| growth_365d | float64 | 320 | 14.8% |  |
| growth_acceleration_7d | float64 | 0 | 0.0% |  |
| growth_acceleration_30d | float64 | 15 | 0.7% |  |
| sma_5 | float64 | 0 | 0.0% |  |
| sma_10 | float64 | 0 | 0.0% |  |
| sma_20 | float64 | 0 | 0.0% |  |
| sma_50 | float64 | 4 | 0.2% |  |
| sma_100 | float64 | 54 | 2.5% |  |
| sma_200 | float64 | 154 | 7.1% |  |
| ema_12 | float64 | 0 | 0.0% |  |
| ema_26 | float64 | 0 | 0.0% |  |
| ema_50 | float64 | 0 | 0.0% |  |
| price_to_sma_20 | float64 | 0 | 0.0% |  |
| price_to_sma_50 | float64 | 4 | 0.2% |  |
| price_to_sma_200 | float64 | 154 | 7.1% |  |
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
| bb_position | float64 | 0 | 0.0% |  |
| obv | float64 | 0 | 0.0% |  |
| ad_line | float64 | 0 | 0.0% |  |
| mfi | float64 | 0 | 0.0% |  |
| typical_price | float64 | 0 | 0.0% |  |
| weighted_close | float64 | 0 | 0.0% |  |
| median_price | float64 | 0 | 0.0% |  |
| dema_20 | float64 | 0 | 0.0% |  |
| tema_20 | float64 | 12 | 0.6% |  |
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
| cum_log_return_180d | float64 | 135 | 6.3% |  |
| log_volatility_20d | float64 | 0 | 0.0% |  |
| log_volatility_60d | float64 | 15 | 0.7% |  |
| log_volume | float64 | 0 | 0.0% |  |
| log_volume_ma_20 | float64 | 0 | 0.0% |  |
| log_volume_ratio_20d | float64 | 0 | 0.0% |  |
| log_price_to_sma_20 | float64 | 0 | 0.0% |  |
| log_price_to_sma_50 | float64 | 4 | 0.2% |  |
| log_price_to_sma_200 | float64 | 154 | 7.1% |  |
| log_bb_width | float64 | 0 | 0.0% |  |
| log_bb_position | float64 | 0 | 0.0% |  |
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
| wavelet_total_energy_60 | float64 | 2155 | 100.0% |  |
| wavelet_entropy_60 | float64 | 2155 | 100.0% |  |
| fft_dominant_power_1_120 | float64 | 75 | 3.5% |  |
| fft_dominant_power_2_120 | float64 | 75 | 3.5% |  |
| fft_dominant_freq_1_120 | float64 | 75 | 3.5% |  |
| fft_spectral_centroid_120 | float64 | 75 | 3.5% |  |
| fft_spectral_rolloff_120 | float64 | 75 | 3.5% |  |
| fft_spectral_bandwidth_120 | float64 | 75 | 3.5% |  |
| dct_trend_strength_120 | float64 | 75 | 3.5% |  |
| dct_price_vs_trend_120 | float64 | 75 | 3.5% |  |
| dct_trend_slope_120 | float64 | 75 | 3.5% |  |
| wavelet_energy_scale_2_120 | float64 | 75 | 3.5% |  |
| wavelet_energy_scale_4_120 | float64 | 75 | 3.5% |  |
| wavelet_energy_scale_8_120 | float64 | 75 | 3.5% |  |
| wavelet_energy_scale_16_120 | float64 | 75 | 3.5% |  |
| wavelet_total_energy_120 | float64 | 2155 | 100.0% |  |
| wavelet_entropy_120 | float64 | 2155 | 100.0% |  |
| lyapunov_exponent | float64 | 0 | 0.0% |  |
| hurst_exponent | float64 | 5 | 0.2% |  |
| fractal_dimension | float64 | 0 | 0.0% |  |
| sample_entropy | float64 | 261 | 12.1% |  |
| recurrence_rate | float64 | 0 | 0.0% |  |
| market_temperature | float64 | 0 | 0.0% |  |
| market_entropy | float64 | 0 | 0.0% |  |
| free_energy | float64 | 0 | 0.0% |  |
| heat_capacity | float64 | 0 | 0.0% |  |
| phase_transition | float64 | 0 | 0.0% |  |
| wave_interference | float64 | 896 | 41.6% |  |
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
- **Mean**: 232.7588
- **Std**: 120.7937
- **Min**: 30.8733
- **Max**: 507.3200

### volume
- **Mean**: 9984.2919
- **Std**: 18829.4679
- **Min**: 3.0000
- **Max**: 289101.0000

### growth_1d
- **Mean**: 1.0014
- **Std**: 0.0292
- **Min**: 0.7748
- **Max**: 1.2271

### growth_3d
- **Mean**: 1.0041
- **Std**: 0.0495
- **Min**: 0.6360
- **Max**: 1.3544

### growth_7d
- **Mean**: 1.0094
- **Std**: 0.0745
- **Min**: 0.5785
- **Max**: 1.5226

### growth_14d
- **Mean**: 1.0190
- **Std**: 0.1082
- **Min**: 0.5051
- **Max**: 1.7176

### growth_30d
- **Mean**: 1.0406
- **Std**: 0.1556
- **Min**: 0.6393
- **Max**: 2.1879

### growth_60d
- **Mean**: 1.0827
- **Std**: 0.2268
- **Min**: 0.6242
- **Max**: 2.4138

### growth_90d
- **Mean**: 1.1281
- **Std**: 0.2947
- **Min**: 0.5727
- **Max**: 2.6605

### growth_180d
- **Mean**: 1.2839
- **Std**: 0.5261
- **Min**: 0.5020
- **Max**: 3.1471


## Sample Data (First 3 Rows)

| symbol   | currency   |   close_price |   volume | trading_date_local   |   year |   month |   weekday |   quarter |   day_of_year |   week_of_year |   is_month_end |   is_quarter_end |   is_year_end |   growth_1d |   growth_3d |   growth_7d |   growth_14d |   growth_30d |   growth_60d |   growth_90d |   growth_180d |   growth_365d |   growth_acceleration_7d |   growth_acceleration_30d |   sma_5 |   sma_10 |   sma_20 |   sma_50 |   sma_100 |   sma_200 |   ema_12 |   ema_26 |   ema_50 |   price_to_sma_20 |   price_to_sma_50 |   price_to_sma_200 |   sma_10_above_20 |   sma_20_above_50 |   sma_50_above_200 |   price_above_sma_20 |   price_above_sma_50 |   daily_return |   daily_return_squared |   volatility_5d |   return_mean_5d |   volatility_10d |   return_mean_10d |   volatility_20d |   return_mean_20d |   volatility_30d |   return_mean_30d |   volatility_60d |   return_mean_60d |   price_momentum_5d |   price_momentum_20d |   price_position_20d |   price_position_60d |   volume_ma_5 |   volume_ma_10 |   volume_ma_20 |   volume_ma_50 |   volume_ratio_10d |   volume_ratio_20d |   volume_ratio_50d |   volume_increasing_10d |   volume_increasing_20d |   price_volume_trend_5d |   price_volume_trend_20d |   volume_momentum_5d |   volume_momentum_20d |   volume_volatility_20d |   obv_approx |   obv_ma_20 |   open_price |   high_price |   low_price |   rsi_14 |   rsi_7 |    macd |   macd_signal |   macd_hist |   stoch_k |   stoch_d |   stoch_rsi_k |   stoch_rsi_d |   williams_r |     adx |   plus_di |   minus_di |       cci |      cmo |   roc_10 |   roc_20 |   momentum_10 |    atr |   natr |   bb_upper |   bb_middle |   bb_lower |   bb_width |   bb_position |        obv |    ad_line |     mfi |   typical_price |   weighted_close |   median_price |   dema_20 |   tema_20 |   trima_20 |   cdl_doji |   cdl_hammer |   cdl_engulfing |   cdl_morning_star |   cdl_evening_star |   log_return_1d |   log_return_5d |   log_return_20d |   log_return_60d |   cum_log_return_30d |   cum_log_return_60d |   cum_log_return_180d |   log_volatility_20d |   log_volatility_60d |   log_volume |   log_volume_ma_20 |   log_volume_ratio_20d |   log_price_to_sma_20 |   log_price_to_sma_50 |   log_price_to_sma_200 |   log_bb_width |   log_bb_position |   volume_boxcox |   price_momentum_boxcox |   rsi_log_odds |   stoch_k_log_odds |   macd_sigmoid |   williams_r_sigmoid |   fft_dominant_power_1_60 |   fft_dominant_power_2_60 |   fft_dominant_freq_1_60 |   fft_spectral_centroid_60 |   fft_spectral_rolloff_60 |   fft_spectral_bandwidth_60 |   dct_trend_strength_60 |   dct_price_vs_trend_60 |   dct_trend_slope_60 |   wavelet_energy_scale_2_60 |   wavelet_energy_scale_4_60 |   wavelet_energy_scale_8_60 |   wavelet_energy_scale_16_60 |   wavelet_total_energy_60 |   wavelet_entropy_60 |   fft_dominant_power_1_120 |   fft_dominant_power_2_120 |   fft_dominant_freq_1_120 |   fft_spectral_centroid_120 |   fft_spectral_rolloff_120 |   fft_spectral_bandwidth_120 |   dct_trend_strength_120 |   dct_price_vs_trend_120 |   dct_trend_slope_120 |   wavelet_energy_scale_2_120 |   wavelet_energy_scale_4_120 |   wavelet_energy_scale_8_120 |   wavelet_energy_scale_16_120 |   wavelet_total_energy_120 |   wavelet_entropy_120 |   lyapunov_exponent |   hurst_exponent |   fractal_dimension |   sample_entropy |   recurrence_rate |   market_temperature |   market_entropy |   free_energy |   heat_capacity |   phase_transition |   wave_interference |   standing_waves |   electric_field |   magnetic_field |   wave_dispersion |   resonance_frequency |   random_walk_deviation |   diffusion_coefficient |   ou_mean_reversion |   jump_diffusion |   levy_flight_tails |   partition_function |   growth_future_7d |   target |
|:---------|:-----------|--------------:|---------:|:---------------------|-------:|--------:|----------:|----------:|--------------:|---------------:|---------------:|-----------------:|--------------:|------------:|------------:|------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|-------------------------:|--------------------------:|--------:|---------:|---------:|---------:|----------:|----------:|---------:|---------:|---------:|------------------:|------------------:|-------------------:|------------------:|------------------:|-------------------:|---------------------:|---------------------:|---------------:|-----------------------:|----------------:|-----------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|-----------------:|------------------:|--------------------:|---------------------:|---------------------:|---------------------:|--------------:|---------------:|---------------:|---------------:|-------------------:|-------------------:|-------------------:|------------------------:|------------------------:|------------------------:|-------------------------:|---------------------:|----------------------:|------------------------:|-------------:|------------:|-------------:|-------------:|------------:|---------:|--------:|--------:|--------------:|------------:|----------:|----------:|--------------:|--------------:|-------------:|--------:|----------:|-----------:|----------:|---------:|---------:|---------:|--------------:|-------:|-------:|-----------:|------------:|-----------:|-----------:|--------------:|-----------:|-----------:|--------:|----------------:|-----------------:|---------------:|----------:|----------:|-----------:|-----------:|-------------:|----------------:|-------------------:|-------------------:|----------------:|----------------:|-----------------:|-----------------:|---------------------:|---------------------:|----------------------:|---------------------:|---------------------:|-------------:|-------------------:|-----------------------:|----------------------:|----------------------:|-----------------------:|---------------:|------------------:|----------------:|------------------------:|---------------:|-------------------:|---------------:|---------------------:|--------------------------:|--------------------------:|-------------------------:|---------------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|---------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------:|---------------------------:|---------------------------:|--------------------------:|----------------------------:|---------------------------:|-----------------------------:|-------------------------:|-------------------------:|----------------------:|-----------------------------:|-----------------------------:|-----------------------------:|------------------------------:|---------------------------:|----------------------:|--------------------:|-----------------:|--------------------:|-----------------:|------------------:|---------------------:|-----------------:|--------------:|----------------:|-------------------:|--------------------:|-----------------:|-----------------:|-----------------:|------------------:|----------------------:|------------------------:|------------------------:|--------------------:|-----------------:|--------------------:|---------------------:|-------------------:|---------:|
| PLW      | PLN        |       33.1307 |     1288 | 2016-12-23 00:00:00  |   2016 |      12 |         4 |         4 |           358 |             51 |              0 |                1 |             1 |      1.0050 |      0.9638 |      0.9439 |       0.9526 |       0.9122 |          nan |          nan |           nan |           nan |                  -0.0087 |                       nan | 33.6348 |  34.2865 |  34.7685 |      nan |       nan |       nan |  34.1438 |  34.5591 |  34.8335 |            0.9529 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |         0.0050 |                 0.0000 |          0.3014 |          -0.0073 |           0.2804 |           -0.0066 |           0.2978 |           -0.0006 |           0.3373 |           -0.0028 |              nan |               nan |             -1.2534 |              -0.5297 |               0.0577 |                  nan |     2028.6000 |      1385.9000 |      1506.1000 |            nan |             0.9294 |             0.8552 |                nan |                       0 |                       0 |                 -5.1613 |                  18.5653 |             298.0000 |              156.0000 |                  1.3959 |        -5989 |  -9383.3000 |      32.9663 |      33.4819 |     32.7779 |  38.0842 | 29.6409 | -0.5727 |       -0.4119 |     -0.1608 |   17.9911 |   20.9987 |       14.7682 |        4.9227 |     -81.7291 | 20.3028 |   14.0468 |    29.9260 | -142.4622 | -23.8317 |  -6.5432 |  -1.5737 |       -2.3196 | 0.9736 | 2.9387 |    35.1018 |     33.6348 |    32.1678 |     0.0872 |        0.3282 | 72602.0000 | 19016.7200 | 67.6647 |         33.1301 |          33.1303 |        33.1299 |   33.9248 |       nan |    35.0502 |          0 |            0 |              80 |                  0 |                  0 |          0.0050 |         -0.0371 |          -0.0159 |              nan |              -0.0919 |                  nan |                   nan |              -1.2113 |                  nan |       7.1616 |             7.3179 |                -0.1564 |               -0.0483 |                   nan |                    nan |        -2.4392 |           -1.1142 |          7.1616 |                  0.4251 |        -0.4860 |            -1.5170 |         0.3606 |               0.0003 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |              0.1539 |              nan |              1.0000 |           1.8745 |            0.0135 |               0.0006 |           1.3255 |       -0.0222 |         -0.4921 |             0.4364 |                 nan |           0.7398 |           0.5341 |           0.3290 |               nan |                1.3385 |                     nan |                  0.0003 |                 nan |           0.0000 |              3.5969 |               0.0243 |             1.0162 |        1 |
| PLW      | PLN        |       33.8537 |     2227 | 2016-12-27 00:00:00  |   2016 |      12 |         1 |         4 |           362 |             52 |              1 |                1 |             1 |      1.0218 |      1.0249 |      0.9645 |       0.9519 |       0.9285 |          nan |          nan |           nan |           nan |                   0.0126 |                       nan | 33.4714 |  34.2062 |  34.7821 |      nan |       nan |       nan |  34.0992 |  34.5054 |  34.7882 |            0.9733 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |         0.0218 |                 0.0005 |          0.3556 |          -0.0046 |           0.2980 |           -0.0022 |           0.3081 |            0.0006 |           0.3443 |           -0.0022 |              nan |               nan |             -0.8170 |               0.2725 |               0.3113 |                  nan |     1217.0000 |      1504.7000 |      1601.8000 |            nan |             1.4800 |             1.3903 |                nan |                       1 |                       1 |                 -5.9189 |                  21.0320 |           -4058.0000 |             1914.0000 |                  1.3040 |        -3762 |  -8539.9000 |      33.1307 |      34.1328 |     33.1307 |  44.7025 | 44.9137 | -0.5546 |       -0.4404 |     -0.1142 |   35.8005 |   24.1663 |       94.6222 |       36.4635 |     -61.7012 | 20.4078 |   17.8051 |    27.7167 |  -74.0979 | -10.5950 |  -2.3170 |   0.8115 |       -0.8030 | 0.9757 | 2.8820 |    34.5782 |     33.4714 |    32.3645 |     0.0661 |        0.6727 | 74829.0000 | 20003.3087 | 69.5618 |         33.7057 |          33.7427 |        33.6317 |   33.8660 |       nan |    34.9552 |          0 |            0 |               0 |                  0 |                  0 |          0.0216 |         -0.0238 |           0.0081 |              nan |              -0.0742 |                  nan |                   nan |              -1.1772 |                  nan |       7.7089 |             7.3795 |                 0.3295 |               -0.0271 |                   nan |                    nan |        -2.7160 |           -0.3964 |          7.7089 |                  0.2410 |        -0.2127 |            -0.5840 |         0.3648 |               0.0021 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.3904 |              nan |              1.0000 |           2.0080 |            0.0121 |               0.0007 |           1.3358 |       -0.0269 |         -0.4791 |             0.2106 |                 nan |           0.7398 |           0.5366 |           0.3263 |               nan |                0.9464 |                     nan |                  0.0003 |                 nan |           0.0000 |              3.5969 |               0.0258 |             0.9733 |        0 |
| PLW      | PLN        |       33.2380 |      909 | 2016-12-28 00:00:00  |   2016 |      12 |         2 |         4 |           363 |             52 |              1 |                1 |             1 |      0.9818 |      1.0082 |      0.9667 |       0.9357 |       0.9188 |          nan |          nan |           nan |           nan |                   0.0310 |                       nan | 33.2437 |  33.9850 |  34.7069 |      nan |       nan |       nan |  33.9666 |  34.4091 |  34.7170 |            0.9577 |               nan |                nan |                 0 |                 0 |                  0 |                    0 |                    0 |        -0.0182 |                 0.0003 |          0.3688 |          -0.0065 |           0.2713 |           -0.0063 |           0.2872 |           -0.0021 |           0.3471 |           -0.0026 |              nan |               nan |             -1.1384 |              -1.5034 |               0.0953 |                  nan |     1312.6000 |      1477.0000 |      1263.7500 |            nan |             0.6154 |             0.7193 |                nan |                       0 |                       0 |                 -8.4937 |                   6.9559 |             478.0000 |            -6761.0000 |                  1.2078 |        -4671 |  -8125.4500 |      33.8537 |      33.8537 |     32.8462 |  40.7115 | 36.9458 | -0.5833 |       -0.4690 |     -0.1143 |   42.9388 |   32.2435 |       51.4690 |       53.6198 |     -78.3844 | 20.7693 |   16.4872 |    27.7553 |  -91.2813 | -18.5770 |  -6.2406 |  -4.3274 |       -2.2123 | 0.9779 | 2.9422 |    33.8809 |     33.2437 |    32.6065 |     0.0383 |        0.4955 | 73920.0000 | 19801.3045 | 65.8166 |         33.3126 |          33.2940 |        33.3499 |   33.7061 |       nan |    34.8304 |          0 |            0 |               0 |                  0 |                  0 |         -0.0184 |         -0.0337 |          -0.0442 |              nan |              -0.0847 |                  nan |                   nan |              -1.2476 |                  nan |       6.8134 |             7.1426 |                -0.3295 |               -0.0432 |                   nan |                    nan |        -3.2613 |           -0.7021 |          6.8134 |                  0.9176 |        -0.3759 |            -0.2843 |         0.3582 |               0.0004 |                       nan |                       nan |                      nan |                        nan |                       nan |                         nan |                     nan |                     nan |                  nan |                         nan |                         nan |                         nan |                          nan |                       nan |                  nan |                        nan |                        nan |                       nan |                         nan |                        nan |                          nan |                      nan |                      nan |                   nan |                          nan |                          nan |                          nan |                           nan |                        nan |                   nan |             -0.0060 |              nan |              1.0000 |           1.7203 |            0.0094 |               0.0007 |           1.3572 |        0.0135 |         -0.4935 |             0.3860 |                 nan |           0.7482 |           0.5546 |           0.3329 |               nan |                0.4396 |                     nan |                  0.0003 |                 nan |           0.0000 |              3.5969 |               0.0263 |             0.9920 |        0 |

## Database Integration Notes

### Key Features for Database Storage
- **Price Features** (23): close_price, price_to_sma_20, price_to_sma_50, price_to_sma_200, price_above_sma_20
- **Technical Indicators** (41): sma_5, sma_10, sma_20, sma_50, sma_100, sma_200, ema_12, ema_26, ema_50, price_to_sma_20
- **Volume Features** (19): volume, volume_ma_5, volume_ma_10, volume_ma_20, volume_ma_50, volume_ratio_10d, volume_ratio_20d, volume_ratio_50d, volume_increasing_10d, volume_increasing_20d, price_volume_trend_5d, price_volume_trend_20d, volume_momentum_5d, volume_momentum_20d, volume_volatility_20d, log_volume, log_volume_ma_20, log_volume_ratio_20d, volume_boxcox
- **Growth Features** (12): growth_1d, growth_3d, growth_7d, growth_14d, growth_30d
- **Target Variables** (1): target
