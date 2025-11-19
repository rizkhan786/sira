
Macro: Do Phase Completion
Objective: Validate all outputs across the phase, roll up results, and formally close the phase.

How to run: Tell Agent: Do Phase Completion

Steps
- Phase Gate Check (required)
  - Run a full consistency check across REQs, DELs, ACs, and TCs.
  - Output → docs/60-Quality/phase-completion-report.md.
  - Block completion until issues are resolved.
- Rollup Outcomes (required)
  - Update docs/50-Completion/phase-outcomes.md with KPIs including both quantitative metrics (like velocity, defect density, test coverage) and qualitative insights (like stakeholder feedback and team satisfaction), along with sprint summaries and lessons learned.
  - Highlight unresolved risks and open items to carry into the next phase.
  - Explicitly list any unmet ACs or TCs and ensure they are re-linked into the next phase backlog.
  - Update PROJECT_PLAN.md with phase summary.
- Archive & Tag (required)
  - Move completed DELs into docs/30-Planning/archives/ (keep a brief index if useful).
  - When moving DELs into archives, ensure traceability links (REQ ⇄ DEL ⇄ AC ⇄ TC) are preserved in the archived index.
  - Tag repository with a phase marker (e.g., phase-1.0).

# WARP Playbook (Project Operational Protocols)

This playbook defines the minimum process to plan, execute, and complete sprints. Use the macro protocols below:
- Do Phase Planning
- Do Sprint Planning
- Do Sprint Execution
- Do Sprint Completion
- Do Phase Completion
- Debug Issue

Macro: Debug Issue
Objective: Systematically diagnose, fix, and verify resolution of defects or unexpected behavior in containerized environments.

How to run: Tell Agent: Debug Issue [brief description]

Steps
1) Issue Capture & Analysis (required)
   - Document the issue in docs/60-Quality/debug-log.md with timestamp, environment, and symptoms.
   - Identify affected components (frontend, backend, database, etc.).
   - Record error messages, logs, and reproduction steps.
   - Tag the issue with severity: Critical, High, Medium, Low.

2) Environment Verification (required)
   - Ensure issue is reproduced in the appropriate Docker Desktop environment (Dev or Test).
   - Check container health status and resource utilization.
   - Capture container logs and environment variables state.
   - Verify .env configuration and secrets are properly loaded.

3) Diagnostic Deep Dive (required)
   - Leverage available testing frameworks and tools:
     * Chrome DevTools MCP for web application debugging
     * Container logs and Docker Desktop diagnostics
     * PyTorch debugging tools (if ML components involved)
     * Database query analyzers (if data issues)
     * API endpoint testing with proper authentication
   - Run targeted test cases to isolate the root cause.
   - Check traceability: does the issue relate to specific REQ/DEL/AC/TC?

4) Fix Implementation (required)
   - Implement fix in the appropriate containerized environment.
   - Update related documentation (ADRs, code comments, etc.).
   - If the fix affects existing ACs or TCs, update docs/40-Testing/ accordingly.
   - Ensure fix doesn't break existing functionality.

5) Verification & Testing (required)
   - Re-run the original failing test case to confirm resolution.
   - Execute full regression test suite in Docker Desktop Test profile.
   - Verify all related ACs still pass.
   - Test in both Dev and Test environments to ensure consistency.
   - Document test results in docs/60-Quality/debug-log.md.

6) Resolution Documentation (required)
   - Update debug-log.md with resolution details and lessons learned.
   - If the issue revealed a gap in testing, create new TC-### to prevent regression.
   - Update PROJECT_PLAN.md if the issue impacts sprint deliverables or timeline.
   - Close the debug session only after all tests pass and verification is complete.

Framework Integration
- Prioritize existing testing frameworks in the project stack.
- Use Chrome DevTools MCP for all web-based debugging and performance analysis.
- Leverage container orchestration tools for environment-specific issues.
- Integrate with any existing monitoring or logging frameworks.

Acceptance Criteria for Debug Resolution
- Original issue no longer reproduces in containerized environment.
- All existing test cases continue to pass.
- New test case created to prevent regression (if applicable).
- Debug log updated with complete resolution documentation.
- No new issues introduced during the fix process.

