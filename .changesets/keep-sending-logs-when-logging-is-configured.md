---
bump: patch
type: fix
---

Logs are now still sent after your application configures the logging module. `logging.config.dictConfig()`, `logging.config.fileConfig()` and `logging.basicConfig()` keep AppSignal's log handler attached, so a configuration that sets its own handlers on the root logger, such as Django's `LOGGING` setting, will now send its logs to AppSignal as well.

If you have manually added an OpenTelemetry log handler to your `LOGGING` setting or to the root logger elsewhere, it should now be removed, as AppSignal's handler will now send those log lines as well, causing them to be sent twice. AppSignal will log a warning when it detects a redundant OpenTelemetry handler.