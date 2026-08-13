> **Pull requests are closed unless invited.** Unsolicited pull requests will be
> closed. Open an issue first and read
> [CONTRIBUTING.md](https://github.com/withnative/surf/blob/main/CONTRIBUTING.md).

## Invitation

- [ ] A maintainer invited this pull request in a linked issue or discussion.
- [ ] The required Apache ICLA status check passes.

<!-- Link the invitation and agreed scope. -->

## What changed

<!-- Explain the problem and the smallest coherent solution. -->

## Verification

- [ ] `cargo fmt --check`
- [ ] `cargo check --locked`
- [ ] `cargo test --locked`
- [ ] `cargo deny check licenses`
- [ ] I added or updated tests in proportion to the behaviour changed.
- [ ] I updated canonical documentation for any changed public behaviour or assurance.

## Public-source and privacy checks

- [ ] This change contains no credentials, personal data, private operational configuration, internal transcripts or machine-specific paths.
- [ ] I identified generated or third-party material and confirmed its provenance and licence.
- [ ] If build inputs or deployment behaviour changed, I updated the corresponding-source checklist and exact-source disclosure.
- [ ] If dependencies changed, I reviewed new licence expressions and refreshed `docs/dependency-licenses.md`.

> **FIRST-OUTSIDE-MERGE BLOCKER:** until Surf's legal entity is confirmed and the
> unmodified Apache ICLA, private signature store, CLA Assistant check and branch
> protection are live, outside pull requests must not merge. This does not block
> publishing the repository.
