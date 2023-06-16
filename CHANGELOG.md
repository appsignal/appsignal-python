# AppSignal for Python Changelog

## 0.1.3

### Changed

- [e2572ea](https://github.com/appsignal/appsignal-python/commit/e2572ead60b411ec5dfa5ab6e8465f50c2cecf08) patch - Change the configuration source load order. The environment variables are no longer leading, but the `__appsignal__.py` file source is. The load order is now:
  
  - Default source (hardcoded config)
  - System source (context dependent config)
  - Environment source (environment variables)
  - Initial source (any config given to `Config()` in `__appsignal__.py`)
- [6a23212](https://github.com/appsignal/appsignal-python/commit/6a232129c634b4e0c3880e80d8425c0d032ab344) patch - Bump agent to 91f1a7c
  
  - Fall back on the revision option for OpenTelemetry endpoint from config, rather than only read it from the OpenTelemetry resource attributes.
  - Fix agent restart when the config changes, not detecting a config change and not starting a new agent process.
  - Retry agent servers port binding when port is busy. This fixes Python package restarting the agent when another agent instance is still running.

## 0.1.2

### Changed

- [a96736a](https://github.com/appsignal/appsignal-python/commit/a96736a9dbb69764cd44b429ff5dfa7cb8cb14eb) patch - Bump agent to 8cb4ef2
  
  - Fix backtrace parsing for Python.
  - Add Flask support.
  - Fix running_in_container detecting for hosts running Docker.
  - Improve running_in_container config option load order.
- [7fbf731](https://github.com/appsignal/appsignal-python/commit/7fbf731064de0a79266f8cc467d60346f2484d77) patch - Bump agent d21e1f4
  
  - Don't report incidents for root spans that are only psycopg2 queries.

## 0.1.1

### Fixed

- [7f4fb7a](https://github.com/appsignal/appsignal-python/commit/7f4fb7a24406010a0e93c6ce7cfeb03c50900b6f) patch - Fix an issue where the installer would fail due to the certificate bundle being missing.

## 0.1.0

### Changed

- [0bb38d1](https://github.com/appsignal/appsignal-python/commit/0bb38d10ce2bf0fddc91f074d500924e4b79886c) minor - Initial beta release
