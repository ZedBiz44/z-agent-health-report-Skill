---
name: z-agent-health-report
description: Run safe daily or weekly OpenClaw or Hermes health checks and return a short report without repairing or changing the agent.
---

# Z Agent Health Report

Run a small set of read-only OpenClaw or Hermes checks and return a plain-language health report for the current agent.

## Use This Skill When

- The user asks for an agent health report, daily health check, or weekly health check.
- A trusted schedule explicitly asks for the daily or weekly report.
- The request is to inspect and report, not repair.

Do not use this skill for host, Docker, firewall, backup, billing, or operating-system audits. Do not use it to prove that every external API, business workflow, or installed skill works. A separate fleet-summary process should identify missing agent reports.

## Required Input

- Report mode: `daily` or `weekly`.
- Runtime platform: `OpenClaw` or `Hermes`. Use the current agent profile or available executable to identify it. Do not guess or run commands for the wrong platform.
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
- Run at most one health report on a given agent at a time. If one is already running, wait; do not launch an overlapping report.
- Normal command logs, session records, and delivery of the requested report are expected side effects.
- Redact secrets, credentials, private URLs, and raw configuration values from the report.
- If a check suggests a repair, report the finding and stop. A separate authorized task must handle the repair.

End every report with: `No changes were made.`

## Choose the Platform Checks

- Use the OpenClaw commands only when the current runtime is OpenClaw.
- Use the Hermes commands only when the current runtime is Hermes.
- If neither platform can be confirmed, mark every platform check `Not checked`, explain why, and stop without improvising commands.

## OpenClaw Daily Report

Run each command once and keep the results separate:

```text
openclaw doctor --json
openclaw security audit --json
openclaw health --json --timeout 10000
openclaw channels status --probe --json --timeout 10000
```

## OpenClaw Weekly Report

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

## Hermes Daily Report

Run each command once and keep the results separate:

```text
hermes status --all
hermes doctor
hermes gateway status --deep
```

Do not use `hermes doctor --fix` or `hermes doctor --live`. The live option makes real external calls and is outside this lean report.

## Hermes Weekly Report

Run each command once and keep the results separate:

```text
hermes status --all --deep
hermes doctor
hermes gateway status --deep
hermes security audit
hermes skills list
hermes cron status
hermes --version
```

The Hermes security audit makes a read-only request to the public OSV vulnerability database. The skill and cron checks report loading or scheduler problems; they do not change either system.

## Interpret Each Check

Use one result for every command:

- `Passed`: the command returned valid output and its required health condition passed.
- `Finding`: the command ran, but it reported a non-critical problem or warning.
- `Failed`: the command could not run, returned unusable output, or a required health condition failed.
- `Not checked`: the installed OpenClaw version does not support the command, the check could not safely run, or the runtime truncated or discarded part of a successful result before it could be interpreted.

Apply these rules:

- For `doctor`, read the JSON `ok` value and findings. Valid output with `ok: false` and only non-critical warnings is `Finding`, not `Failed`. Use `Failed` when the command cannot run, the JSON is invalid, or an error-level or critical diagnostic makes the required check unusable. A successful exit code does not make an `ok: false` result healthy.
- For `security audit`, report the severity and a short safe summary of each finding. Never include sensitive values.
- For `health`, require valid JSON with `ok: true`. Treat a connection failure or `ok: false` as `Failed`. Summarize the gateway, event loop, plugin-error count, and channel readiness without exposing session paths or configuration values.
- For `gateway status --deep`, report service-discovery findings separately. It is not a substitute for the live gateway health check.
- For channel status, treat a failed probe for any configured, required channel as `Failed`. List optional or intentionally disabled channels separately if the output identifies them.
- For `plugins list`, report loading errors, missing dependencies, disabled status, and diagnostics. Do not claim an external integration was functionally tested.
- For `config validate`, invalid configuration is `Failed`.
- For `openclaw --version`, record the version without comparing it to an unverified latest version.
- For `hermes status`, require the configured primary provider, required Discord connection, and gateway service to be available. Optional unconfigured providers or channels are not findings.
- For `hermes doctor`, report active security advisories, configuration errors, missing required packages, unhealthy supervision, required-tool failures, and the final issue count. Optional providers and tools are not findings unless the organization profile marks them required.
- For `hermes gateway status --deep`, treat a stopped or unreachable gateway as `Failed`. A running supervised or intentionally container-managed gateway passes even when it is not installed as a host system service.
- For `hermes security audit`, report critical, high, moderate, and unknown findings by package and advisory ID. A critical finding is `Failed`; lower severities are `Finding` unless an approved notice matches exactly.
- For `hermes skills list`, report load failures or disabled required skills. Do not treat intentionally disabled optional skills as findings.
- For `hermes cron status`, require the scheduler to be running when scheduled reports are expected.
- For `hermes --version`, record the installed version without comparing it to an unverified latest version.
- If a command succeeded but its output was not fully retained, use `Not checked`, explain that the result was incomplete, and do not turn the missing evidence into a health failure.
- Continue with independent checks after one check fails. Do not improvise another command.

## Approved Notices

An approved notice is a reviewed, exact exception that is safe to show without lowering the overall status.

- Match the exact check and diagnostic code.
- Show every match under `Approved notices`.
- If the wording, code, severity, or affected component changes, treat it as a new finding.
- Never approve a critical security finding, failed live gateway health check, failed required-channel probe, or invalid configuration.

## Overall Status

Use exactly one status:

- `Needs Attention`: any critical security finding, failed live gateway or scheduler health check, failed required-channel probe, invalid configuration, or other required check is `Failed`.
- `Warning`: no required check failed, but at least one non-approved finding or `Not checked` result remains.
- `Healthy`: every required check passed, with only exact approved notices allowed.

When status is `Healthy`, say: `All required checks passed within this report's scope.`

## Report Format

Keep the report short and use Mountain Time.

Return the complete report in the current reply. If the user says not to deliver it to a channel, do not use a channel-delivery tool, but still return the full report to the current caller. Never replace the report with only a completion note.

```markdown
# Agent Health Report

**Agent:** [name or ID]
**Runtime:** [OpenClaw gateway or Hermes runtime safe label]
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

- The report names the current agent, platform, and safe runtime label.
- Every required command has one check result.
- Failed checks are not hidden as warnings.
- Approved notices are exact matches and still visible.
- The overall status follows the rules above.
- The report does not claim that unrelated skills, hosts, or external workflows were tested.
- The current reply contains the complete report, not only a completion note.
- The final line says `No changes were made.`


