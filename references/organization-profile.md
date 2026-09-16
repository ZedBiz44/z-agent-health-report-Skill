# Organization Profile

## Organization

- Name: ZedBiz
- Region: Canada, with operating time shown in Mountain Time
- Primary technical repository: https://github.com/ZedBiz44/z-agent-health-report-Skill
- Human operating guide: the Notion Skills database selected by Jack

## Runtime

- Agent platforms: OpenClaw and Hermes
- Skill format: shared `SKILL.md` with `name` and `description` frontmatter
- OpenClaw pilot agents: Terry and Harry
- Hermes pilot agent: Ruby
- Report modes: daily and weekly

## Operating Boundary

- Default operating mode: Get-er-Done for the approved build and pilot
- Health-report behavior: read-only inspection and reporting
- Repairs, restarts, updates, installs, configuration edits, and automatic issue creation: out of scope
- Fleet-level missing-report detection: handled by a separate summary process
- Approved notices: must be reviewed and exact. The retained `gateway.auth.token` warning is approved only while its path, diagnostic, file permissions, and exposure remain unchanged.
- Optional unconfigured services: not applicable and do not lower current operating health
- Saved delivery failures: current only inside the report window; older entries are historical
- VPS1 gateway publication: host loopback only, with public access through the intended Caddy proxy
- VPS1 Discord agent channels: private, with `@everyone` denied `ViewChannel`
- Rocky's single preserved Workshop backup: reviewed and attributed to `main`; preserve it as recovery history

## Sources of Truth

- GitHub: skill logic, files, versions, and change history
- Notion: human-facing SOP, ownership, use, and verification guidance
- Live OpenClaw output: operational proof for each report run

## Security

- Do not store secrets in this repository or the Notion SOP.
- Do not report raw tokens, passwords, private URLs, or full configuration values.
- Keep tests read-only and limited to the commands in `SKILL.md`.

## Rollback

- Preserve any previous deployed copy before replacement.
- If the pilot fails, remove the new skill folder or restore the preserved copy.
- Verify the agent returns to its prior runtime state.



