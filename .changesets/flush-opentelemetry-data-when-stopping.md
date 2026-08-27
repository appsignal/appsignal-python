---
bump: patch
type: fix
---

Send the traces, metrics and logs that are still buffered when `stop` is called, instead of dropping them.
