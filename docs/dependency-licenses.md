# Dependency licence audit

## Result

The locked dependency graph was reviewed on **13 August 2026**. All direct,
development, build, transitive and target-specific Rust dependencies declare
licence expressions covered by the allow-list in [`deny.toml`](../deny.toml).
No dependency in `Cargo.lock` declares a strong-copyleft, proprietary or unknown
licence.

At the reviewed commit, Cargo resolved 60 packages across all targets: Surf
itself and 59 third-party packages. The direct third-party declarations were:

| Scope | Package | Locked version | Declared licence |
|---|---|---:|---|
| Runtime | `axum` | 0.8.9 | MIT |
| Runtime | `serde` | 1.0.229 | MIT OR Apache-2.0 |
| Runtime | `serde_json` | 1.0.151 | MIT OR Apache-2.0 |
| Runtime | `tokio` | 1.53.1 | MIT |
| Development | `http-body-util` | 0.1.4 | MIT |
| Development | `sha2` | 0.10.9 | MIT OR Apache-2.0 |
| Development | `tower` | 0.5.3 | MIT |

The committed `Cargo.lock` and automated output are the source of truth if this
snapshot changes; versions in this table must be refreshed with dependency
updates.

The graph consists of permissive terms drawn from:

- Apache-2.0, including the LLVM exception where declared;
- MIT;
- BSD-3-Clause;
- Unicode-3.0; and
- Unlicense.

Some crates offer a choice among licences; `matchit` declares both MIT and
BSD-3-Clause. These expressions are evaluated by `cargo-deny`, rather than
flattened into a hand-maintained list.

Surf itself declares `AGPL-3.0-or-later`. Passing this audit means the declared
expressions satisfy the repository's configured policy; it is not a legal
opinion about every possible use, combination or distribution.

## Reproduce the audit

From the repository root, using the committed lockfile:

```console
cargo metadata --locked --format-version 1 > /tmp/surf-cargo-metadata.json
cargo deny check licenses
```

To inspect every package expression independently of the policy tool:

```console
cargo metadata --locked --format-version 1 \
  | jq -r '.packages[] | [.name, .version, (.license // "MISSING")] | @tsv' \
  | sort
```

`cargo deny check licenses` is the authoritative automated result. `cargo-deny`
uses the committed lockfile to evaluate the complete resolved graph, including
platform-specific packages, and fails on an unapproved, unlicensed or
unrecognised expression. CI repeats the check for every pull request and push to
`main`.

## Review procedure for dependency changes

1. Inspect the package source, licence files and upstream metadata for every new
   or changed crate.
2. Run the two commands above with `--locked` semantics preserved.
3. Treat a new licence, exception or unclear expression as a review item; do not
   broaden `deny.toml` without recording why it is compatible with distribution.
4. Refresh this audit's date and findings in the same pull request.
5. Seek qualified legal advice for ambiguity. Tool output is evidence, not legal
   advice.
