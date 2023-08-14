# AppSignal for Python Changelog

## 0.2.1

### Changed

- [bb0d90b](https://github.com/appsignal/appsignal-python/commit/bb0d90b10af9184fe56c1ed23ff2795a488bf915) patch - Warn if the appsignal-beta package is present in the dependencies list to nudge people into switching to the new `appsignal` package.

## 0.2.0

### Added

- [6b164d2](https://github.com/appsignal/appsignal-python/commit/6b164d2811540d1cd9ebdae5767935142674a5c3) patch - Use `RENDER_GIT_COMMIT` environment variable as revision if no revision is specified.
- [74a961e](https://github.com/appsignal/appsignal-python/commit/74a961e344929c486c345c32f5c7d784d311213d) patch - Allow configuration of the agent's TCP and UDP servers using the `bind_address` config option. This is by default set to `127.0.0.1`, which only makes it accessible from the same host. If you want it to be accessible from other machines, use `0.0.0.0` or a specific IP address.
- [0d1de38](https://github.com/appsignal/appsignal-python/commit/0d1de38237fc1863e31c9626e6cac81c7d2f6b7d) patch - Report total CPU usage host metric for VMs. This change adds another `state` tag value on the `cpu` metric called `total_usage`, which reports the VM's total CPU usage in percentages.
- [c186236](https://github.com/appsignal/appsignal-python/commit/c1862362f217600d80e568a562d4af81ce34230c) patch - Add diagnose command

### Changed

- [ebdcdec](https://github.com/appsignal/appsignal-python/commit/ebdcdec6d2ac064b4dbcb1d2da3f402b409b654e) minor - Rename package from `appsignal-beta` to `appsignal`. Please update your dependencies (for example, in `requirements.txt`) accordingly.
- [6c8dc88](https://github.com/appsignal/appsignal-python/commit/6c8dc8803e0662bf2e8eae9f29bca7c2636f0e38) patch - Bump agent to 32590eb.
  
  - Only ignore disk metrics that start with "loop", not all mounted disks that end with a number to report metrics for more disks.
- [61c3537](https://github.com/appsignal/appsignal-python/commit/61c3537a9f338be480a2a4ef0d378f01e379be76) patch - Bump agent to 6bec691.
  
  - Upgrade `sql_lexer` to v0.9.5. It adds sanitization support for the `THEN` and `ELSE` logical operators.

## 0.1.4

### Added

- [8490ba0](https://github.com/appsignal/appsignal-python/commit/8490ba0af53ae87b92d61eed4834a6ae33600902) patch - Add support for OpenTelemetry instrumentation of ASGI-based frameworks, such as FastAPI and Starlette.

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
