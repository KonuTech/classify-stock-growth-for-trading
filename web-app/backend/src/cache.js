const redis = require('redis');

class CacheManager {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.retryCount = 0;
    this.maxRetries = 3;
  }

  async connect() {
    try {
      if (this.client && this.isConnected) {
        return this.client;
      }

      const redisHost = process.env.REDIS_HOST || 'localhost';
      const redisPort = process.env.REDIS_PORT || 6379;

      console.log(`📦 Connecting to Redis at ${redisHost}:${redisPort}...`);
      
      this.client = redis.createClient({
        socket: {
          host: redisHost,
          port: redisPort,
          reconnectDelay: 1000,
        },
      });

      this.client.on('error', (err) => {
        console.error('❌ Redis error:', err.message);
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        console.log('✅ Redis connected successfully');
        this.isConnected = true;
        this.retryCount = 0;
      });

      this.client.on('ready', () => {
        console.log('✅ Redis ready for operations');
        this.isConnected = true;
      });

      this.client.on('end', () => {
        console.log('📦 Redis connection ended');
        this.isConnected = false;
      });

      await this.client.connect();
      return this.client;
    } catch (error) {
      console.error('❌ Failed to connect to Redis:', error.message);
      this.isConnected = false;
      
      // Graceful degradation - continue without cache
      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        console.log(`🔄 Retrying Redis connection (${this.retryCount}/${this.maxRetries})...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return this.connect();
      }
      
      console.log('⚠️ Operating without Redis cache (graceful degradation)');
      return null;
    }
  }

  /**
   * Generate cache key for stock statistics
   */
  getStockListKey(timeframe) {
    return `stock_list:${timeframe}`;
  }

  getStockStatsKey(symbol, timeframe) {
    return `stock_stats:${symbol}:${timeframe}`;
  }

  getStockDetailKey(symbol, timeframe) {
    return `stock_detail:${symbol}:${timeframe}`;
  }

  getCacheTimestampKey(timeframe) {
    return `cache_timestamp:${timeframe}`;
  }

  /**
   * Get cache TTL based on timeframe
   */
  getTTL(timeframe) {
    const ttlMap = {
      '1M': 3600,    // 1 hour
      '3M': 3600,    // 1 hour  
      '6M': 7200,    // 2 hours
      '1Y': 7200,    // 2 hours
      'MAX': this.getMaxTTL(),  // Dynamic TTL until market close + 1 hour
    };
    return ttlMap[timeframe] || 3600; // default 1 hour
  }

  /**
   * Calculate dynamic TTL for MAX timeframe until next market close + buffer
   */
  getMaxTTL() {
    const now = new Date();
    const today = new Date(now);
    
    // Set to 18:00 (6 PM) Warsaw time - after market close (17:00)
    const marketCloseToday = new Date(today);
    marketCloseToday.setHours(18, 0, 0, 0);
    
    // If it's already past 6 PM today, set for tomorrow 6 PM
    const targetTime = now > marketCloseToday 
      ? new Date(marketCloseToday.getTime() + 24 * 60 * 60 * 1000)
      : marketCloseToday;
    
    // Calculate seconds until target time
    const secondsUntilRefresh = Math.floor((targetTime - now) / 1000);
    
    // Minimum 1 hour, maximum 25 hours (for weekend/holidays)
    return Math.max(3600, Math.min(secondsUntilRefresh, 25 * 3600));
  }

  /**
   * Get cached data with automatic JSON parsing
   */
  async get(key) {
    try {
      if (!this.isConnected || !this.client) {
        return null;
      }

      const data = await this.client.get(key);
      if (!data) {
        return null;
      }

      const parsed = JSON.parse(data);
      console.log(`📦 Cache HIT for key: ${key}`);
      return parsed;
    } catch (error) {
      console.error(`❌ Cache GET error for ${key}:`, error.message);
      return null;
    }
  }

  /**
   * Set cached data with automatic JSON serialization and TTL
   */
  async set(key, data, timeframe) {
    try {
      if (!this.isConnected || !this.client) {
        console.log(`⚠️ Cache unavailable, skipping SET for ${key}`);
        return false;
      }

      const ttl = this.getTTL(timeframe);
      const serialized = JSON.stringify(data);
      
      await this.client.setEx(key, ttl, serialized);
      console.log(`📦 Cache SET for key: ${key} (TTL: ${ttl}s)`);
      
      // Also set timestamp for cache validation
      const timestampKey = this.getCacheTimestampKey(timeframe);
      await this.client.setEx(timestampKey, ttl, Date.now().toString());
      
      return true;
    } catch (error) {
      console.error(`❌ Cache SET error for ${key}:`, error.message);
      return false;
    }
  }

  /**
   * Check if cache is fresh for a given timeframe
   */
  async isCacheFresh(timeframe, maxAgeMinutes = 60) {
    try {
      if (!this.isConnected || !this.client) {
        return false;
      }

      const timestampKey = this.getCacheTimestampKey(timeframe);
      const timestamp = await this.client.get(timestampKey);
      
      if (!timestamp) {
        return false;
      }

      const cacheAge = (Date.now() - parseInt(timestamp)) / 1000 / 60; // minutes
      const maxAge = timeframe === 'MAX' ? 1440 : maxAgeMinutes; // MAX: 24 hours, others: 1 hour
      
      return cacheAge < maxAge;
    } catch (error) {
      console.error(`❌ Cache freshness check error for ${timeframe}:`, error.message);
      return false;
    }
  }

  /**
   * Invalidate cache for specific timeframe
   */
  async invalidate(timeframe) {
    try {
      if (!this.isConnected || !this.client) {
        return;
      }

      const pattern = timeframe === 'ALL' 
        ? 'stock_*' 
        : `*:${timeframe}`;
        
      const keys = await this.client.keys(pattern);
      
      if (keys.length > 0) {
        await this.client.del(keys);
        console.log(`🗑️ Invalidated ${keys.length} cache keys for ${timeframe}`);
      }
    } catch (error) {
      console.error(`❌ Cache invalidation error for ${timeframe}:`, error.message);
    }
  }

  /**
   * Get cache statistics
   */
  async getStats() {
    try {
      if (!this.isConnected || !this.client) {
        return { connected: false };
      }

      const info = await this.client.info('memory');
      const keyCount = await this.client.dbSize();
      
      return {
        connected: this.isConnected,
        keyCount,
        memoryInfo: info
      };
    } catch (error) {
      console.error('❌ Cache stats error:', error.message);
      return { connected: false, error: error.message };
    }
  }
}

// Singleton instance
const cacheManager = new CacheManager();

module.exports = cacheManager;