Rules enforced
- Two-week sprints.
- Work is containerized via Docker Desktop with separate compose files per environment.
- Secrets in .env files (do not commit real secrets).
- Acceptance criteria (ACs) must be defined during sprint planning and traced to requirements.
- Testing is the main quality gate. No deliverable can be marked done until:
  * All tests covering its ACs pass
  * Validation script confirms all required fields from spec are present
  * API responses validated against acceptance criteria specification
- Test Validation Protocol (required):
  * Extract expected fields from sprint scope before testing
  * Create validation script (tests/validation/validate_del*.py) for each deliverable
  * Run validation script on all API responses
  * Document validation results with field-by-field checklist
  * See docs/testing/test-validation-protocol.md for full process
- Chrome DevTools MCP integration required for all web application testing and debugging.
- PROJECT_PLAN.md must be updated after each sprint.
- Consistency checks (REQ ⇄ DEL ⇄ AC ⇄ TC) are mandatory at both planning and completion gates.
- Environment Profiles (Docker Desktop):
  - Dev: interactive development profile with Chrome DevTools MCP access.
  - Test: executes the test suite and returns pass/fail status.
- Versioning:
  - Sprint tags use v0N.0 (e.g., v03.0)
  - Phase tags use phase-1.0, phase-2.0, …

Traceability model
- IDs: REQ-### (functional), NFR-### (non-functional), DEL-### (deliverable), AC-### (acceptance criterion), TC-### (test case)
- Mapping:
  - Each DEL maps to one or more REQ/NFR
  - Each AC maps to a DEL and one or more REQ/NFR
  - Each TC maps to one or more ACs
- Indexes/Registers:
  - Deliverables: docs/30-Planning/deliverables-register.md
  - ACs: docs/40-Testing/acceptance-criteria-index.md
  - Test Cases: docs/40-Testing/test-cases.md


Definition of Ready (DoR)
- DEL with linked REQ/NFR
- ACs authored and linked to each DEL
- Test cases authored and linked to each AC
- Validation script created (tests/validation/validate_del*.py) with all expected fields from spec
- Environment ready (Docker dev/test)
- Environment images build successfully in Docker Desktop (dev + test)
- Branch ready (Sprint Execution will create the sprint branch and record it in the sprint doc)

Macro: Do Sprint Execution
Objective: Implement sprint deliverables in a dedicated branch, keep sprint documentation current, and validate continuously through testing.

How to run: Tell Agent: Do Sprint Execution for Sprint N

Steps
0) Branch Setup
   - Create a new branch for the sprint and record its name in docs/30-Planning/sprints/sprint-0N.md.
1) Environment
   - Verify ops/docker/.env exists (or is copied from the example).
   - Ensure the development environment is started and running inside Docker Desktop using the Dev profile.
   - Record environment status in docs/30-Planning/sprints/sprint-0N.md (e.g., 'Dev environment running in Docker Desktop').
2) Implementation
   - Build the deliverables committed for this sprint.
   - Update the sprint doc with progress notes.
   - If a design delta arises, create a new ADR under docs/20-Solution/decisions/adr-*.md and note it in sprint-0N.md.
3) Testing During Execution (gating)
   - Before testing: Create validation checklist from sprint scope document (extract all expected fields from ACs and implementation details).
   - Create or use validation script from tests/validation/validate_del*.py to systematically verify all required fields.
   - Execute the Test profile in Docker Desktop and capture results.
   - Run validation script on API responses to ensure all fields from spec are present.
   - Record pass/fail + validation results in docs/40-Testing/test-cases.md.
   - Do not mark any deliverable 'Done' until:
     * All tests covering its ACs pass
     * Validation script confirms all required fields present
     * Response matches spec document field-by-field
4) Maintain Traceability
   - Ensure DEL ⇄ AC ⇄ TC links remain valid.
   - Update deliverables-register.md, acceptance-criteria-index.md, and test-cases.md as needed.
   - If any DEL ⇄ AC ⇄ TC link changes or breaks during execution, record the reason (e.g., requirement change, design delta) in docs/30-Planning/sprints/sprint-0N.md.

Macro: Do Sprint Completion
Objective: Validate sprint outcomes, finalize documentation, and integrate sprint branch back into the main line.

How to run: Tell Agent: Do Sprint Completion for Sprint N

