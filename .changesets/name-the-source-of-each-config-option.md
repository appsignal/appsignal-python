---
bump: patch
type: change
---

The `appsignal diagnose` report now names where each configuration option's value came from, so an option that is not what you set says what set it instead. An option holding a value from more than one source lists each one with the value it holds, in the order they are merged.
