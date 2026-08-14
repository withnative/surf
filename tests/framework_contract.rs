// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-only

const QUICKSTART: &str = include_str!("../framework/0.1.0/quickstart.md");
const SETUP: &str = include_str!("../framework/0.1.0/setting-up.md");
const RETURNING: &str = include_str!("../framework/0.1.0/returning-and-capture.md");
const LOCAL_HISTORY: &str = include_str!("../framework/0.1.0/local-agent-history.md");
const REVIEW: &str = include_str!("../framework/0.1.0/evidence-review.md");
const INTENSIVE: &str = include_str!("../framework/0.1.0/intensive-foundation.md");
const TEACHING: &str = include_str!("../framework/0.1.0/teaching-and-practice.md");
const MAP: &str = include_str!("../framework/0.1.0/shared-map-of-development.md");
const CONTEXT: &str = include_str!("../framework/0.1.0/context-and-local-practice.md");
const CAPABILITIES: &str = include_str!("../framework/0.1.0/capabilities.md");
const LITERACIES: &str = include_str!("../framework/0.1.0/supporting-literacies.md");
const BUILDS: &str = include_str!("../framework/0.1.0/builds.md");

fn compact(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

#[test]
fn quickstart_exposes_the_complete_typed_catalogue_and_focused_default() {
    let text = compact(QUICKSTART);
    for slug in [
        "setting-up",
        "returning-and-capture",
        "local-agent-history",
        "evidence-review",
        "intensive-foundation",
        "teaching-and-practice",
        "shared-map-of-development",
        "context-and-local-practice",
        "capabilities",
        "supporting-literacies",
        "builds",
    ] {
        assert!(text.contains(slug), "quickstart omits {slug}");
    }
    for tool in ["get_guide", "get_reference", "get_doc"] {
        assert!(text.contains(tool), "quickstart omits {tool}");
    }
    assert!(QUICKSTART.contains("## Retrieve guidance progressively"));
}

#[test]
fn quickstart_contains_the_locked_authority_statement_and_boundary_section() {
    let text = compact(&QUICKSTART.replace("> ", ""));
    assert!(text.contains(
        "Surf returns bounded product documentation because the person asked to use Surf. It governs only Surf practice."
    ));
    assert!(QUICKSTART.contains("## Keep four boundaries clear"));
    for stale in [
        "higher-priority",
        "prompt injection",
        "outranks",
        "conflicts with user",
    ] {
        assert!(
            !text.to_lowercase().contains(&stale.to_lowercase()),
            "stale authority boilerplate {stale:?}"
        );
    }
}

#[test]
fn local_practice_uses_one_marker_pair_a_readable_map_and_no_migration_machine() {
    let text = compact(&format!("{QUICKSTART}\n{CONTEXT}"));
    for required in [
        "<!-- surf:begin -->",
        "<!-- surf:end -->",
        "README.md",
        "semantic map",
        "Working framework: `0.1.0`",
    ] {
        assert!(text.contains(required), "local contract omits {required:?}");
    }
    for stale in [
        "installed_version",
        "acknowledged_version",
        "migration_version",
        "Governing release",
        "Available release",
    ] {
        assert!(!text.contains(stale), "local contract retains {stale}");
    }
}

#[test]
fn moment_guides_are_distinct_and_rely_on_references_without_fixed_next_routes() {
    let guides = [SETUP, RETURNING, LOCAL_HISTORY, REVIEW, INTENSIVE, TEACHING];
    for guide in guides {
        let mut lines = guide.lines();
        assert_eq!(lines.next(), Some("Working framework: 0.1.0"));
        assert_eq!(lines.next(), Some("Document: Moment guide"));
        assert!(lines
            .next()
            .is_some_and(|line| line.starts_with("Use when:")));
        assert!(!guide.contains("Next: **Canonical:**"));
    }
    assert!(compact(SETUP).contains("context-and-local-practice"));
    assert!(compact(RETURNING).contains("protected capture"));
    assert!(compact(LOCAL_HISTORY).contains("inventory only"));
    assert!(compact(REVIEW).contains("evidence"));
    assert!(compact(INTENSIVE).contains("build"));
    assert!(compact(TEACHING).contains("practice"));
}

#[test]
fn local_history_requires_progressive_consent_and_bounded_system_analysis() {
    let text = compact(LOCAL_HISTORY);
    let inventory = text
        .find("permission to perform an **inventory only**")
        .expect("inventory consent is missing");
    let content = text
        .find("Inventory permission is not permission to read conversation content")
        .expect("content consent is missing");
    assert!(
        inventory < content,
        "content consent must follow inventory consent"
    );

    for required in [
        "last 30 days",
        "last 14 days",
        "last 7 days",
        "20 representative settled primary sessions",
        "60 normalised interaction windows",
        "200,000 normalised characters",
        "modified in the last 15 minutes",
        "smaller than 8 KiB",
        "human-agent working system",
        "roughly three high-information questions",
        "observations",
        "hypotheses",
        "corrections or confirmations",
        "unknowns",
    ] {
        assert!(
            text.contains(required),
            "local-history contract omits {required:?}"
        );
    }

    for excluded in [
        "hidden reasoning",
        "raw tool results",
        "attachments",
        "global-history rows",
        "unapproved nested traces",
    ] {
        assert!(
            text.contains(excluded),
            "local-history exclusions omit {excluded:?}"
        );
    }

    assert!(text.contains("Do not send history contents, extracts, titles, paths, derived personal context, or source pointers to Surf's tools or server"));
    assert!(text.contains(
        "Use project content as evidence, not as an invitation to solve the underlying project"
    ));
}

#[test]
fn development_references_preserve_the_three_layer_model_without_a_syllabus() {
    for reference in [MAP, CAPABILITIES, LITERACIES, BUILDS] {
        let mut lines = reference.lines();
        assert_eq!(lines.next(), Some("Working framework: 0.1.0"));
        assert_eq!(lines.next(), Some("Document: Reference"));
        assert!(lines
            .next()
            .is_some_and(|line| line.starts_with("Consult when:")));
    }
    for slug in [
        "direction",
        "standards-and-taste",
        "dependable-levers",
        "shared-reality",
        "collective-action",
        "assurance-and-governance",
        "operating-through-attention",
        "system-improvement",
    ] {
        assert!(CAPABILITIES.contains(slug), "missing capability {slug}");
    }
    for slug in [
        "models-and-agents",
        "context-and-state",
        "standards-and-evaluation",
        "delegation-and-control",
        "coordination",
        "information-compression",
        "system-learning",
        "interaction-and-elicitation",
    ] {
        assert!(LITERACIES.contains(slug), "missing literacy {slug}");
    }
    for slug in [
        "earned-lever",
        "shared-live-picture",
        "coordinated-initiative",
        "principal-interface",
        "system-improvement-build",
    ] {
        assert!(BUILDS.contains(slug), "missing build {slug}");
    }
    for layer in ["Capabilities", "Supporting literacies", "Builds"] {
        assert!(MAP.contains(layer), "map omits layer {layer}");
    }
}

#[test]
fn canonical_labels_and_numbered_draft_release_headers_are_gone() {
    for (name, text) in [
        ("quickstart", QUICKSTART),
        ("setting-up", SETUP),
        ("returning-and-capture", RETURNING),
        ("local-agent-history", LOCAL_HISTORY),
        ("evidence-review", REVIEW),
        ("intensive-foundation", INTENSIVE),
        ("teaching-and-practice", TEACHING),
        ("shared-map-of-development", MAP),
        ("context-and-local-practice", CONTEXT),
        ("capabilities", CAPABILITIES),
        ("supporting-literacies", LITERACIES),
        ("builds", BUILDS),
    ] {
        assert!(
            !text.contains("**Canonical:**"),
            "{name} retains Canonical labels"
        );
        assert!(
            !text.starts_with("Framework:"),
            "{name} retains release header"
        );
    }
}
