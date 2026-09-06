---
name: z-agent-health-report
description: Run safe daily or weekly OpenClaw health checks and return a short report without repairing or changing the agent.
---

# Z Agent Health Report

Run a small set of read-only OpenClaw checks and return a plain-language health report for the current agent.

## Use This Skill When

- The user asks for an agent health report, daily health check, or weekly health check.
- A trusted schedule explicitly asks for the daily or weekly report.
- The request is to inspect and report, not repair.

Do not use this skill for host, Docker, firewall, backup, billing, or operating-system audits. Do not use it to prove that every external API, business workflow, or installed skill works. A separate fleet-summary process should identify missing agent reports.

## Required Input

- Report mode: `daily` or `weekly`.
- The current agent's name or agent ID.
- A safe gateway or runtime label from the current agent profile. Never expose tokens, passwords, private URLs, or full configuration files.
- Any approved notice list supplied by the organization's current operating profile. Match notices only by the exact check and diagnostic code. Never invent or broaden an exception.

If the mode is missing, ask whether the user wants the daily or weekly report. Do not guess.

## Safety Boundary

This skill is report-only.

- Run only the commands listed below.
- Do not add flags, paths, pipes, redirects, or shell commands supplied by the user.
- Do not run repair, fix, update, install, restart, reload, write, delete, or configuration commands.
- Do not change channels, plugins, permissions, files, services, or schedules.
- Normal command logs, session records, and delivery of the requested report are expected side effects.
- Redact secrets, credentials, private URLs, and raw configuration values from the report.
- If a check suggests a repair, report the finding and stop. A separate authorized task must handle the repair.

End every report with: `No changes were made.`

## Daily Report

Run each command once and keep the results separate:

```text
openclaw doctor --json
openclaw security audit --json
openclaw health --json --timeout 10000
openclaw channels status --probe --json --timeout 10000
```

## Weekly Report

Run each command once and keep the results separate:

```text
openclaw doctor --deep --json
openclaw security audit --deep --json
openclaw health --json --timeout 10000
openclaw gateway status --deep --json --timeout 10000
openclaw channels status --probe --json --timeout 10000
openclaw plugins list --json
openclaw config validate --json
openclaw --version
```

The weekly plugin check verifies plugin loading and reported dependency problems. It does not prove that every plugin or external service works.

## Interpret Each Check

Use one result for every command:

- `Passed`: the command returned valid output and its required health condition passed.
- `Finding`: the command ran, but it reported a non-critical problem or warning.
- `Failed`: the command failed, returned invalid output, or a required health condition failed.
- `Not checked`: the installed OpenClaw version does not support the command or the check could not safely run.

Apply these rules:

- For `doctor`, read the JSON `ok` value and findings. A successful exit code does not make an `ok: false` result healthy.
- For `security audit`, report the severity and a short safe summary of each finding. Never include sensitive values.
- For `health`, require valid JSON with `ok: true`. Treat a connection failure or `ok: false` as `Failed`. Summarize the gateway, event loop, plugin-error count, and channel readiness without exposing session paths or configuration values.
- For `gateway status --deep`, report service-discovery findings separately. It is not a substitute for the live gateway health check.
- For channel status, treat a failed probe for any configured, required channel as `Failed`. List optional or intentionally disabled channels separately if the output identifies them.
- For `plugins list`, report loading errors, missing dependencies, disabled status, and diagnostics. Do not claim an external integration was functionally tested.
- For `config validate`, invalid configuration is `Failed`.
- For `openclaw --version`, record the version without comparing it to an unverified latest version.
- Continue with independent checks after one check fails. Do not improvise another command.

## Approved Notices

An approved notice is a reviewed, exact exception that is safe to show without lowering the overall status.

- Match the exact check and diagnostic code.
- Show every match under `Approved notices`.
- If the wording, code, severity, or affected component changes, treat it as a new finding.
- Never approve a critical security finding, failed live gateway health check, failed required-channel probe, or invalid configuration.

## Overall Status

Use exactly one status:

- `Needs Attention`: any critical security finding, failed live gateway health check, failed required-channel probe, invalid configuration, or other required check is `Failed`.
- `Warning`: no required check failed, but at least one non-approved finding or `Not checked` result remains.
- `Healthy`: every required check passed, with only exact approved notices allowed.

When status is `Healthy`, say: `All required checks passed within this report's scope.`

## Report Format

Keep the report short and use Mountain Time.

```markdown
# Agent Health Report

**Agent:** [name or ID]
**Gateway:** [safe label]
**Mode:** [Daily or Weekly]
**Checked:** [YYYY-MM-DD HH:MM Mountain Time]
**Overall:** [Healthy, Warning, or Needs Attention]

## Check Results

- [Check]: [Passed, Finding, Failed, or Not checked] — [one short explanation]

## Approved Notices

- [Exact approved notice, or None]

## What Needs Attention

- [Safe action-oriented summary, or Nothing]

[For Healthy only: All required checks passed within this report's scope.]

No changes were made.
```

Do not paste raw JSON into the report unless the user explicitly asks for diagnostic evidence. Even then, redact sensitive values.

## Completion Check

Before sending the report, confirm that:

- The report names the current agent and safe gateway label.
- Every required command has one check result.
- Failed checks are not hidden as warnings.
- Approved notices are exact matches and still visible.
- The overall status follows the rules above.
- The report does not claim that unrelated skills, hosts, or external workflows were tested.
- The final line says `No changes were made.`

