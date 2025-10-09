---
bump: minor
type: add
---

Support usage with external collector. When the `collector_endpoint` configuration option is provided, instead of booting up the AppSignal agent bundled with the application, the OpenTelemetry stack will be configured to send data to the given collector.

This is an **experimental** feature. The following functionality is not currently supported when using the collector:

- NGINX metrics
- StatsD metrics
- Host metrics

Some configuration options are only supported when using the agent or when using the collector. A warning will be emitted if a configuration option that is only supported by one is set while using the other.