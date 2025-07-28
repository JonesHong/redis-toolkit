# Changelog

All notable changes to Redis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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