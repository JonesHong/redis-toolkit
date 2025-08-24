# Changelog

All notable changes to Redis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-08-25

### 🎉 New Features
- **Dynamic Subscription Management** - 動態訂閱管理功能
  - Auto-expiration after configurable idle time (default 5 minutes)
  - Channel activity tracking and statistics
  - Expired channel history with resubscribe capability
  - Thread-safe implementation with automatic cleanup
  - Configurable via `RedisOptions` or runtime modification

### ✨ Enhancements
- Added `SubscriptionManager` class for intelligent pub/sub lifecycle management
- Enhanced `RedisToolkit` with dynamic subscription methods:
  - `subscribe_dynamic()` - Dynamic channel subscription with custom callbacks
  - `unsubscribe_dynamic()` - Unsubscribe from channels
  - `get_subscription_stats()` - Get subscription statistics
  - `get_expired_channels()` - Query expired channels
  - `resubscribe_channel()` - Resubscribe to expired channels
  - `set_subscription_manager()` - Replace or disable subscription manager at runtime
- Extended `RedisOptions` with subscription configuration:
  - `enable_dynamic_subscription` - Enable/disable feature
  - `subscription_expire_minutes` - Channel expiration time
  - `subscription_check_interval` - Expiration check interval
  - `subscription_auto_cleanup` - Auto cleanup expired records
  - `subscription_max_expired` - Maximum expired records to keep

### 📚 Documentation
- Added comprehensive examples for dynamic subscription
- Updated CLAUDE.md with new architecture details
- Added unit tests for subscription manager

### 🔧 Technical Details
- Maintains backward compatibility
- Zero impact on existing pub/sub functionality
- Optional feature that can be disabled
- Thread-safe with RLock protection
- Automatic resource cleanup

## [0.3.0] - 2025-07-28

### 🗑️ Removed (Breaking Changes)
- Removed `RedisCore` alias (backward compatibility)
- Removed `enable_retry` parameter (retry is now always enabled)
- Removed `decode_responses` option (always False)
- Removed `socket_keepalive_options` option (rarely used)
- Removed custom `redis_client` parameter

### ✨ Improvements
- Simplified API with fewer unnecessary parameters
- Clearer initialization flow
- Reduced codebase by ~100 lines

### 🔐 Security Enhancements
- Added input validation mechanism
- Configurable size limits for keys and values
- Protection against resource exhaustion attacks

### 🛠️ Other Changes
- Improved exception handling granularity
- Enhanced log formatting for large data
- Better thread safety for pub/sub operations

## [0.2.0] - 2025-07-28

### 🔐 Security
- **BREAKING**: Completely removed pickle serialization to eliminate remote code execution vulnerabilities
- All serialization now uses secure JSON-based formats
- Added SECURITY.md with security policy and best practices

### ✨ Added
- Safe NumPy array serialization using JSON format
- Clear error messages for unsupported data types
- Security-first design philosophy

### 💥 Breaking Changes
- Custom class instances and function objects are no longer serializable
- Applications relying on pickle serialization will need to migrate to supported types
- Removed `_try_pickle_load()` function

### 📝 Documentation
- Added comprehensive security documentation
- Updated README to highlight security improvements
- Added migration guidance for affected users

### 🐛 Fixed
- Eliminated critical security vulnerability (potential RCE via pickle)

## [0.1.3] - Previous Release

### Added
- Video converter support
- Image converter improvements
- Enhanced error handling

### Fixed
- Various bug fixes and performance improvements

---

For more details, see the [commit history](https://github.com/JonesHong/redis-toolkit/commits/main).