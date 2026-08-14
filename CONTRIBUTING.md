# Contributing to Surf

**Issues, questions, design discussion and forks are welcome. Pull requests are
closed unless a maintainer invites one.**

Surf is maintained alongside other work. Reviewing outside code well takes more
time than writing it, and a queue of unreviewed pull requests serves nobody. An
unsolicited pull request will therefore be closed, even when the idea is useful.

## What is useful

- **Open an issue.** Bug reports, unclear documentation, unsupported client
  behaviour and framework guidance that gives bad advice are all valuable.
- **Describe the fix rather than writing it.** Explain the observed problem and
  desired behaviour before investing in a patch.
- **Discuss a substantial proposal first.** A maintainer may invite a pull
  request after the scope and approach are agreed.
- **Fork Surf.** Surf is AGPL-3.0-only. Running, changing and publishing a
  fork under the licence is a first-class option, not a consolation prize. The
  official hosted service remains the supported product.

Report security vulnerabilities through [the private reporting
process](SECURITY.md), not a public issue or discussion.

## Code and other material submitted in issues or discussions

Please describe a proposed fix instead of pasting a patch. If you intentionally
submit code, documentation or other copyrightable material anywhere in this
repository—including an issue or discussion—you offer that material under the
same inbound copyright and patent licence terms that Surf uses for invited pull
requests: the Apache Individual Contributor License Agreement v2.0 (ICLA). You
keep ownership of your material; this is a licence offer, not an assignment.

The project cannot accept that offer or merge outside material until the legal
entity is confirmed and Surf's unmodified Apache ICLA form and signing flow are
live. Until then, maintainers will use descriptions only and independently write
any implementation.

## Invited pull requests

If a maintainer invites a pull request, the contributor must sign Surf's
unmodified Apache ICLA v2.0 before the contribution can merge. The ICLA grants
an inbound licence rather than transferring ownership. If an employer owns the
code—for example, because it was written on company time or equipment—say so in
the issue first; an individual signature may not be enough.

The contributor-agreement mechanism does **not** block publication of the
repository. It blocks the first outside merge. Before that can happen, the
project must:

- confirm the contracting legal entity and substitute its name and contact
  details into the otherwise unmodified Apache ICLA;
- publish that `CLA.md` and its signing instructions;
- create the private signature store;
- enable the CLA Assistant check; and
- require that check on the protected `main` branch.

No local `CLA.md` is published while the contracting entity is unresolved,
because a signable agreement with a placeholder—or an unchanged agreement that
grants rights to the Apache Software Foundation instead of Surf's operator—would
mislead contributors. No bespoke agreement or launch-time legal review is
required by the current decision.

## Preparing an invited change

Surf requires the Rust toolchain declared by the repository's CI configuration.

```console
cargo fmt --check
cargo check --locked
cargo test --locked
cargo deny check licenses
```

Install `cargo-deny` from its published crate when it is not already available:

```console
cargo install cargo-deny --locked
```

Keep `Cargo.lock` committed. If a dependency changes, include the lockfile and
confirm that `cargo deny check licenses` passes. Explain any new licence or
exception in the pull request; do not weaken `deny.toml` just to make CI green.

An invited pull request should:

- solve the agreed coherent problem;
- include tests in proportion to the behaviour changed;
- update canonical documentation when behaviour or a public assurance changes;
- disclose generated or third-party material and its provenance;
- avoid unrelated formatting or dependency churn; and
- complete the repository's pull-request checklist.

Keep framework guidance separate from documentation about Surf itself. Do not
add accounts, authentication, participant state, analytics or outbound data
flows without an explicit design decision and updated privacy documentation. Do
not include credentials, private operational configuration, internal
transcripts or machine-specific paths.

Until real production use creates a compatibility obligation, framework work
converges on the single, freely revisable working version `0.1.0`. Do not add a
historical framework catalogue, installed/available release state, migration
machinery or compatibility promises for development drafts. Git history is the
development archive. Keep authored moment guides and references distinct from
MCP resources, which are only a protocol delivery surface.

## Maintainer contribution hygiene

- Do not copy code out of issues or discussions. Understand the described
  problem and write the implementation independently.
- If a non-trivial suggested patch is genuinely the only sensible
  implementation, invite a pull request so the contributor signs the ICLA.
- Invited pull requests always pass the required CLA check; familiarity or a
  small change is not an exception.
- Do not soften this policy one pull request at a time. Change it deliberately
  and document the governance decision if Surf begins actively seeking outside
  contributions.

This is repository policy, not legal advice.
