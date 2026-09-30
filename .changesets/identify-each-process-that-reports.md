---
bump: patch
type: fix
---

Metrics are reported correctly when several processes of your application send the same metric, including processes forked after AppSignal starts. Each process reports under a `service.instance.id` and a `process.pid` of its own, which is what AppSignal uses to tell them apart.
