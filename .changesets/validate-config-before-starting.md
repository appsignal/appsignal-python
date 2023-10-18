---
bump: "patch"
type: "fix"
---

Validate the AppSignal configuration before starting the AppSignal agent. This prevents the agent from starting with an invalid config and while reporting no data. The AppSignal client and demo CLI will communicate that they could not send any data in this invalid configuration scenario.
