---
name: schieber-build
description: Orchestrator for Schieber card-game development. Coordinates `schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer` agents. Trigger for any Schieber build/implement/fix/test work — "implement next task", "finish Schieber", "continue the frontend", "add websocket endpoint", "fix the trump phase", "run QA on Schieber", "review the game session", and all rerun / refine / iterate / update / modify variants of the above. Also trigger on "Schieber" + test/smoke/integration. Do NOT trigger for pure questions answered from the codebase (rule lookups, protocol lookups) — answer those directly.
---

# Schieber Build Orchestrator

Coordinates the 4-agent team (`schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer`) through a batch of plan tasks from `docs/superpowers/plans/2026-04-13-schieber-html5-frontend.md`.

**Execution mode: hybrid.** Backend + frontend run as an **agent team** in the build phase (parallel with inter-agent messaging). QA and reviewer run as **single subagents** after build.

## Phase 0: Context Check

Before dispatching anything:

1. Check if `_workspace/` exists under project root.
2. **Detect task completion from BOTH plan checkboxes AND commit log.** Plan checkboxes drift — authors commit code without ticking boxes. Read `git log --oneline` and compare commit subjects (`feat: add trick loop and run() to GameSession`) to plan task titles. If a task's deliverable appears in a commit subject, treat the task as done regardless of checkbox state. Report any mismatch.
3. Decide mode:
   - **Initial run** — no `_workspace/`, no work items queued yet → start fresh.
   - **Continuation** — `_workspace/` present, next plan task(s) ready → read latest `_workspace/*.md` artifacts for context, continue from the next uncompleted task.
   - **Partial re-run** — user asks to redo a specific task/module → move `_workspace/` → `_workspace_prev/`, rerun only the affected agent(s).
   - **New batch** — user gives a fresh scope outside the plan → treat as initial run, create plan addendum if needed.
   - **Audit-first** — when the plan appears complete but no QA verification exists: before dispatching any build agent, spawn the QA agent to establish current state. Finding false-positive defects later is costlier than an up-front audit.
4. **Protocol skill sanity check** — before trusting `schieber-protocol` as ground truth, verify it against actual `send_json`/`receive_json` call sites in `ausbau/game_session.py` AND the frontend dispatch. A skill written from the plan (not from code) is aspirational, not factual — reconcile to reality first. When both backend and frontend agree on a shape that differs from the skill, the skill is the thing to update, not the code.

Report mode chosen to the user in one sentence before starting.

## Phase 1: Scope

Determine the batch of plan tasks for this run. Default batch size: **2–4 tasks** (keeps QA scope manageable).

1. Read current plan progress.
2. Pick next batch.
3. Split tasks by agent:
   - Backend-only tasks (7, 8, 9 for example): to `schieber-backend`.
   - Frontend-only tasks (13, 14): to `schieber-frontend`.
   - Mixed tasks (10, 15): split — decide which file goes where.

## Phase 2: Team Build

Choose execution mode based on coordination needs:

- **Parallel subagents (default when skill-as-contract is sufficient):** spawn `schieber-backend` and `schieber-frontend` via two parallel `Agent` tool calls with `run_in_background: true` and `model: "opus"`. When the shared protocol skill is authoritative and complete, the agents do not need to talk mid-work — they read the same contract and deliver. This was the dominant pattern across the first four batches of this project and it worked well.
- **Agent team (when mid-work coordination matters):** use `TeamCreate` with both members, then `TaskCreate` per plan task. Pick this when protocol changes are expected during the batch and the two agents need to negotiate shapes live via `SendMessage` (`PROTOCOL_DELTA` / `PROTOCOL_Q`).

Default to parallel subagents. Upgrade to team mode only when you can point at a specific coordination need.

Monitor for completion. When both agents report done, proceed.

**Artifacts produced:**
- `_workspace/{N}_backend_note.md` — backend summary: files changed, tests added, protocol deltas.
- `_workspace/{N}_frontend_note.md` — frontend summary: files changed, handlers, UX notes.

`N` = batch index (0-padded two digits).

## Phase 3: QA (Subagent)

**Execution mode:** single subagent. After Phase 2 completes (team or parallel subagents), spawn `schieber-qa` via `Agent` tool with `model: "opus"`. If Phase 2 used team mode, `TeamDelete` first.

Pass QA the batch scope and pointers to backend/frontend notes. QA writes `_workspace/{N}_qa_report.md` and returns verdict: GREEN / YELLOW / RED.

- **RED**: blocker defects. Return to Phase 2 — spawn a new team with scoped fix instructions drawn from the QA report. Loop until GREEN or YELLOW.
- **YELLOW**: non-blocker defects. Proceed to Phase 4 but surface defects for the user's decision.
- **GREEN**: proceed to Phase 4.

**Orchestrator in-flight completion.** If QA reports a *trivial* gap (one- or two-file edit, no design question, clear fix path), the orchestrator MAY apply the fix directly and add a test rather than re-dispatching. Thresholds:
- OK to fix directly: normalizing a field value across two call sites, adding one return-tuple element, removing an unused import, fixing a single test assertion.
- NOT OK to fix directly: changing protocol semantics, adding new message types, any change that spans more than two files, any change requiring a judgment call about game rules.
When in doubt, re-dispatch the backend or frontend agent with a narrow scope — that preserves ownership.

