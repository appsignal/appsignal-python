# AppSignal for Python Changelog

## 1.6.1

_Published on 2025-10-13._

### Fixed

- Fix parsing of OpenTelemetry spans emitted by `FastAPI` and popular database libraries. (patch [8209230](https://github.com/appsignal/appsignal-python/commit/8209230267a26585c64ea69ddfcf930af2c2fd22))

## 1.6.0

_Published on 2025-10-09._

### Added

- Support logging through the external collector experimental feature. When the `collector_endpoint` configuration option is provided, the OpenTelemetry stack will be automatically configured to instrument logs.

  The `logging` module will be automatically instrumented, such that log lines emitted through loggers that propagate to the root logger will be automatically sent to AppSignal. To disable this behaviour, add `"logging"` to the `disable_default_instrumentations` configuration option list.

  (minor [c7ac2bd](https://github.com/appsignal/appsignal-python/commit/c7ac2bdd20d33321fcc8c6e58da95c5550b2f67c))
- Support usage with external collector. When the `collector_endpoint` configuration option is provided, instead of booting up the AppSignal agent bundled with the application, the OpenTelemetry stack will be configured to send data to the given collector.

  This is an **experimental** feature. The following functionality is not currently supported when using the collector:

  - NGINX metrics
  - StatsD metrics
  - Host metrics

  Some configuration options are only supported when using the agent or when using the collector. A warning will be emitted if a configuration option that is only supported by one is set while using the other.

  (minor [c7ac2bd](https://github.com/appsignal/appsignal-python/commit/c7ac2bdd20d33321fcc8c6e58da95c5550b2f67c))

## 1.5.4

_Published on 2025-06-06._

### Added

- Add `nginx_port` configuration option. This configuration option can be used to customize the port on which the AppSignal integration exposes [the NGINX metrics server](https://docs.appsignal.com/metrics/nginx.html). (patch [e531134](https://github.com/appsignal/appsignal-python/commit/e5311340141879d02ec2d40ff8961b40b669e711), [151c290](https://github.com/appsignal/appsignal-python/commit/151c290c14878f787936ac8c2c1e18bf0db56e5c), [2a76f66](https://github.com/appsignal/appsignal-python/commit/2a76f66c6f9cdf769833d9c0e0666bffdebd8fbd))

## 1.5.3

_Published on 2025-05-08._

### Changed

- Allow overriding namespaces that are automatically set by the AppSignal agent based on the OpenTelemetry instrumentation that emitted the span, such as the `graphql` or `background` namespaces. (patch [548ba1c](https://github.com/appsignal/appsignal-python/commit/548ba1c051bfaf9b6305c8ae3adabe785da0bacc))

## 1.5.2

_Published on 2025-05-05._

### Changed

- Remove redundant cron check-in pairs. When more than one pair of start and finish cron check-in events is reported for the same identifier in the same period, only one of them will be reported to AppSignal. (patch [392a9e7](https://github.com/appsignal/appsignal-python/commit/392a9e718b3d1100b68afa0f1d6286386333c357))

## 1.5.1

_Published on 2025-03-14._

### Changed

- Improve SQL sanitisation for functions and numbered placeholders. (patch [684f895](https://github.com/appsignal/appsignal-python/commit/684f895bf70093fe26ccf5f59fa2cab3e22d720a))

## 1.5.0

_Published on 2025-02-24._

### Changed

- [cea5704](https://github.com/appsignal/appsignal-python/commit/cea5704df63a917cb6d17449b88fa4710b708af9) patch - Update span recognition following the OpenTelemetry Semantic Conventions 1.30 database specification. We now also sanitize SQL queries in the `db.query.text` attribute and Redis queries in the `db.operation.name` attribute.
- [71eb3f7](https://github.com/appsignal/appsignal-python/commit/71eb3f743051d6864e5447cf4fc2ba1eb9e3fc3e) patch - Update bundled trusted root certificates

### Removed

- [cea5704](https://github.com/appsignal/appsignal-python/commit/cea5704df63a917cb6d17449b88fa4710b708af9) minor - Remove the OpenTelemetry beta feature in favor of the new [AppSignal collector](https://docs.appsignal.com/collector). If you are using the AppSignal agent to send OpenTelemetry data in our public beta through the `/enriched` endpoint on the agent's HTTP server, please migrate to the collector to continue using the beta. The collector has a much better implementation of this feature for the beta.

### Fixed

- [11afe17](https://github.com/appsignal/appsignal-python/commit/11afe177c02feded4f296d3340f75d3729349ad3) patch - Fix an issue where calling `appsignal.stop()` after sending check-in events would leave a dangling thread, stopping the application from shutting down correctly.

## 1.4.1

_Published on 2024-12-20._

### Added

- Set the app revision config option for Scalingo deploys automatically. If the `CONTAINER_VERSION` system environment variable is present, it will use used to set the `revision` config option automatically. Overwrite it's value by configuring the `revision` config option for your application. (patch [fbec34c](https://github.com/appsignal/appsignal-python/commit/fbec34cbddfd40fa4bf2b2cd166e45c1df63fc56))

### Fixed

- Fix a performance issue when sanitising `INSERT INTO ... VALUES` queries. (patch [073e6d2](https://github.com/appsignal/appsignal-python/commit/073e6d2c5c928e6cb527786469a2b0518417c296))

## 1.4.0

_Published on 2024-10-09._

### Added

- Add support for heartbeat check-ins.

  Use the `appsignal.check_in.heartbeat` function to send a single heartbeat check-in event from your application. This can be used, for example, in your application's main loop:

  ```python
  from appsignal.check_in import heartbeat

  while True:
    heartbeat("job_processor")
    process_job()
  ```

  Heartbeats are deduplicated and sent asynchronously, without blocking the current thread. Regardless of how often the `.heartbeat` function is called, at most one heartbeat with the same identifier will be sent every ten seconds.

  Pass `continuous=True` as the second argument to send heartbeats continuously during the entire lifetime of the current process. This can be used, for example, after your application has finished its boot process:

  ```python
  def main():
    start_app()
    heartbeat("my_app", continuous=True)
  ```

  (minor [687890b](https://github.com/appsignal/appsignal-python/commit/687890b54db3b9f03d8e0a7270586c545a89fdb6))

### Changed

- Change the primary download mirror for integrations. (patch [3e0bb9e](https://github.com/appsignal/appsignal-python/commit/3e0bb9e36eb3b0fbe2ae9b907fcda9060c018d2e))
- Send check-ins concurrently. When calling `appsignal.check_in.cron`, instead of blocking the current thread while the check-in events are sent, schedule them to be sent in a separate thread. (patch [687890b](https://github.com/appsignal/appsignal-python/commit/687890b54db3b9f03d8e0a7270586c545a89fdb6))

## 1.3.10

_Published on 2024-08-23._

### Changed

- [f9b17a7](https://github.com/appsignal/appsignal-python/commit/f9b17a753cb8178851658334f6235add43acc89d) patch - Simplify the implementation of `set_gauge` in favor of the newer OpenTelemetry's sync implementation.

## 1.3.9

_Published on 2024-08-19._

### Added

- [c2e3f26](https://github.com/appsignal/appsignal-python/commit/c2e3f26575747fbd17e333c527ab33fc4758385d) patch - Add helper to manually stop the agent process for this AppSignal instance.
  
  Some contexts, like serverless functions, exit before AppSignal can ensure all data is sent to our servers. To ensure the data is sent, the new `appsignal.stop()` method can be called to gracefully stop the AppSignal agent process.

## 1.3.8

_Published on 2024-08-14._

### Changed

- Rename heartbeats to cron check-ins. Calls to `appsignal.heartbeat` and `appsignal.Heartbeat` should be replaced with calls to `appsignal.check_in.cron` and `appsignal.check_in.Cron`, for example:

  ```python
  # Before
  from appsignal import heartbeat

  def do_something():
    pass

  heartbeat("do_something", do_something)

  # After
  from appsignal.check_in import cron

  def do_something():
    pass

  cron("do_something", do_something)
  ```

  (patch [b530263](https://github.com/appsignal/appsignal-python/commit/b5302635665ed43c42d5cac063f7c008c2ffb85f))

### Deprecated

- Calls to `appsignal.heartbeat` and to the `appsignal.Heartbeat` constructor will emit a deprecation warning. (patch [b530263](https://github.com/appsignal/appsignal-python/commit/b5302635665ed43c42d5cac063f7c008c2ffb85f))

## 1.3.7

_Published on 2024-06-26._

### Added

- [d6d9724](https://github.com/appsignal/appsignal-python/commit/d6d9724c8655a667923859c87ac609e6729ce650) patch - Add support for Pika
- [626db80](https://github.com/appsignal/appsignal-python/commit/626db805596279b1c76e140edb8087855807c0af) patch - AMQP messaging processing with Pika tracing data is now supported.

## 1.3.6

_Published on 2024-06-12._

### Fixed

- [21ce8fb](https://github.com/appsignal/appsignal-python/commit/21ce8fb51338f7e94b2d9737ee511e6ea37ccb5d) patch - Fix an issue where Redis events are misidentified as HTTP events.

## 1.3.5

_Published on 2024-06-11._

### Added

- [8d036f8](https://github.com/appsignal/appsignal-python/commit/8d036f8ee5c6991ba9c15df64bdac66d0fc94a9d) patch - Add basic OpenTelemetry messaging support. This adds support for any OpenTelemetry instrumentation that complies with the OpenTelemetry Semantic Conventions specification for messaging.

### Changed

- [8d036f8](https://github.com/appsignal/appsignal-python/commit/8d036f8ee5c6991ba9c15df64bdac66d0fc94a9d) patch - Rename the `hostname` tag, which contains the host of the URI that an HTTP request was made against, to `request_host`.
  
  This fixes an issue where the `hostname` tag would later be internally overriden to the hostname of the machine processing the request, but notifications would still be emitted containing the previous `hostname` value.

## 1.3.4

### Added

- [5ed6e44](https://github.com/appsignal/appsignal-python/commit/5ed6e44b7afa98408833d836368270d3a7c34e7e) patch - Unsupported systems, like Microsoft Windows, won't start the agent and other integration components to prevent them from failing and allowing apps to be run normally.

## 1.3.3

_Published on 2024-05-14._

### Added

- [b3db311](https://github.com/appsignal/appsignal-python/commit/b3db3118ff5368d4e24d0bfaf15be725a1a6134a) patch - Support Kamal-based deployments. Read the `KAMAL_VERSION` environment variable, which Kamal exposes within the deployed container, if present, and use it as the application revision if it is not set. This will automatically report deploy markers for applications using Kamal.

## 1.3.2

_Published on 2024-05-06._

### Added

- [c4a2ac4](https://github.com/appsignal/appsignal-python/commit/c4a2ac4777ff8938bd58818349249b935b747b10) patch - Add support for the `aiopg`, `asyncpg`, `mysql`, `pymysql` and `mysqlclient` Python SQL database adapters.

## 1.3.1

_Published on 2024-04-29._

### Added

- [a455252](https://github.com/appsignal/appsignal-python/commit/a4552522962ff6f95d4c61b30ab111addb589719) patch - Add automatic instrumentation support for SQLAlchemy, SQLite and version 3 of the `psycopg` PostgreSQL adapter.

## 1.3.0

_Published on 2024-04-22._

### Added

- [6ac44b7](https://github.com/appsignal/appsignal-python/commit/6ac44b73af0f2351ca914f2499500e9073a9bd0a) minor - _Heartbeats are currently only available to beta testers. If you are interested in trying it out, [send an email to support@appsignal.com](mailto:support@appsignal.com?subject=Heartbeat%20beta)!_
  
  ---
  
  Add heartbeats support. You can use the `heartbeat` function to send heartbeats directly from your code, to track the execution of certain processes:
  
  ```python
  from appsignal import heartbeat
  
  def send_invoices():
    # ... your code here ...
    heartbeat("send_invoices")
  ```
  
  It is also possible to pass a defined function as an argument to the `heartbeat`
  function:
  
  ```python
  def send_invoices():
    # ... your code here ...
  
  heartbeat("send_invoices", send_invoices)
  ```
  
  If an exception is raised within the function, the finish event will not be
  reported to AppSignal, triggering a notification about the missing heartbeat.
  The exception will be raised outside of the heartbeat function.

## 1.2.1

### Fixed

- [bf4aa09](https://github.com/appsignal/appsignal-python/commit/bf4aa099ea87a09736c4b908ba0fa4a418f3a6d2) patch - Unmatching Flask app routes are no longer recorded as valid spans.

## 1.2.0

_Published on 2024-03-20._

### Added

- [9c20b6f](https://github.com/appsignal/appsignal-python/commit/9c20b6f821e25a7b7f5d47521a97f2a744ab66c6) minor - Add a minutely probes system. This can be used, alongside our metric helpers, to report metrics to AppSignal once per minute.
  
  ```python
  from appsignal import probes, set_gauge
  
  def new_carts(previous_carts=None):
      current_carts = Cart.objects.all().count()
  
      if previous_carts is not None:
        set_gauge("new_carts", current_carts - previous_carts)
  
      return current_carts
  
  probes.register("new_carts", new_carts)
  ```
  
  The minutely probes system starts by default, but no probes are automatically registered. You can use the `enable_minutely_probes` configuration option to disable it.
- [3a27381](https://github.com/appsignal/appsignal-python/commit/3a27381d42470a3e65e5862aa52d78ba77e28a30) patch - Implement CPU count configuration option. Use it to override the auto-detected, cgroups-provided number of CPUs that is used to calculate CPU usage percentages.
  
  To set it, use the the `cpu_count` configuration option or the `APPSIGNAL_CPU_COUNT` environment variable.

### Fixed

- [3a797e1](https://github.com/appsignal/appsignal-python/commit/3a797e1cca59ba1d6fcd67f7e36c25eff0445ee2) patch - Fix ASGI events (from Python ASGI applications) showing up in the "Slow API requests" panel.

## 1.1.1

_Published on 2024-03-11._

### Added

- [16fb8f9](https://github.com/appsignal/appsignal-python/commit/16fb8f94a848a0cdd8f15692ba0fe2cd3c5822c1) patch - Add distribution value custom metric helper. This can be used to add values to distributions in the same way as in our other integrations:
  
  ```python
  # Import the AppSignal metric helper
  from appsignal import add_distribution_value
  
  # The first argument is a string, the second argument a number (int/float)
  # add_distribution_value(metric_name, value)
  add_distribution_value("memory_usage", 100)
  add_distribution_value("memory_usage", 110)
  
  # Will create a metric "memory_usage" with the mean field value 105
  # Will create a metric "memory_usage" with the count field value 2
  ```

## 1.1.0

_Published on 2024-03-04._

### Added

- [f51f5e4](https://github.com/appsignal/appsignal-python/commit/f51f5e40a814faf1f941dff65fbd7162fc39d5ec) patch - Add histogram support to the OpenTelemetry HTTP server. This allows OpenTelemetry-based instrumentations to report histogram data to AppSignal as distribution metrics.

### Changed

- [0e3733e](https://github.com/appsignal/appsignal-python/commit/0e3733eccac09bc8be4e66ef42f57d4c3561e252) minor - **Breaking change**: Normalize CPU metrics for cgroups v1 systems. When we can detect how many CPUs are configured in the container's limits, we will normalize the CPU percentages to a maximum of 100%. This is a breaking change. Triggers for CPU percentages that are configured for a CPU percentage higher than 100% will no longer trigger after this update. Please configure triggers to a percentage with a maximum of 100% CPU percentage.
- [fdbc92c](https://github.com/appsignal/appsignal-python/commit/fdbc92c1e39f763a21d60dd602170dc18a9ca27a) patch - Make the debug log message for OpenTelemetry spans from libraries we don't automatically recognize more clear. Mention the span id and the instrumentation library.
- [fdbc92c](https://github.com/appsignal/appsignal-python/commit/fdbc92c1e39f763a21d60dd602170dc18a9ca27a) patch - Fix an issue where queries containing a MySQL leading type indicator would only be partially sanitised.
- [0e3733e](https://github.com/appsignal/appsignal-python/commit/0e3733eccac09bc8be4e66ef42f57d4c3561e252) patch - Support fractional CPUs for cgroups v2 metrics. Previously a CPU count of 0.5 would be interpreted as 1 CPU. Now it will be correctly seen as half a CPU and calculate CPU percentages accordingly.
- [ce6ebf2](https://github.com/appsignal/appsignal-python/commit/ce6ebf211549c53b85adf3e19d2cf24fbc09c072) patch - Update bundled trusted root certificates.

### Fixed

- [f8cf85a](https://github.com/appsignal/appsignal-python/commit/f8cf85abf09a70fd919b0f836a4b47ad7fba1fa5) patch - Fix (sub)traces not being reported in their entirety when the OpenTelemetry exporter sends one trace in multiple export requests. This would be an issue for long running traces, that are exported in several requests.

## 1.0.4

### Changed

- [2171910](https://github.com/appsignal/appsignal-python/commit/21719106b8a20a44288758fbce09e67afd1ce308) patch - Fix disk usage returning a Vec with no entries on Alpine Linux when the `df --local` command fails.

### Fixed

- [3215eb4](https://github.com/appsignal/appsignal-python/commit/3215eb49dc76fd7ad3674842015426c0e2763443) patch - Fix missing error metrics for the error rate and error count graphs in some scenarios, like with Node.js Koa apps.

## 1.0.3

### Changed

- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - Improve extraction of OpenTelemetry span details from the Requests library, by using the HTTP method, scheme, host and port as the event name. This improves grouping in the "Slow API requests" performance panel.
- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - Remove extra HTTP attributes from Django root spans.
- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - Remove `route` tag from HTTP server spans. Since the span will already have the route attribute as part of its name, the tag is redundant.
- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - Filter more disk mountpoints for disk usage and disk IO stats. This helps reduce noise in the host metrics by focussing on more important mountpoints.
  
  The following mountpoint are ignored. Any mountpoint containing:
  
  - `/etc/hostname`
  - `/etc/hosts`
  - `/etc/resolv.conf`
  - `/snap/`
  - `/proc/`

### Fixed

- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - Fix an issue where the `method` tag extracted from an incoming HTTP request span would be overriden with the method used for an outgoing HTTP request span.
- [11e205a](https://github.com/appsignal/appsignal-python/commit/11e205a7b13516b972fa7c6dbe1a27fee87e26a1) patch - - Support disk usage reporting (using `df`) on Alpine Linux. This host metric would report an error on Alpine Linux.
  - When a disk mountpoint has no inodes usage percentage, skip the mountpoint, and report the inodes information successfully for the inodes that do have an inodes usage percentage.

## 1.0.2

### Changed

- [7ab8753](https://github.com/appsignal/appsignal-python/commit/7ab87535015f88a6e0d0d5a0ec49885d9593f76c) patch - Bump agent to 1dd2a18.
  
  - When adding an SQL body attribute via the extension, instead of truncating the body first and sanitising it later, sanitise it first and truncate it later. This prevents an issue where queries containing very big values result in truncated sanitisations.
- [addb832](https://github.com/appsignal/appsignal-python/commit/addb832d94ad66a64c2d5e775ac63f1689dc10e6) patch - Bump agent to eec7f7b
  
  
  Updated the probes dependency to 0.5.2. CPU usage is now normalized to the number of CPUs available to the container. This means that a container with 2 CPUs will have its CPU usage reported as 50% when using 1 CPU instead of 100%. This is a breaking change for anyone using the cpu probe.
  
  
  If you have CPU triggers set up based on the old behaviour, you might need to update those to these new normalized values to get the same behaviour. Note that this is needed only if the AppSignal integration package you're using includes this change.

### Fixed

- [1243c3c](https://github.com/appsignal/appsignal-python/commit/1243c3c8011fd2653e140a6054dd402b921dc870) patch - Fix the metadata on the demo CLI's example samples. It will no longer contain unused attributes. The performance sample will report a named `process_request.http` event, rather than report an `unknown` event, in the event timeline.
- [5e91cef](https://github.com/appsignal/appsignal-python/commit/5e91cefa1fcd7602444fcfc0f92011bd5213c963) patch - Fix a crash on the diagnose report when attempting to report the platform for which AppSignal for Python was installed.

## 1.0.1

### Changed

- [4c59581](https://github.com/appsignal/appsignal-python/commit/4c59581d727f551786255804aa55327d41eb2053) patch - Report the agent's architecture and platform in the diagnose report as the "Agent architecture" field. This helps debug if the installed package version matches the host architecture and platform. If they do not match, the package for the wrong architecture is installed.
- [42c12a2](https://github.com/appsignal/appsignal-python/commit/42c12a26c85dc44d5b66ae799aebc6419de9a818) patch - Report the package install path in the diagnose report as the "Package install path" field. This field will help us debug issues related to paths in the diagnose report viewer.
- [c126167](https://github.com/appsignal/appsignal-python/commit/c126167afe5b637b6bfcbb9c769ec7e869392ab5) patch - Report whether the app is running in a container in the diagnose report as the "Running in container" field. This field will help notify us about the environment in which the app is running, as containers have different behavior from more standard Virtual Machines.
- [75f9599](https://github.com/appsignal/appsignal-python/commit/75f95996b8e4eab1157a10fd4daf028307e52693) patch - Bump agent to b604345.
  
  - Add an exponential backoff to the retry sleep time to bind to the StatsD, NGINX and OpenTelemetry exporter ports. This gives the agent a longer time to connect to the ports if they become available within a 4 minute window.
  - Changes to the agent logger:
    - Logs from the agent and extension now use a more consistent format in logs for spans and transactions.
    - Logs that are for more internal use are moved to the trace log level and logs that are useful for debugging most support issues are moved to the debug log level. It should not be necessary to use log level 'trace' as often anymore. The 'debug' log level should be enough.
  - Add `running_in_container` to agent diagnose report, to be used primarily by the Python package as a way to detect if an app's host is a container or not.

## 1.0.0

### Added

- [c1b31b8](https://github.com/appsignal/appsignal-python/commit/c1b31b8e9fac34bf5e5056400fa735295d191cfd) major - Release AppSignal for Python package version 1.0!

  Read our [Python package version 1.0 announcement blog post](https://blog.appsignal.com/2023/10/31/appsignal-monitoring-available-for-python-applications.html)!

  This release marks the 1.0 release of our Python integration and contains the following features:
  
  - Track errors in your app.
  - Track performance of HTTP endpoints and background jobs.
  - Dive into more detail with custom instrumentation.
  - View host metrics for Virtual Machines and containers on which the app is running.
  - Report custom metrics that are unique to your app, and get alerted when they change.
  - Deploy tracking whenever a new version of your application gets deployed.
  - Automatic support for the following frameworks and libraries:
      - Celery
      - Django
      - FastAPI
      - Flask
      - Jinja2
      - Psycopg2
      - Redis
      - Requests
      - Starlette
      - WSGI/ASGI
  
  Please see [our Python package documentation](https://docs.appsignal.com/python) and [guides](https://docs.appsignal.com/guides.html) for more information. Reach out to us on [support@appsignal.com](mailto:support@appsignal.com) if you need any help 👋

### Changed

- [cd360e6](https://github.com/appsignal/appsignal-python/commit/cd360e65220b54b642259248c5c84d1a72e0593a) patch - The diagnose CLI will now print more details about each path in diagnose CLI output, such as if it exists or not, if it's writable and the ownership details. This will help with debugging path related issues without sending the report to the AppSignal servers.
- [bde96cb](https://github.com/appsignal/appsignal-python/commit/bde96cba6aaaefd83f4658d530378c7d5db967fd) patch - Rename the example error reported by our installer and demo CLIs from `ValueError` to `DemoError` to better communicate this is an example error and should not be treated as a real error from the app.
- [4e854df](https://github.com/appsignal/appsignal-python/commit/4e854dfd5b158a4b7d6527dc3004f31fafb3b0fe) patch - Add a message about committing the Push API key in the client file upon generation. We recommend storing this key in environment variables instead or in some kind of separate credentials system instead.

### Fixed

- [05f7f8d](https://github.com/appsignal/appsignal-python/commit/05f7f8dd926dbe20c986deb2b2a986e971afb557) patch - Fix an issue where the installer would always find the push API key to be invalid, halting the installation process.
- [cd360e6](https://github.com/appsignal/appsignal-python/commit/cd360e65220b54b642259248c5c84d1a72e0593a) patch - Fix the diagnose report CLI exiting with an error when a path was not found. When a file, like the `appsignal.log` file, was not found, the diagnose CLI would exit with an error when trying to read from the file. It will now no longer try to read a non-existing file and no longer error.
- [ccd49ad](https://github.com/appsignal/appsignal-python/commit/ccd49ad812a2c79e544c939cf47ae4fc1539136d) patch - Fix the demo error and performance incidents that are reported by our install and demo CLI tools to recognize them by our front-end as examples. It will now show the intended box with some additional explanation that you don't have to worry about these example errors and performance measurements. They're there to test if our integration works in your app and report the first bits of data.

## 0.3.2

### Added

- [48fbe34](https://github.com/appsignal/appsignal-python/commit/48fbe341ff53396faa22832879386db28499a6b3) patch - Add the `--environment` CLI option to the demo CLI tool. This allow you to configure to which app environment the demo samples should be sent. It would default to development (and only be configurable via the `APPSIGNAL_APP_ENV` environment variable), but now it's configurable through the CLI options as well.
  
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
