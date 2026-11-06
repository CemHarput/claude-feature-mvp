# Claude Code Feature Workflow MVP

For small changes, the main session works directly; for larger features, a
separate architect, implementer and an optional reviewer are used. The slash
command files live in `.claude/commands/`. In the saved-feature flow the main
Claude session is the coordinator; independent module research runs in
parallel, dependent stages run sequentially.

## Requirements and setup

- A current Claude Code, with Opus/Sonnet models available on your account.
- Python 3.9+ (`python3`) and Git. On Windows, WSL is recommended.
- An existing Git repository for your application; the package does not
  include an application skeleton.

Unzip the archive. Run the installer from the extracted `claude-feature-mvp`
directory:

```bash
python3 /full/path/claude-feature-mvp/install.py /full/path/your-project
```

The installer appends the instructions to an existing CLAUDE.md and keeps an
existing settings.json. If an agent/command file with the same name but
different content exists, it fails without writing. The same protection applies
to changed files in a project that has an earlier version installed; compare
the new instructions with the existing files and merge them by hand.
Existing project settings / user settings / managed settings remain in effect;
the installer does not reset permissions. The new settings.json in the package
uses the normal `default` mode. Normal Claude Code tool permissions may be
requested while commands run.

Review the installation changes and commit them with your own Git workflow.
Before the first implementation, the application/config working tree must be
clean; reports under `docs/features/` are excluded from this check. The check
exists so that pre-existing source changes do not get mixed into the feature.

Restart Claude Code in the project root; verify the six agents in `/agents`
and the six commands in the slash menu. The same flow can be used with
`claude` in the VS Code integrated terminal. If the CLI is installed, check
`claude --version`. If you lack model access, you can set the `model` field
in the agent files to `inherit`. If your project has special build/test
recipes, write them in `.claude/project-context.md`.

## Usage

For a small bug, a text/style change, or a clear addition that fits the
existing architecture:

```text
/feature-fast Fix the wrong heading on the profile page.
```

The main session changes the code, runs the relevant checks and gives a short
result. It does not create a plan, feature state or a separate agent call. For
auth/authorization, payments, data loss, migration risk, or cross-module work
with unclear design, use the saved flow below. The number of files alone is
not a measure of risk.

```text
/feature-plan user-export I want to export the user list as CSV. Only admins should be able to use it.
```

When needed, independent modules are examined in parallel by read-only
researcher agents. The planner verifies the existing code and the findings and
produces a plan with four core sections; it does not change application code.
The main session saves `docs/features/user-export/plan.md` and stops. Read the
plan; you can ask for revisions during planning. If you revised a ready plan
before implementing it, the implement command approves the current hash.

```text
/feature-implement user-export
```

This command is your approval of the saved, current plan. The coordinator
passes the plan's entry points, relevant symbols, decisions and test commands
to the implementer. The implementer verifies them in the code, changes the
code/tests and runs the necessary checks. It makes local naming and helper
function decisions within the existing architecture itself; it stops on
decisions that change behavior, the API, dependencies or the data model.
The reviewer does not start automatically.

```text
/feature-review user-export
/feature-status user-export
```

Review only produces a report. If there are findings, no automatic fix is
made; follow the report and request fixes separately. Concrete findings under
`CHANGES_REQUESTED` that stay within the approved plan's scope can be fixed in
this order:

```text
/feature-fast --feature user-export Fix findings F1 and F2
/feature-review user-export
```

This usage invalidates the old review and appends the fix and the check
evidence to `implementation.md`. If the new review says `PASS`, you can close
the feature; the helper has no separate `closed` state. If the architecture or
scope changes, plan with a new slug. A verdict is valid as of the report time;
it does not cover later changes.

For a half-finished in_progress/blocked feature, the same implement command
resumes it. Finish the active/blocked work before moving to another feature; a
feature that is to be abandoned entirely must have its source changes and
state archived manually, after review. The MVP has no automatic
rollback/abandon command. Do not use concurrent Claude sessions for one
feature in the same working directory. Use separate Git worktrees for
independent work.

## File structure

```text
claude-feature-mvp/
  README.md
  CLAUDE.md
  install.py
  .claude/
    settings.json
    project-context.md
    agents/
      architecture-planner.md
      feature-researcher.md
      feature-implementer.md
      feature-reviewer.md
      project-reviewer.md
      refactor-implementer.md
    commands/
      feature-fast.md
      feature-plan.md
      feature-implement.md
      feature-review.md
      feature-status.md
    workflows/feature.md
    scripts/feature_state.py
  tests/test_mvp.py
  tests/test_project_review.py
```

When run, request.md, plan.md, state.json, implementation.md and an optional
review.md are created in the project under `docs/features/<slug>/`. These
reports carry task context across sessions; do not write secrets in them.

## Model and permission choices