Steps
1) Acceptance and testing
   - Verify every AC-### is met and all related TC-### pass; record results in test-cases.md.
   - Run validation scripts (tests/validation/validate_del*.py) for all deliverables to confirm:
     * All required fields from spec are present in API responses
     * Field types match expectations
     * Acceptance criteria compliance validated programmatically
   - Include validation output in test reports (show checklist of verified fields).
   - Use docs/50-Completion/sprint-completion-checklist.md to confirm all required checks.
   - Run the full test suite in Docker Desktop (Test profile) before merge.
   - Sprint cannot be marked complete if any validation script fails.
2) Documentation updates
- Update docs/30-Planning/sprints/sprint-0N.md with outcomes.
   - Update docs/30-Planning/deliverables-register.md statuses.
   - Capture any design deltas in docs/20-Solution and create ADRs under docs/20-Solution/decisions/adr-*.md if needed.
3) Project plan update (required)
   - Update PROJECT_PLAN.md (status, next sprint, decisions snapshot).
4) Merge & Tag (required)
   - Merge the sprint branch into main (resolve conflicts if any).
   - Tag the release as v0N.0.
   - Record the merge and tag in docs/30-Planning/sprints/sprint-0N.md.
   - Create docs/50-Completion/release-notes-sprint-0N.md for this increment.
   - Update docs/50-Completion/release-notes.md to index and link to this sprint's release notes.
5) Repository sync (required)
   - Ensure the repository is initialized if new; otherwise sync changes with the configured remote.
   - Always include tags when pushing (use sprint tag v0N.0).
   - Repository sync only after Docker Desktop Test results are green.

Macro: Do Phase Planning
Objective: Define the scope of the phase, ensure requirements are clean and prioritized, assign deliverables to sprints, and validate consistency before execution begins.

How to run: Tell Agent: Do Phase Planning

Steps
- Consistency Check (required)
  - Validate links across REQ ⇄ DEL ⇄ AC ⇄ TC.
  - Output a report to docs/60-Quality/consistency-report.md.
  - Block planning until violations are resolved.
- Backlog Hygiene (required)
  - Review and prioritize docs/10-Requirements/functional-requirements.md and non-functional-requirements.md.
  - Merge duplicates, remove obsolete items, and apply priority tags (e.g., MoSCoW or RICE).
  - Ensure docs/30-Planning/deliverables-register.md is seeded directly from these prioritized requirements (one DEL per REQ by default).
- Phase Scope Setup (required)
  - Update docs/30-Planning/phase-plan.md with objectives and sprint count.
  - Assign DEL-### to sprints in docs/30-Planning/deliverables-register.md.
  - Seed/update docs/40-Testing/acceptance-criteria-index.md with at least one AC per DEL.
- Project Plan Update (required)
  - Update PROJECT_PLAN.md with the phase schedule and deliverables summary.


Minimal process ethos
- Keep documents concise; prioritize links and IDs.
- Favor decision records (ADRs) over lengthy narratives.
- Testing is truth: green tests + met ACs = done.

Macro: Do Project Intake (Minimal — Assistant-led)
- How to run: Tell Agent: Do Project Intake
- What I will ask (max 3 prompts):
  1) Project name + one‑line vision
  2) Primary user/persona + main problem to solve
  3) Confirm tech baseline [Python 3.12 + FastAPI + Postgres + port 8080] (Y/n)
- What I will do automatically:
  - Draft/update these docs with concise content and sensible defaults:
    - docs/00-Initiation/discovery-questionnaire.md, scope-and-objectives.md, stakeholders-and-roles.md, constraints-and-assumptions.md, risks-log.md, glossary.md
    - docs/10-Requirements/PRD.md, functional-requirements.md (seed 3 REQs), non-functional-requirements.md (seed priorities)
    - docs/20-Solution/solution-architecture.md (Mermaid), solution-design.md, tech-stack-and-language.md, deployment-topology.md
  - Clearly mark TBD sections where deeper detail can be added later.

Macro: Do Initiation (Minimal)
- How to run: Tell Agent: Do Initiation
- Questions: (1) Project name + one‑liner vision, (2) Persona + main outcome
- Result: Updates docs/00-Initiation/discovery-questionnaire.md, scope-and-objectives.md, stakeholders-and-roles.md, constraints-and-assumptions.md, risks-log.md, glossary.md with concise drafts.

