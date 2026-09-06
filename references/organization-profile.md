# Organization Profile

## Organization

- Name: ZedBiz
- Region: Canada, with operating time shown in Mountain Time
- Primary technical repository: https://github.com/ZedBiz44/z-agent-health-report-Skill
- Human operating guide: the Notion Skills database selected by Jack

## Runtime

- Agent platform: OpenClaw
- Skill format: shared `SKILL.md` with `name` and `description` frontmatter
- Pilot agents: Terry and Harry
- Report modes: daily and weekly

## Operating Boundary

- Default operating mode: Get-er-Done for the approved build and pilot
- Health-report behavior: read-only inspection and reporting
- Repairs, restarts, updates, installs, configuration edits, and automatic issue creation: out of scope
- Fleet-level missing-report detection: handled by a separate summary process
- Approved notices: must be reviewed, exact matches; none are assumed by default

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


