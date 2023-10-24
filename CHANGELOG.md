# AppSignal for Python Changelog

## 0.3.2

### Added

- [48fbe34](https://github.com/appsignal/appsignal-python/commit/48fbe341ff53396faa22832879386db28499a6b3) patch - Add the `--environment` CLI option to the demo CLI tool. This allow you to configure to which app environment the demo samples should be sent. It would default to production (and only be configurable via the `APPSIGNAL_APP_ENV` environment variable), but now it's configurable through the CLI options as well.
  
  ```
  python -m appsignal demo --environment=production
  ```
- [3f97c9d](https://github.com/appsignal/appsignal-python/commit/3f97c9dfcfde922a36d8f1545c76a0b1641fd0df) patch - Add the `set_sql_body` tracing helper to set the body attribute on a span that contains a SQL query. When using this helper the given SQL query will be sanitized, reducing the chances of sending sensitive data to AppSignal.
  
  ```python
  from appsignal import set_sql_body
  
  # Must be used in an instrumented context -- e.g. a Django or Flask handler
  def index():
      set_sql_body("SELECT * FROM users WHERE 'password' = 'secret'")
      # Will be stored as:
      set_sql_body("SELECT * FROM users WHERE 'password' = ?")
  ```
  
  When the `set_body` helper is also used, the `set_sql_body` overwrites the `set_body` attribute.
  
  More information about our [tracing helpers](https://docs.appsignal.com/python/instrumentation/instrumentation.html) can be found in our documentation.

### Changed

- [9cca18d](https://github.com/appsignal/appsignal-python/commit/9cca18d39b7ec815fe404f37337689f06165be1c) patch - When the `__appsignal__.py` file is found in the directory in which the demo and diagnose CLIs are run (`python -m appsignal demo` or `python -m appsignal diagnose`), AppSignal will now load the `__appsignal__.py` file's configuration. When this file is loaded, the demo and diagnose CLI will use the configuration declared in that file to send the demo data and compile a diagnose report. In this scenario, it will no longer prompt you to enter the application configuration manually.
- [b0c6c28](https://github.com/appsignal/appsignal-python/commit/b0c6c28902d142efc3bb7e677aa61294fe24e99a) patch - Bump agent to 8260fa1
  
  - Add `appsignal.sql_body` magic span attribute for OpenTelemetry spans. When this attribute is detected, we store the value as the span/event body. This span is sanitized beforehand so it doesn't contain any sensitive data and helps to group events in our backend. When used in combination with the `appsignal.body` attribute, the new `appsignal.sql_body` attribute is leading.
  
    More information on [AppSignal OpenTelemetry span attributes](https://docs.appsignal.com/opentelemetry/custom-instrumentation/attributes.html) can be found in our docs.

### Fixed

- [791f874](https://github.com/appsignal/appsignal-python/commit/791f874b5c670618719f3c8a6d48837da37129f7) patch - Validate the AppSignal configuration before starting the AppSignal agent. This prevents the agent from starting with an invalid config and while reporting no data. The AppSignal client and demo CLI will communicate that they could not send any data in this invalid configuration scenario.
- [6d42381](https://github.com/appsignal/appsignal-python/commit/6d42381b28bce61b246ea549f2a91ec9a6185e32) patch - Fix the agent diagnostic report in diagnose CLI tool (`python -m appsignal diagnose`). The agent diagnose report would always contain an error, because it did not pick up the AppSignal configuration properly.

## 0.3.1

### Changed

- [4b94772](https://github.com/appsignal/appsignal-python/commit/4b947723346ad8f3b538caa85e5cf4d8d383d1f9) patch - Bump agent to e8207c1.
  
  - Add `memory_in_percentages` and `swap_in_percentages` host metrics that represents metrics in percentages.
  - Ignore `/snap/` disk mountpoints.
  - Fix issue with the open span count in logs being logged as a negative number.
  - Fix agent's TCP server getting stuck when two requests are made within the same fraction of a second.

## 0.3.0

### Added

- [9e4d6ef](https://github.com/appsignal/appsignal-python/commit/9e4d6ef326ddb495755707312b64fc9a7cbaf938) minor - Support OpenTelemetry metrics through its metrics exporter. We enable the metrics exporter by default so it can be used to collect data from instrumentations and manually by using an OpenTelemetry metrics meter. Not all metric types are supported at this time, only sums and gauges.
- [073b3c2](https://github.com/appsignal/appsignal-python/commit/073b3c2958b21d0347461b2aca7841f8d0e897a9) patch - Add error helpers. These helpers simplify reporting errors to AppSignal that are not handled automatically by your framework, alongside the current instrumented context or separately. For example, to report an error from an `except` clause as a separate sample:
  
  ```python
  from appsignal import send_error
  
  def index():
    cookies = put_hand_in_cookie_jar()
    except HandStuckError as error:
      send_error(error)
  ```
  
  More information about [error helpers](https://docs.appsignal.com/python/instrumentation/exception-handling.html) is available in our documentation.
- [073b3c2](https://github.com/appsignal/appsignal-python/commit/073b3c2958b21d0347461b2aca7841f8d0e897a9) patch - Add sample data helpers. These helpers simplify adding properties to OpenTelemetry spans that display specific data in the AppSignal sample UI. For example, to add custom data to the current sample:
  
  ```python
  from appsignal import set_custom_data
  
  # Must be used in an instrumented context -- e.g. a Flask handler
  @app.get("/")
  def index():
    set_custom_data({"hello": "there"})
  ```
  
  The full list of sample data helpers is available in our documentation as part of the [tagging and sample data guides](https://docs.appsignal.com/guides/custom-data.html) and [namespace guide](https://docs.appsignal.com/guides/namespaces.html).
- [61988e5](https://github.com/appsignal/appsignal-python/commit/61988e5010c4710121af1f0ce8e4b6797171651a) patch - Add helper for reporting counter metrics to AppSignal using OpenTelemetry. Use these helpers to simplify sending counter metrics as supported by AppSignal.
  
  ```python
  from appsignal import increment_counter
  
  # Report a counter increasing
  increment_counter("counter_name", 1)
  # Report a counter decreasing
  increment_counter("counter_name", -1)
  
  # Add tags to counter
  increment_counter("counter_with_tags", 1, {"tag1": "value1"})
  ```
  
  Consult our documentation for more information about AppSignal's [custom metrics](https://docs.appsignal.com/metrics/custom.html).
- [61988e5](https://github.com/appsignal/appsignal-python/commit/61988e5010c4710121af1f0ce8e4b6797171651a) patch - Add helper for reporting gauge metrics to AppSignal using OpenTelemetry. Use these helpers to simplify sending gauge metrics as supported by AppSignal.
  
  ```python
  from appsignal import set_gauge
  
  # Report a gauge value
  set_gauge("gauge_name", 10)
  
  # Add tags to metrics
  set_gauge("gauge_with_tags", 10, {"tag1": "value1"})
  ```
  
  Consult our documentation for more information about AppSignal's [custom metrics](https://docs.appsignal.com/metrics/custom.html).

### Changed

- [1d72ea7](https://github.com/appsignal/appsignal-python/commit/1d72ea74a7709135660ccd2f826a5400d1511e11) patch - Bump agent to 6133900.
  
  - Fix `disk_inode_usage` metric name format to not be interpreted as a JSON object.
  - Convert all OpenTelemetry sum metrics to AppSignal non-monotonic counters.
  - Rename standalone agent's `role` option to `host_role` so it's consistent with the integrations naming.

## 0.2.3

### Fixed

- [1a52190](https://github.com/appsignal/appsignal-python/commit/1a52190c11f1f83f1421b28a0f9f448aa4326fe0) patch - Fix CLI using `python -m appsignal`. It would error with a `ModuleNotFoundError`.

## 0.2.2

### Added

- [381638e](https://github.com/appsignal/appsignal-python/commit/381638e08a67cd15e86c6cec81beec9a0cf03cb4) patch - Add the `statsd_port` config option to change the StatsD UDP server port of the appsignal-agent process. By default the port is set to 8125.
- [7f5c848](https://github.com/appsignal/appsignal-python/commit/7f5c848631e818073620e0f43de7fbba85ec0a11) patch - Add the `host_role` config option. This config option can be set per host to generate some metrics automatically per host and possibly do things like grouping in the future.
- [c2e0e2c](https://github.com/appsignal/appsignal-python/commit/c2e0e2c17ae1692eb35410bdccfe74536e52d9ea) patch - Add the OpenTelemetry HTTP server port config option (`opentelemetry_port`) to configure on which port the `appsignal-agent` server process will listen for OpenTelemetry data from the HTTP exporter. This can be used to configure two apps on the same machine to use different ports so it's possible to run two AppSignal apps on the same machine. See our [Running multiple applications on one host docs page](https://docs.appsignal.com/guides/application/multiple-applications-on-one-host.html) for more information.

### Changed

- [5a0cfa9](https://github.com/appsignal/appsignal-python/commit/5a0cfa95e7b4207aa8010eea3693459b89afa29f) patch - Bump agent to version d789895.
  
  - Increase short data truncation from 2000 to 10000 characters.

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