Macro: Do Requirements (Minimal)
- How to run: Tell Agent: Do Requirements
- Questions: (1) One‑sentence problem, (2) Auto‑seed 3 FRs and 3 NFRs (you can adjust later)
- Result: Updates docs/10-Requirements/*.md.

Macro: Do Solution (Minimal)
- How to run: Tell Agent: Do Solution
- Questions: (1) Confirm tech baseline (default above), (2) Optional: main components (press Enter for defaults)
- Result: Updates docs/20-Solution/*.md and adjusts ops/docker/.env.example PORT if changed.

Note: No external scripts are needed; the Agent will ask the brief questions and edit files directly when you invoke these macros.

Macro: Start New Project
Objective: Create a new project from this template into a destination directory with one simple command, fully containerized.

How to run: Tell Agent: Start New Project
- If you omit the destination, I will prompt for: Destination path (required), Initialize Git (Y/n), Overwrite if exists (y/N).
- Non-interactive form: Tell Agent: Start New Project in "C\\Path\\To\\Dest" [with Git] [overwrite]

What this does
- Runs PowerShell on the host system and executes scripts/new-project.ps1.
- Copies all template files into the destination, excluding: .git, .vs, .idea, .vscode, bin, obj, node_modules, dist, out, .terraform, .venv, venv.
- If ops/docker/.env.example exists, creates ops/docker/.env if missing.
- If you say "with Git", initializes a repo and makes an initial commit.
- If you say "overwrite", allows copying into a non-empty destination.

The command the Assistant will run
- Windows (Host PowerShell):
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\\scripts\\new-project.ps1" -Destination "C:\\Path\\To\\Dest" [-Git] [-Overwrite]

Acceptance criteria
- The copy runs on host PowerShell (reliable on Windows systems).
- Destination contains the template minus the excluded items listed above.
- ops/docker/.env is created from .env.example when present.
- When "with Git" is requested, .git exists and an initial commit is present.
- Re-running with "overwrite" succeeds and is idempotent.
- Works with Windows paths, including spaces.

Test cases (required before marking done)
- T1: New empty destination → Success; files present; excluded items absent; .env created.
- T2: Non-empty destination without overwrite → Error message and no changes.
- T3: Non-empty destination with overwrite → Success; idempotent.
- T4: Destination path contains spaces → Success.
- T5: OneDrive path (this repo lives under OneDrive) → Success; if file locks occur, pause OneDrive sync and retry.

Notes
- Uses host PowerShell for reliable execution on Windows systems.
- Long Windows paths: if you encounter path-length issues, enable long paths in Windows or keep destination path shorter.

Macro: Do Sprint Planning
Objective: Define the sprint's goal and deliverables, ensure acceptance criteria and test cases are ready, and prepare for execution.

How to run: Tell Agent: Do Sprint Planning for Sprint N

Steps
- Confirm sprint number and scope (required)
  - Default to the next planned sprint if not specified.
- Select deliverables for the sprint (required)
  - Choose from the prioritized requirements created in Phase Planning.
  - Update docs/30-Planning/deliverables-register.md to mark selected DEL-### as In Progress with Target Sprint = N.
- Sprint doc update (required)
  - Update docs/30-Planning/sprints/sprint-0N.md with sprint goal, deliverables, and tasks per deliverable:
    - Implement, Integrate, Author tests, Make tests pass, Update docs.
- Acceptance criteria (required)
  - Update docs/40-Testing/acceptance-criteria-index.md with AC-### linked to each DEL-### (seed 1–2 per DEL if missing).
- Test cases (required)
  - Update docs/40-Testing/test-cases.md with TC-### linked to each AC-### (seed at least one per AC with concise steps and expected results).
- Test plan and data (required)
  - Update docs/40-Testing/test-plan.md with sprint scope, entry/exit criteria, and links to ACs/TCs.
  - Update docs/40-Testing/test-data-strategy.md with data needed for sprint ACs.
- Project plan update (required)
  - Update PROJECT_PLAN.md with sprint schedule and deliverables summary.

Guarantees
- ACs are defined for every deliverable in the sprint.
- Test cases exist for every AC before execution begins.
- Testing remains the gate for marking deliverables 'Done'.