| Role | Model alias | Tools | Output |
| --- | --- | --- | --- |
| Architect | opus | Read, Grep, Glob | Plan based on code evidence |
| Researcher | inherit | Read, Grep, Glob | Independent module findings |
| Implementer | sonnet | Read, Grep, Glob, Edit, Write, Bash | Code + tests + handoff |
| Reviewer | opus | Read, Grep, Glob | Independent review report |
| Refactor implementer | sonnet | Read, Grep, Glob, Edit, Write, Bash | Code + tests + handoff for selected review findings |

This selection is a starting policy; aliases are resolved according to
provider/account access. To reduce cost, you can set the reviewer to sonnet or
all roles to inherit. The planner/researcher/reviewer have no shell or write
tools. The coordinator saves the reports. The tool allowlist and the normal
permission mode are different mechanisms.

Before changing models, record planning, implementation, testing and reporting
times separately across several similar tasks. Count re-reading and fix rounds
too; do not switch models based only on the duration of a single agent call.
First see the effect of the short flow on total time, then compare model
options on the same task types.

## Verification

In the package directory:

```bash
python3 -m unittest discover -s tests -v
```

The tests check setup, state transitions, the dirty-source block, hash
changes, the concurrent-feature block and resume in real temporary Git
repositories. Live Claude Code test: make a small change with `/feature-fast`
and verify that no separate agent/feature report is created and that the
relevant check runs. Then plan a larger feature; check that the source files
are unchanged; on the implement call, verify the Sonnet agent and the test
results; verify that the reviewer does not run until you call review; then
call review and check that only a report is produced. Run status in a new
session.

Live Claude Code agent calls are outside the scope of the automated tests.
The package's static form and Python/Git behavior are tested; your own
project's build/test results arise in real feature work after installation.

## MVP limits

It uses prompt-based coordination and a Python state guard. The helper checks
the hash of the approved plan; there is no hook that catches arbitrary code
edits. Therefore this is not a security boundary that locks all writes of the
main Claude session. Test successes are not interpreted by the helper; the
coordinator chooses implemented/blocked based on the evidence in the report.
Report files can be edited by hand. Review covers the whole implementation
diff and untracked files relative to the current HEAD; commits/branch changes
must not be made during implementation. If you want a review afterwards, a
manual review against an explicit baseline is needed. Ignored source files do
not enter the Git diff; explicitly add such files to the scope in your project.

## Official sources

Documents checked on 11 October 2026:
- https://code.claude.com/docs/en/slash-commands
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/settings

Commands and skills produce the same slash interface; the existing
`.claude/commands/` format is supported. If supporting files are needed later,
you can move to the skills format; this is not necessary for this MVP.

## New: project architecture and code quality review

```text
/project-review
/project-review src/backend
/project-review src/auth/login.ts
```

The parameter is a real repo-relative file/directory path. The architecture is
extracted first, then the code files are reviewed in order. Findings on clean
code, separation of responsibilities, coupling, duplication, error handling
and architectural antipatterns are reported with evidence and in order of
severity. Only a report is written; no fixes are made in application code.

New files: .claude/commands/project-review.md, agents/project-reviewer.md,
workflows/project-review.md, project-review.json,
scripts/project_review_snapshot.py and templates/project-review-report.md
(all under .claude). The project reviewer uses Opus; it only has the
Read/Grep/Glob tools.

After the review, you can use the `refactor-implementer` agent by naming the
finding IDs you want fixed or an explicitly bounded repair scope. The agent
re-verifies the finding in the current code, preserves user changes, applies
only the approved scope and runs the relevant tests. It returns `NEEDS_INPUT`
for unclear product decisions and `NEEDS_PLAN` for broad architectural changes
without a plan; it does not apply review findings automatically or in bulk.

Reports are stored under `docs/reviews/<UTC-timestamp>/` as architecture.md,
code-quality.md, report.md, the file inventory and batch reports. If the first
and last fingerprints differ, it reports STALE; if the review is missing parts,
it reports INCOMPLETE. Large projects are split into batches in sequence;
unread files are explicitly shown in the coverage table.

This is not a SonarQube integration. If local lint/static analyzers exist,
they are used in check mode, without installing or fixing anything, by reading
their commands. If none exist, this is stated explicitly. Complexity /
coverage / duplication percentages, debt time and quality gates are not
produced without measurement. Rules are justified against the real project
structure; personal style preferences are not counted as bugs. Findings are
reported with severity and confidence.

Git-ignored files are out of scope. node_modules/vendor/build are excluded by
default; if your hand-written sources live there, update the config.
Non-UTF-8, binary, very large and symlink files are recorded separately.
Review reports may trip the clean-source check at the start of a feature:
before starting a new feature, commit the reports with your own Git workflow or
safely move them out of the working tree.

If an earlier MVP is installed, install.py from the new ZIP stops on changed
files; compare the new instructions with the existing project files and merge
them. Existing settings and feature files are preserved. Restart Claude Code so
that the project reviewer agent appears.

Live trial: run /project-review; check that the architecture report is produced
before the code phase, that coverage matches the inventory, that findings point
to real lines, and that product files are unchanged.

Package verification: 13 Python/Git tests passed. Adding the new module to a
project installed from the previous ZIP was also checked. A live Claude Code
agent trial is outside the scope of the automated tests.
