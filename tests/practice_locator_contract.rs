// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-or-later

use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};

const QUICKSTART: &str = include_str!("../framework/0.1.0/quickstart.md");
const SETUP: &str = include_str!("../framework/0.1.0/setting-up.md");
const CONTEXT: &str = include_str!("../framework/0.1.0/context-and-local-practice.md");
const SKILL: &str = include_str!("../plugins/surf/skills/next-step/SKILL.md");
const PRIVACY: &str = include_str!("../docs/privacy-and-data.md");
const RELEASE_ACCEPTANCE: &str = include_str!("../docs/plugin-release-acceptance.md");
const ACCEPTANCE: &str = include_str!("../docs/evidence/2026-08-13-practice-locator-acceptance.md");

fn compact(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

fn locator_example() -> &'static str {
    CONTEXT
        .split_once("```json")
        .expect("locator JSON fence is missing")
        .1
        .split_once("```")
        .expect("locator JSON fence is unterminated")
        .0
        .trim()
}

fn plugin_files(root: &Path) -> Vec<PathBuf> {
    fn visit(root: &Path, current: &Path, files: &mut Vec<PathBuf>) {
        for entry in fs::read_dir(current).expect("plugin directory must be readable") {
            let path = entry.expect("plugin entry must be readable").path();
            if path.is_dir() {
                visit(root, &path, files);
            } else {
                files.push(path.strip_prefix(root).unwrap().to_path_buf());
            }
        }
    }

    let mut files = Vec::new();
    visit(root, root, &mut files);
    files.sort();
    files
}

#[test]
fn locator_paths_and_schema_are_exact_and_platform_specific() {
    let text = compact(CONTEXT);
    assert!(text.contains("`$HOME/.surf/locator.json` on macOS/Linux"));
    assert!(text.contains(r"`%USERPROFILE%\.surf\locator.json` on Windows"));

    let value: Value = serde_json::from_str(locator_example()).expect("example must be JSON");
    let object = value.as_object().expect("locator must be a JSON object");
    assert_eq!(
        object.len(),
        2,
        "locator example must have exactly two keys"
    );
    assert_eq!(object.get("schema_version"), Some(&Value::from(1)));
    assert_eq!(
        object.get("surf_home"),
        Some(&Value::from("/absolute/path/to/the/confirmed/practice"))
    );
    assert!(text.contains("each exactly once"));
    assert!(text.contains("JSON whitespace and object-member order are immaterial"));
    assert!(text.contains("fully expanded, platform-absolute string"));
    assert!(text.contains("versions only the locator structure and interpretation"));
    for forbidden in [
        "Do not accept `~`",
        "environment-variable references",
        "globs or a list of candidates",
        "learning content, participant identifiers, server-side identifiers or credentials",
    ] {
        assert!(text.contains(forbidden), "schema rule missing: {forbidden}");
    }
}

#[test]
fn discovery_order_gives_a_valid_launch_practice_strict_precedence() {
    let text = compact(CONTEXT);
    let launch = text
        .find("A valid launch-directory practice wins; do not read the user-level locator")
        .expect("launch precedence is missing");
    let canonical = text
        .find("Otherwise, read only the canonical locator path for the platform")
        .expect("canonical locator read is missing");
    let target = text
        .find("Validate the locator before following it")
        .expect("target validation is missing");
    assert!(launch < canonical && canonical < target);
    for validator in [
        "`AGENTS.md` marker",
        "`README.md` semantic map",
        "working-framework record",
    ] {
        assert!(
            text.contains(validator),
            "target validator missing: {validator}"
        );
    }
    assert!(text.contains("This order applies whether Surf was activated naturally or explicitly"));
}

#[test]
fn invalid_locator_states_and_wrong_filesystem_shapes_fail_closed() {
    let text = compact(CONTEXT);
    assert!(
        text.contains("Only an absent locator permits the existing bounded-discovery conversation")
    );
    assert!(text.contains("do not reinterpret denial as absence or widen the search"));
    for row in [
        "Locator malformed | Stay read-only, describe the problem and ask for direction; no search.",
        "Locator stale | Stay read-only, describe the missing or invalid target and ask for direction; no search.",
        "Locator duplicated | Stay read-only, describe the duplicate keys and ask for direction; no search.",
        "Locator unsupported | Stay read-only, describe the unknown schema version and ask for direction; no search.",
        "Locator inaccessible | Stay read-only, describe the denied locator or target and ask for direction; no search.",
    ] {
        assert!(text.contains(row), "failure outcome missing: {row}");
    }
    for malformed in [
        "malformed JSON or UTF-8",
        "a byte-order mark",
        "duplicate keys",
        "a missing or additional key",
        "a non-integer or unsupported `schema_version`",
        "a non-string or non-absolute `surf_home`",
    ] {
        assert!(
            text.contains(malformed),
            "malformed case missing: {malformed}"
        );
    }
    for shape in [
        "must be a real directory and must not be a symlink",
        "must be a regular file and must not itself be a symlink",
        "Inspect these entries without following symlinks",
        "Do not treat it as absent, follow it, search elsewhere or replace it",
        "Locator has the wrong filesystem shape | Stay read-only",
        "no search or write",
    ] {
        assert!(
            text.contains(shape),
            "filesystem-shape rule missing: {shape}"
        );
    }
    assert!(!text.contains("irregular or unsafe locator file"));
}

