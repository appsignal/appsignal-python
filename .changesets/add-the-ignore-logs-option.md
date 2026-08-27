---
bump: minor
type: add
---

Add an `ignore_logs` option, which takes a list of patterns. Log lines that match any of the patterns are not sent to AppSignal. Set it with the `APPSIGNAL_IGNORE_LOGS` environment variable, or as an option on the `Appsignal` client. Read our [ignore logs guide](https://docs.appsignal.com/guides/filter-data/ignore-logs.html) for the patterns that are supported.

This option only has an effect in collector mode, because that is the only mode in which this package sends logs.
