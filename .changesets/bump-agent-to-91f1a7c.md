---
bump: "patch"
type: "change"
---

Bump agent to 91f1a7c

- Fall back on the revision option for OpenTelemetry endpoint from config, rather than only read it from the OpenTelemetry resource attributes.
- Fix agent restart when the config changes, not detecting a config change and not starting a new agent process.
- Retry agent servers port binding when port is busy. This fixes Python package restarting the agent when another agent instance is still running.
