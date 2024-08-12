---
bump: patch
type: add
---

Add helper to manually stop the agent process for this AppSignal instance.

Some contexts, like serverless functions, exit before AppSignal can ensure all data is sent to our servers. To ensure the data is sent, the new `appsignal.stop()` method can be called to gracefully stop the AppSignal agent process.
