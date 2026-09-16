# ZedBiz Approved Health Notices

These notices were verified on September 16, 2026. Keep them visible under Approved Notices. Stop applying an exception when its exact condition changes.

## OpenClaw Fleet

- `gateway.auth.token` under `core/doctor/security` is an approved retained setting. Its configuration file must remain owner-only and no token value may appear in a report.
- `models.weak_tier` is approved only when it identifies `openai/gpt-6-astra` as below the GPT-5 family. GPT-6 Astra is the approved current model; that version-name comparison is not a failure.

## VPS1 OpenClaw Agents

- The internal `core/doctor/security` LAN-bind warning is approved only while Docker publishes the agent gateway to `127.0.0.1` on the host and the public agent domain continues through the intended Caddy proxy. A host binding of `0.0.0.0`, an unexpected published port, or failed HTTPS check is a new security action.
- `channels.discord.allowlisted_groups.broad_members` is approved only for the existing private agent channels. The Discord guild `@everyone` role was verified as denied `ViewChannel`; only explicit approved user and bot overwrites remain. A new channel, changed permission overwrite, or public visibility is a new security action.

## Rocky

- `core/doctor/skill-workshop-relocation` with one preserved legacy backup root is approved maintenance. The backup ID is `2026-09-01T18-22-51.068Z-a2f06d2b`; OpenClaw state records identify `main` as its owner. The backup differs from Rocky's current Workshop copy and must remain preserved. A second root, different backup ID, damaged manifest, or ownership change is a new finding.
