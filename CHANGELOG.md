# AppSignal for Python Changelog

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
