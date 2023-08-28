---
bump: "minor"
type: "add"
---

Support OpenTelemetry metrics through its metrics exporter. We enable the metrics exporter by default so it can be used to collect data from instrumentations and manually by using an OpenTelemetry metrics meter. Not all metric types are supported at this time, only sums and gauges.
