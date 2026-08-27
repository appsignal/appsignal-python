---
bump: patch
type: fix
---

Apply the `ca_file_path` and `http_proxy` configuration options to the data sent to a collector. Before this change both options were only applied to the data sent by the agent, so a custom certificate authority file or a proxy had no effect when a collector was used.
