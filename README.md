# z-agent-health-report

Version: 0.1.1

This repository is the technical source of truth for the ZedBiz agent health-report skill. It gives an OpenClaw agent a lean, read-only daily or weekly health check and a short human-readable report.

## What It Does

- Runs an approved set of OpenClaw health commands.
- Separates passed checks, findings, failures, and checks that could not run.
- Uses clear `Healthy`, `Warning`, or `Needs Attention` status.
- Reports exact approved notices without hiding them.
- Makes no intentional configuration or service changes.

## What It Does Not Do

- It does not repair, restart, update, install, or reconfigure anything.
- It does not audit the VPS host, Docker, firewall, backups, billing, or operating system.
- It does not prove that every skill, plugin, external API, or business workflow works.
- It does not decide whether an expected agent report is missing.
- It does not automatically create GitHub issues.

## Installation

Install the `z-agent-health-report` folder in the target agent's workspace skills directory. Preserve the folder name exactly.

Restart or reload only when the target runtime requires it and the operator is authorized to do so. Verify discovery from a fresh agent session after deployment.

## Usage

Ask the agent for one mode:

- `Run the daily agent health report.`
- `Run the weekly agent health report.`

The agent should return the report defined in [SKILL.md](SKILL.md) and make no repairs.

## Validation

Validate the repository with the current `z-ai-skill-developer` validator:

```text
python scripts/validate_skill.py <path-to-z-agent-health-report-folder>
```

Also test from fresh agent sessions. A file-exists check is not sufficient proof that the skill is discoverable and usable.

## Operating Guidance

The Notion SOP is the human operating guide. This GitHub repository remains authoritative for the skill instructions and change history.

Build and pilot work is tracked in [GitHub issue #1](https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/1).

