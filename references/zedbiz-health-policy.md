# ZedBiz Health Classification Policy

Use this policy to classify common OpenClaw and Hermes findings. Keep each finding visible. These rules change its category, not the underlying diagnostic.

## Current Operating Problems

- A gateway, event loop, required scheduler, required model route, or required plugin is currently failing.
- A configured required channel fails its live probe.
- The queue helper finds a failed outbound or incoming delivery inside the report window.
- A required memory feature fails a real supported memory check. A missing setting alone does not prove memory is broken.
- A required configuration is invalid.

## Security Actions

- A critical security finding is `Needs Attention`.
- A non-critical plaintext-secret warning is a security action. Name only the setting path. Never expose the value.
- `gateway.auth.token` is an approved retained ZedBiz setting. Show it under Approved Notices unless its diagnostic code, path, permissions, or exposure changes.
- Any other literal Telegram, API, memory, or service credential remains a security action until it uses a supported secret reference.
- A network-accessible gateway is a security action until the host firewall, reverse proxy, authentication, and intended bind are verified. After verification, record the exact approved notice rather than silently hiding it.
- Shared-user and broad Discord warnings are security actions unless the reported access matches the approved private channel, users, and roles. A heuristic warning alone is not proof of unauthorized access.
- Unpinned plugin versions are supply-chain maintenance unless a known active vulnerability makes them more severe.

## Maintenance Notices

- Oversized or migration-related AGENTS.md and TOOLS.md findings are maintenance unless required instructions are proven truncated or missing during a live run.
- A missing `policy.jsonc` is maintenance unless the organization profile requires the Policy plugin for that agent. If the plugin is intentionally unused, classify it as Not applicable.
- A stale disabled-plugin setting is maintenance.
- A model-tier warning is maintenance when it names the organization's approved current model. Do not treat a version-name comparison as proof that the model is weak.
- A non-critical package advisory is maintenance. A critical advisory is `Needs Attention`; a high advisory remains a security action until reviewed for actual use and exposure.
- An optional command link, local convenience symlink, backup review, or node-onboarding limitation is maintenance.

## Historical Records

- Failed delivery or incoming-message records older than the report window are historical.
- Report their total, oldest date, and newest date.
- Do not retry, resend, delete, or repair them during a health report.
- Historical records never lower the current operating status.

## Not Applicable

- Optional unconfigured providers, channels, plugins, commands, and system packages are Not applicable.
- Not applicable items do not lower the current status and should not appear under What Needs Attention.
