# Changelog

All notable changes to Redis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-07-28

### Added
- Enhanced logging with pretty-loguru integration
- Configuration validation methods for `RedisOptions` and `RedisConnectionConfig`
- Extended `RedisConnectionConfig` with new options:
  - `connection_timeout` and `socket_timeout` for timeout control
  - `retry_on_timeout` and `retry_on_error` for retry behavior
  - `health_check_interval` for connection health monitoring
  - SSL/TLS support with certificate options
- Comprehensive API documentation in `docs/API.md`
- Quick start guide in `docs/QUICKSTART.md`
- `@with_retry` decorator in retry utilities

### Changed
- Replaced standard logging with pretty-loguru throughout the codebase
- Updated `RedisOptions` with `log_level` and `log_path` configuration
- Improved error messages with more helpful suggestions

### Fixed
- Thread safety improvements in connection pool manager
- Better error handling during Python shutdown

### Removed
- All yaml2py dependencies and configuration support
- Environment variable configuration support (`create_from_env`)
- Factory module and lazy loading functionality

## [0.2.0] - 2025-07-15

### Added
- Support for passing existing Redis instances to RedisToolkit
- Dual initialization methods (Redis instance or configuration)
- `client` property for accessing underlying Redis client
- Connection pool manager for efficient connection reuse
- Comprehensive error handling with custom exceptions

### Changed
- RedisToolkit now accepts either `redis` or `config` parameter
- Improved serialization with better type support
- Enhanced validation with configurable limits

### Security
- Disabled pickle serialization to prevent RCE vulnerabilities
- Added input validation for key lengths and value sizes

## [0.1.0] - 2025-07-01

### Added
- Initial release of Redis Toolkit
- Basic set/get operations with automatic serialization
- Batch operations for efficient multi-key handling
- Pub/Sub support with automatic JSON serialization
- Media converters for images, audio, and video
- Retry mechanism with exponential backoff
- Context manager support
- Thread-safe operations

### Features
- Support for Python native types (dict, list, bool, bytes, int, float)
- NumPy array serialization
- Configurable logging and validation
- Connection pooling support
- Subscriber thread management

## [Unreleased]

### Planned
- Performance benchmarking suite
- Additional example scripts
- Enhanced documentation with tutorials
- Code coverage improvements
- Long function refactoring

---

For more details, see the [GitHub releases](https://github.com/JonesHong/redis-toolkit/releases).