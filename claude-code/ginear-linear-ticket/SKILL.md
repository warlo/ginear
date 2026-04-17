---
name: ginear-linear-ticket
description: Use before starting non-trivial code work or before committing, to attach to an existing Linear ticket or create one via the `gin` CLI (ginear). Creates a branch that matches the Linear identifier so the ticket and git history stay linked. Skip for trivial edits, doc-only tweaks, or when the user already named a ticket/branch.
---

# ginear-linear-ticket

Use the `gin` CLI to keep code work linked to Linear tickets. `gin` is `ginear` (https://github.com/warlo/ginear) — a thin wrapper over the Linear API with non-interactive flags and `--json` output suitable for scripting.

## When to run

Run **before** starting implementation (so the branch is created correctly) or **before** the first commit of a new line of work.

**Do it when:**
- The user starts a new feature, bug fix, or refactor of more than a few lines.
- You're about to create a branch or commit but the current branch is `main` / detached / unrelated to the work.
- The user explicitly asks to "make a ticket" or "find the ticket".

**Skip when:**
- Trivial edits (typo, one-line tweak, formatting).
- Doc-only changes unless the user wants tracking.
- The user is already on a branch whose name matches a Linear identifier (e.g. `hww/ins-440-...`) — that means a ticket is already attached.
- The user explicitly said no tracking.

If unsure whether to run, **ask once** with a short yes/no prompt — don't create tickets speculatively.

## Pre-flight

Before calling `gin`, check that it's installed and configured:

```bash
command -v gin >/dev/null && echo "gin: installed" || echo "gin: missing"
test -f "$HOME/.ginear" && echo "config: ok" || echo "config: missing"
```

### If `gin` is missing

Ginear is a tiny Python CLI (https://github.com/warlo/ginear). Offer to install it:

> "ginear (`gin`) isn't installed. It's a small Python CLI that wraps the Linear API. Install it with `pipx install ginear`? (y/n)"

On yes, run:

```bash
command -v pipx >/dev/null || { echo "pipx not installed — run: brew install pipx && pipx ensurepath"; exit 1; }
pipx install ginear
```

Then continue to the config step. If `pipx` is also missing, stop and tell the user to install it (`brew install pipx && pipx ensurepath`); don't install Homebrew packages without consent.

### If config is missing

`gin init` is interactive (opens a browser for the API token and prompts for team/project). Tell the user:

> "ginear needs a one-time setup. Run `gin init` in your terminal, then retry."

Do **not** run `gin init` in the background — it will block.

Once both checks pass, proceed to the workflow.

## The workflow

### 1. Look for an existing ticket first

Derive 2–4 keywords from what the user is trying to do, then search:

```bash
gin search "keywords here" --limit 10 --json
```

Output is a JSON array of `{id, identifier, title, branchName, url, creator, state}`. Choose at most one clear match — same topic, same area of the codebase, still open (i.e., `state.name` is not "Done"/"Cancelled"/"Closed"). If nothing is a clear match, skip to step 3 (create).

Do **not** guess. If several tickets look plausible, list the top 3 to the user (identifier + title) and ask which to use, or offer to create a new one.

### 2. Attach to the existing ticket

```bash
gin attach <IDENTIFIER> --json
```

This switches git to the ticket's branch (creating it if needed) and prints the issue JSON. Use `--no-switch` if the user wants to stay on the current branch.

Report briefly: "Attached to `ENG-123` – *title*".

### 3. Otherwise, create a new ticket

```bash
gin create \
  --title "Short imperative title" \
  --description "One–two sentences on what and why. Include links/context if helpful." \
  --json
```

Without `--no-switch`, `gin` switches to the new ticket's branch.

**Title rules:** imperative mood, ≤72 chars, no ticket-number prefix (Linear assigns it).
**Description rules:** plain text or markdown. Don't paste secrets. Keep it short — it's a ticket, not a PRD.

If the user is ambivalent about whether they want a ticket, ask before creating. Tickets are cheap but not free.

### 4. Committing

For the first commit of the new line of work, `gin commit` combines ticket + commit:

```bash
gin commit -m "feat(scope): do the thing" --title "Do the thing" --description "Why"
```

If a ticket is already attached (steps 1–2 or pre-existing branch), use plain `git commit` — don't create another ticket.

## Output handling

Always pass `--json` when you need structured data. Parse the JSON with `jq` or inline — don't grep the human text.

Example: get the identifier of the matched/created ticket for PR descriptions:

```bash
IDENTIFIER=$(gin search "refactor auth" --limit 1 --json | jq -r '.[0].identifier')
```

## Reference: full command surface

| Command | Purpose | Notable flags |
|---|---|---|
| `gin search [query]` | List matching issues | `--limit N`, `--json` |
| `gin attach <id>` | Switch to issue's branch | `--no-switch`, `--json` |
| `gin create` | Create issue (+ switch) | `--title`, `--description`, `--no-switch`, `--json` |
| `gin commit -m <msg>` | Create issue + switch + git commit | `--title`, `--description`, `--json` |
| `gin init` | Re-run onboarding | – |
| `gin team` / `project` / `state` | Configure defaults | – |

## Failure modes

- **"Missing team_id. Run `gin init`."** — Tell the user; don't run `gin init` automatically (it's interactive and opens a browser).
- **Invalid API token** — `gin` clears the token and exits. Tell the user to run `gin init`.
- **Branch already exists** — `gin attach` / `create_issue` switch to it via `git switch`; that's expected.
- **Issue creation fails** — `gin create --json` exits with code 1. Report the error and fall back to the user.