#[test]
fn setup_move_and_delete_have_explicit_safe_write_semantics() {
    let setup = compact(SETUP);
    let context = compact(CONTEXT);
    for required in [
        "one explicit proposal that names both the exact practice home and the canonical locator file",
        "confirmation of that proposal authorises both writes",
        "do not add a second consent prompt",
        "safely create or replace the locator only after the practice validates",
        "cross-directory continuity was not established",
    ] {
        assert!(setup.contains(required), "setup rule missing: {required}");
    }
    for required in [
        "repeated setup is idempotent",
        "Never silently overwrite an invalid locator",
        "create a new regular sibling temporary file",
        "without following or reusing an existing entry",
        "atomically replace `locator.json`",
        "read the canonical locator back",
        "A later move requires a new confirmation",
        "deleting only the locator restores the no-global-discovery state",
        "leaves the practice untouched",
    ] {
        assert!(context.contains(required), "write rule missing: {required}");
    }
}

#[test]
fn contract_prohibits_broad_search_and_surf_mcp_content_transfer() {
    let guidance = compact(&format!("{QUICKSTART}\n{SETUP}\n{CONTEXT}"));
    assert!(guidance.contains("Do not search for another locator or scan the home directory"));
    assert!(guidance.contains("do not broaden the search"));
    assert!(guidance.contains(
        "does not require copying the person's locator or practice files into Surf MCP calls"
    ));
    assert!(guidance
        .contains("Keep the locator path and local practice content out of guidance retrieval"));
    assert!(compact(SKILL).contains(
        "Never send the person's prompt, conversation, or practice-file contents to Surf tools."
    ));
    assert!(PRIVACY.contains("the local locator path or its contents"));
}

#[test]
fn provider_neutral_plugin_remains_a_thin_guidance_handoff() {
    let skill = compact(SKILL);
    assert!(skill.contains("name: next-step"));
    assert!(skill.contains("source of current Surf guidance"));
    assert!(skill.contains("call the Surf MCP tool named `quickstart` once"));
    assert!(skill.contains("retrieve further guides, references, or product documentation only as the current quickstart and the person's request require"));
    assert!(!skill.contains("locator"));
    assert!(!SKILL.contains("schema_version"));
    assert!(!SKILL.contains("locator.json"));
    assert!(SKILL.len() <= 2_500);

    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("plugins/surf");
    for file in plugin_files(&root) {
        let path = file.to_string_lossy();
        assert!(
            !["bin", "hooks", "scripts"]
                .iter()
                .any(|part| file.iter().any(|value| value == *part)),
            "guidance-only package contains runtime directory: {path}"
        );
        assert!(
            !matches!(
                file.extension().and_then(|value| value.to_str()),
                Some("sh" | "py" | "js" | "ts" | "exe")
            ),
            "guidance-only package contains executable/helper candidate: {path}"
        );
    }
}

#[test]
fn dated_acceptance_distinguishes_contract_tests_from_unrun_live_clients() {
    let acceptance = compact(ACCEPTANCE);
    let release_acceptance = compact(RELEASE_ACCEPTANCE);
    assert!(acceptance.contains("It does not claim that prose-contract tests prove"));
    assert!(acceptance.contains("Claude Code 2.1.231 | Not run"));
    assert!(acceptance.contains("ChatGPT/Codex Desktop | Not run"));
    assert!(acceptance.contains("natural-language plugin activation"));
    assert!(acceptance.contains("sandbox denial"));
    assert!(acceptance.contains("no first-setup question, parent/home scan"));
    assert!(release_acceptance.contains(
        "ask `what's my current Surf goal?` as a natural-language request, without an explicit plugin invocation or path"
    ));
    assert!(!release_acceptance.contains("without naming Surf"));
}
