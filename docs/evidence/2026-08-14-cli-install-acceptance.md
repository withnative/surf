# Claude Code CLI install acceptance evidence — 2026-08-14

> Historical route: this run used the former Surf-owned `withnative` marketplace. Surf no
> longer publishes that marketplace; current clean installs register the canonical
> `withnative/plugins` catalogue. The client and package-behaviour observations below
> remain useful, but they do not verify the new catalogue route.

This records an observed `claude plugin` install, uninstall and update cycle against the
former public `withnative/surf` marketplace on macOS. It is indicative operational evidence, not
a clean-profile certification and not a mechanical release gate.

**This was not a clean profile.** The `withnative` marketplace was already configured and
`surf@withnative` was already installed at user scope before the run began. The run was
executed by an AI agent in a terminal on the maintainer's own macOS machine, at his
direction. No participant practice content was involved, read or recorded.

## Observed commands and output

Uninstall, with the bare plugin name:

```text
$ claude plugin uninstall surf
✔ Successfully uninstalled plugin: surf (scope: user)
```

Exit status 0. The bare name is accepted by `uninstall`.

Install:

```text
$ claude plugin install surf@withnative
✔ Successfully installed plugin: surf@withnative (scope: user)
```

Exit status 0. The install was fully non-interactive: no confirmation prompt appeared and
`-y` was not needed.

Marketplace refresh:

```text
$ claude plugin marketplace update withnative
✔ Successfully updated marketplace: withnative
```

Update, with the bare plugin name:

```text
$ claude plugin update surf
✘ Failed to update plugin "surf": Plugin "surf" not found
```

Update, with the `plugin@marketplace` form:

```text
$ claude plugin update surf@withnative
✔ Plugin "surf" updated from 0.1.0 to 0.1.1 for scope user. Restart to apply changes.
```

Throughout, `claude plugin list` reported `surf@withnative`, `Scope: user`,
`Status: ✔ enabled`.

## Findings

**`update` and `uninstall` disagree about the bare name.** `claude plugin uninstall surf`
succeeded, but `claude plugin update surf` failed with `Plugin "surf" not found` while
`claude plugin list` showed the plugin installed at user scope. The `plugin@marketplace`
form works for both. This asymmetry is the most likely thing to trip a reader, so the
canonical guide now uses the qualified form for `update` and says why.

**The install resolves from a stale local marketplace snapshot.** The install produced
plugin package version `0.1.0` even though `origin/main` had already published `0.1.1`.
The locally cached snapshot predated that publish. Refreshing the marketplace before
installing avoids serving an older package than the one published.

**`marketplace update` refreshes the catalogue only.** After
`claude plugin marketplace update withnative` reported success, `claude plugin list` still
showed the installed plugin at `0.1.0`. Moving the installed plugin required a separate
`claude plugin update surf@withnative` (or an uninstall and reinstall).

**Updates ask for a restart in so many words.** The successful update printed
`Restart to apply changes.` The install printed no equivalent notice, so nothing is
claimed here about whether a fresh install reaches an already-running session.

**A user-scope install is live in the Claude Code desktop application.** The desktop
session in which this work was done had the user-scope `surf@withnative` plugin active,
with its skill and MCP server loaded.

**Codex, reported by the maintainer rather than executed in this run.** The maintainer
confirms he has run the `codex` CLI install himself and that it works, and that the plugin
does appear in the ChatGPT/Codex desktop application afterwards, in a less prominent area
of the interface than an in-app install. That is his own report from earlier use; no
`codex` command was run or captured during this session.

## What this does not establish

- **Clean-profile install.** The marketplace and plugin were already present. A clean
  profile taking `marketplace add` and `install` from nothing was not exercised.
- **Desktop restart after a CLI reinstall.** A user-scope install was observed active in
  the desktop application, but a desktop restart taken specifically after this reinstall
  was not separately observed.
- **The `codex plugin` CLI install verb**, which the maintainer reports using successfully
  but which has not been captured in a recorded test with exact output.
- Activation, framework retrieval, practice setup and resumption behaviour, which are
  covered by their own gates and evidence records.

The corresponding release gates remain open. See the
[plugin release acceptance runbook](../plugin-release-acceptance.md).
