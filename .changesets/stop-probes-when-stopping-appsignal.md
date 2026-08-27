---
bump: patch
type: fix
---

Stop running minutely probes when `stop` is called. Before this change they kept running and kept reporting metrics after AppSignal was stopped.
