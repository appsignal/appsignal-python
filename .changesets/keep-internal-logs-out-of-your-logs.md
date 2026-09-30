---
bump: patch
type: fix
---

When `disable_default_instrumentations` is used to disable the `logging` instrumentation, prevent the log lines emitted internally by AppSignal from propagating to a manually configured OpenTelemetry handler in the root logger.
