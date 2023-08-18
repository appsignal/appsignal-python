---
bump: "patch"
type: "add"
---

Add the OpenTelemetry HTTP server port config option (`opentelemetry_port`) to configure on which port the `appsignal-agent` server process will listen for OpenTelemetry data from the HTTP exporter. This can be used to configure two apps on the same machine to use different ports so it's possible to run two AppSignal apps on the same machine.
