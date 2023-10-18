---
bump: "patch"
type: "fix"
---

Validate the AppSignal configuration before starting the AppSignal agent. This prevents the agent from starting with an invalid config and while reporting no data. To avoid confusion, it will print an error about the invalid configuration upon start. The demo CLI will also more clearly communicate that it could not send any data in this invalid configuration scenario.