## Phase 4: Review (Subagent, optional by batch type)

Whether to invoke the reviewer depends on the batch:

- **Skip for skill-only batches** (no code change). The reviewer adds no value when the only files touched are `.claude/skills/*.md` — the QA cross-boundary audit already validated agreement with code.
- **Skip for tooling-only batches** (e.g. `run_tests.py`, CI config) unless the change affects test semantics.
- **Skip for one-file trivial fixes** completed by orchestrator in-flight per Phase 3.
- **Invoke for every code-change batch that touches backend OR frontend code.** These are where plan drift, game-rule errors, and test-coverage gaps hide.

When invoking: spawn `schieber-reviewer` via `Agent` tool with `model: "opus"`. Pass the batch scope, QA report, and diff range. Reviewer writes `_workspace/{N}_review.md` and returns APPROVE or REQUEST_CHANGES.

- **REQUEST_CHANGES** with BLOCKER findings: return to Phase 2 scoped fix.
- **REQUEST_CHANGES** with only MAJOR / MINOR / NIT: surface to user, ask whether to address now or defer.
- **APPROVE**: proceed to Phase 5.

## Phase 5: Commit & Plan Update

1. **Defensive staging.** Run `git status --short` before staging. If any files are already staged or modified that are outside this batch (pre-existing user work, unrelated WIP), do NOT use `git add -A` or `git add .` — list the exact paths belonging to this batch and `git add` only those. If you accidentally sweep an unrelated file into a commit, use `git reset --soft HEAD~1` + `git restore --staged <path>` to fix before pushing.
2. Create git commit per plan convention (see plan file — each task has its own commit message). One batch may produce one or several commits depending on logical scope; prefer one commit per defect or per plan task.
3. Tick the `- [x]` boxes in the plan file for completed tasks. Use `sed -i 's/^- \[ \] /- [x] /g' <plan.md>` only when you are confident every step of every listed task is complete — otherwise edit the specific lines.
4. Report to user: tasks completed, defects open, next batch recommended.

## Phase 6: Feedback

Ask user: "Anything about the flow, agent behavior, or protocol to adjust?" If yes, update the relevant agent/skill file and record the change in CLAUDE.md's harness changelog.

## Data Flow

- **Shared contract:** `schieber-protocol` skill (WebSocket), `schieber-game-rules` skill (game logic). All agents read these.
- **Inter-agent messaging (Phase 2):** `SendMessage` for `PROTOCOL_DELTA` / `PROTOCOL_Q` / "ready for QA".
- **Task tracking (Phase 2):** `TaskCreate` per plan task, dependencies between backend and frontend where protocol overlaps.
- **Artifacts:** `_workspace/` under project root. Naming: `{NN}_{agent}_{kind}.md`. Examples: `03_backend_note.md`, `03_qa_report.md`, `03_review.md`.
- **Reviewer independence:** reviewer only sees workspace artifacts and the git diff, never the live agents.

## Error Handling

| Situation | Action |
|-----------|--------|
| Agent test suite fails | Agent re-attempts once; second failure — report to orchestrator, pause, ask user. |
| Protocol skill ambiguous | Backend proposes amendment in its note, orchestrator confirms with user before adopting. |
| QA flags a skill gap | Update the skill file in a separate step; note the update in CLAUDE.md changelog. |
| Smoke test needs running server | Backend spawns `uvicorn` in background; QA connects. If port 8765 busy, use 8766. |
| `_workspace/` collision with prior partial run | Move to `_workspace_prev/` before new run, do not delete. |
| Two teammates disagree on field semantics | Orchestrator reads the skill, issues a ruling, records as note in `_workspace/{N}_ruling.md`. |

## Test Scenarios

### Happy path
User: "continue Schieber — do tasks 7 and 8".
→ Phase 0 reads `_workspace/` (continuation), Phase 1 picks tasks 7 (Weis) and 8 (trick loop), both backend.
→ Phase 2 spawns backend agent only (no frontend work needed for 7/8). Team of 1 is fine — actually degenerate to subagent direct call.
→ Phase 3 QA. Phase 4 review. Phase 5 commits. User notified.

### Protocol change path
User: "add a `can_undo` field to `your_turn`".
→ Phase 0 new batch.
→ Phase 1 scope = backend (server-side) + frontend (handler) + protocol skill update.
→ Phase 2 team. Backend updates skill FIRST, sends `PROTOCOL_DELTA` to frontend. Frontend updates handler.
→ Phase 3 QA verifies both sides read same field.
→ Phase 4 review. Commit.

### Failure path
QA reports BLOCKER: backend sends `trick_end.winner` as internal key but frontend reads display name.
→ Orchestrator returns to Phase 2 with scoped fix: "backend: align `trick_end.winner` with protocol skill (display name)". Re-run QA. Loop until GREEN.

## Team Size

For Schieber this harness: 2 active build members (backend + frontend) plus 2 sequential subagents (QA, reviewer). Do not exceed 3 build members — the domain does not split finer.
