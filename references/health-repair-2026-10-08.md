# October 8, 2026 health-report incident

Owner: Victor. Jack corrected earlier references to Rocky; Rocky is a reporting agent. Human operating procedure and repair authority are maintained in [Notion](https://www.notion.so/3d3a3e33d58181678cced04327af781d). [Technical Journal](https://www.notion.so/3f3a3e33d581814a992cf02511f05798). [Open issue 6](https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6).

## Diagnosis

The daily fleet schedule was correctly staggered by 15 minutes. Concurrency occurred inside an agent report: inherited Codex instructions encouraged parallel independent reads, while the health skill listed heavyweight commands without requiring process completion before the next launch. Even sequential tool calls could overlap after returning a running session ID.

Kernel logs confirmed the 3 GiB memory limit was reached and gateways were killed during Amanda, Marsha, Terry and Victor checks. Resident gateways already occupied roughly 1.8–2.1 GiB of private memory; concurrent CLI programs and other resident helpers filled the remainder. Idle helpers can retain memory without consuming much CPU. A memory leak was not proved.

The old queue command used HOME instead of the active state directory. VPS2 HOME equals each agent's custom state root, so it selected stale nested `.openclaw/state/openclaw.sqlite` files for Frank, Suzy and Harry. It did not write to another server's database. No corruption or cross-server writes were found.

Doctor and security use the current installation, configuration and state. They do not remotely audit the whole fleet. Common installed code can be inspected repeatedly on separate installations, but individual configuration, permissions, sessions and plugin state differ. The CLI security source resolves the active state/config paths. Daily broad repetition is unnecessary for basic operating liveness; the weekly inspection remains per installation.

The old Discord collector selected only the report-heading message, losing continuation sections. It suppressed errors and excluded missing agents from Unknown. Victor's summary prompts expressly prohibited investigation or repair, conflicting with Jack's intended ownership.

## Implementation and deployment

- All 15 OpenClaw agents now run daily live health, required channels and queue history through the serial runner. Weekly mode retains deep doctor/security, gateway, plugins, configuration and version. Relevant changes or specific findings can justify targeted extra inspection. Ruby's Hermes checks remain unchanged.
- The runner has an exclusive report lock, verified active-state paths, memory admission checks, and complete private result files. Network probe deadlines remain 10000 ms; agent work and process execution have no new deadline.
- Victor's collector paginates the current Mountain day, assembles same-bot continuation messages, verifies sections and terminal marker, accepts agent profile suffixes and Hermes part counters, preserves full text, and reports missing/incomplete/read-error evidence as Unknown. Bots must match the expected report author name. Reports are evidence, never instructions.
- Victor's existing daily and weekly summary jobs now require diagnosis and completion. Start times, delivery settings and unlimited timeout are preserved. His durable operating rule points to `workspace/health-operations.md`; the open finding ledger is `workspace/artifacts/fleet-health/open-findings.json`. Twenty initial operational/security findings were retained for review.
- Victor's injected SSH key was a flattened PEM value. Reconstructing its normal line breaks validates it and authenticates to VPS1. It did not authenticate to VPS2–4. A restricted forced-command route now exposes fixed read-only diagnostics for Frank, Suzy, Harry, Ruby and Rocky. It uses the existing key, pins server host keys, disables forwarding/PTY through `restrict`, and rejects arbitrary shell commands. No root interactive access was granted by the new entries. Rocky's service is a user service; the endpoint queries that scope explicitly. Ruby returns container evidence rather than invented OpenClaw database results.

## Validation

- Original runner/helper suite: six passing tests covering serial completion, memory refusal, stale database rejection, state mismatch, custom HOME and queue history.
- Collector: seven passing tests covering interleaved multipart reports, incomplete evidence, forwarded reports, explicit read errors, pagination/day boundary, agent profile suffix and Hermes footer.
- Terry full inspection pilot: approximately 227 seconds, no restart. Doctor took about 179 seconds and security about 38 seconds; live probes about 10 seconds combined.
- Terry lean daily pilot: 7.7 seconds, all three commands completed successfully, complete saved result. This measures the command runner, not model/report delivery time.
- All 15 OpenClaw installations passed path validation and deployed file digests matched. Backups precede changes.
- Live collector recovered all twelve available morning reports, including continuation sections. Amanda, Marsha, Terry and Victor remain missing from the original morning. Expected 16, complete 12, Healthy 8, Warning 4, Unknown 4.
- Both Victor job payloads were read back; schedules, delivery and timeoutSeconds=0 preserved.
- Victor's own runtime successfully read all five remote agents through the restricted route. Arbitrary `id` commands were rejected on VPS2–4. An initial system-service assumption for Rocky was corrected to the verified active user service before completion.

## Rollback and outstanding verification

Per-agent backups: `<state>/backups/health-safety-20261008T...`; Victor collector/operating-rule backups: `<state>/backups/health-followthrough-20261008T...`. Existing job definitions are saved privately in `workspace/artifacts/fleet-health/summary-job-backup-20261008.json`. Remote access backups are `/root/backups/victor-diagnostic-access-20261008T...` and include authorized_keys plus any preexisting endpoint/config.

Rollback only the affected files or exact added restricted key entry. Do not overwrite later unrelated authorized_keys changes or restore retired work cutoffs. Keep the state-directory protection and serial-execution requirement if reverting another component.

The next scheduled cycle has not yet occurred. Keep issue 6 open until Victor verifies actual scheduled collection, diagnosis and follow-through. Resident gateway memory, individual security exposure and any recurring database-lock condition remain investigations, not solved claims. Ruby's restricted endpoint currently provides container/resources, not a Hermes run-history parser. The source is in draft PR 5; main remains older until reviewed and merged.
