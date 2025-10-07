---
bump: minor
type: add
---

Support logging through the external collector experimental feature. When the `collector_endpoint` configuration option is provided, the OpenTelemetry stack will be automatically configured to instrument logs.

The `logging` module will be automatically instrumented, such that log lines emitted through loggers that propagate to the root logger will be automatically sent to AppSignal. To disable this behaviour, add `"logging"` to the `disable_default_instrumentations` configuration option list.