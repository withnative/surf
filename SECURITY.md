# Security policy

## Reporting a vulnerability

Please do not disclose a suspected vulnerability in a public issue, discussion,
pull request or social-media post. Include:

- a description of the issue and its likely impact;
- the affected release, framework version or commit;
- clear reproduction steps or a proof of concept;
- any mitigations you have already identified; and
- how we may contact you about the report.

Do not include personal data, credentials or unrelated confidential information.
Please allow the maintainers a reasonable opportunity to investigate and
coordinate a fix before public disclosure.

Surf's canonical reporting route is GitHub private vulnerability reporting:

- [Privately report a security vulnerability](https://github.com/withnative/surf/security/advisories/new)

This link is staged in the private publication candidate. It is not a live
reporting route until `withnative/surf` is public and GitHub's private
vulnerability reporting control has been enabled and independently verified.
Ordinary public issues remain disabled throughout that cutover. This plan
explicitly accepts the bounded interval between the separately confirmed
visibility change and successful verification of the private form.

If the link does not show a private reporting form, do not disclose details in
a public issue, discussion, pull request or other public channel. Surf does not
currently offer an alternative private intake.

## Publication cutover for maintainers

Immediately after the approved private-to-public visibility change, and before
opening public issues or promoting a release:

1. Confirm that `withnative/surf` is public at the expected root commit and has
   no unexpected branches, tags, releases or other refs.
2. In **Settings > Security > Advanced Security**, enable **Private
   vulnerability reporting**.
3. From a signed-out or non-maintainer position, open the private reporting URL
   above and verify that GitHub presents a private vulnerability-report form.
   Do not submit real sensitive material as part of the test.
4. Re-verify push rulesets and every safeguard that may have changed or been
   disabled when repository visibility changed.
5. Record the timestamp, repository state, tester position and result in the
   private publication evidence. Only a passing result permits the later task
   to enable public issues or promote a release.

If enablement, reachability or safeguard verification fails, keep public issues
disabled and stop release finalisation. Treat the repository as already
exposed, preserve the evidence and either repair and re-verify the control or
obtain explicit approval for a real, tested alternative intake. Changing the
repository back to private does not undo public exposure or restore
confidentiality.

## Scope

Security reports may cover the hosted MCP service, the server implementation,
the published framework, build and release integrity, or a mismatch between the
documented privacy boundary and actual behaviour.

The version currently receiving fixes and the response timetable will be stated
here once release policy is final. Reports about community-operated forks should
normally go to that fork's operator.

This policy does not promise rewards or safe-harbour terms that have not been
formally adopted.
