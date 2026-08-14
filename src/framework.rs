// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-only

//! The single pre-production Surf framework compiled into the server.

/// Surf works against one freely revisable framework until a real production
/// practice creates a compatibility obligation.
pub const WORKING_VERSION: &str = "0.1.0";

/// Kept as a concise identity for source and landing metadata.
pub const LATEST: &str = WORKING_VERSION;

pub const CHANGELOG: &str = include_str!("../framework/CHANGELOG.md");
pub const QUICKSTART: &str = include_str!("../framework/0.1.0/quickstart.md");

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DocumentKind {
    MomentGuide,
    Reference,
}

impl DocumentKind {
    pub fn label(self) -> &'static str {
        match self {
            Self::MomentGuide => "Moment guide",
            Self::Reference => "Reference",
        }
    }
}

/// One progressively retrieved framework document.
pub struct Document {
    pub slug: &'static str,
    pub title: &'static str,
    pub description: &'static str,
    pub kind: DocumentKind,
    pub text: &'static str,
}

pub static GUIDES: &[Document] = &[
    Document {
        slug: "setting-up",
        title: "Setting up",
        description: "Use when establishing or recovering a Surf practice, agreeing how it should work, and activating a useful first route.",
        kind: DocumentKind::MomentGuide,
        text: include_str!("../framework/0.1.0/setting-up.md"),
    },
    Document {
        slug: "returning-and-capture",
        title: "Returning and capture",
        description: "Use when a Surf practice exists and the person is returning, reporting an experience, or changing retained context directly.",
        kind: DocumentKind::MomentGuide,
        text: include_str!("../framework/0.1.0/returning-and-capture.md"),
    },
    Document {
        slug: "evidence-review",
        title: "Evidence review",
        description: "Use when looking across evidence, correcting the current account, reaching an experiment verdict, or choosing what to try next.",
        kind: DocumentKind::MomentGuide,
        text: include_str!("../framework/0.1.0/evidence-review.md"),
    },
    Document {
        slug: "intensive-foundation",
        title: "Intensive foundation",
        description: "Use for a concentrated period of explanation, mapping, guided practice, and meaningful system building.",
        kind: DocumentKind::MomentGuide,
        text: include_str!("../framework/0.1.0/intensive-foundation.md"),
    },
    Document {
        slug: "teaching-and-practice",
        title: "Teaching and practice",
        description: "Use for explanation, correctable mapping, guided practice, and understanding checks.",
        kind: DocumentKind::MomentGuide,
        text: include_str!("../framework/0.1.0/teaching-and-practice.md"),
    },
];

pub static REFERENCES: &[Document] = &[
    Document {
        slug: "shared-map-of-development",
        title: "Shared map of development",
        description: "Consult when Surf's three-layer development model can improve calibration, teaching, review, or selection of a useful focus.",
        kind: DocumentKind::Reference,
        text: include_str!("../framework/0.1.0/shared-map-of-development.md"),
    },
    Document {
        slug: "context-and-local-practice",
        title: "Context and local practice",
        description: "Consult when locating, validating, reading, maintaining, repairing, or explaining the person's inspectable Surf practice.",
        kind: DocumentKind::Reference,
        text: include_str!("../framework/0.1.0/context-and-local-practice.md"),
    },
    Document {
        slug: "capabilities",
        title: "Capabilities",
        description: "Consult when durable human-agent system capability, evidence, failure, or a possible next capability focus is relevant.",
        kind: DocumentKind::Reference,
        text: include_str!("../framework/0.1.0/capabilities.md"),
    },
    Document {
        slug: "supporting-literacies",
        title: "Supporting literacies",
        description: "Consult when a practical or conceptual mechanism would help the person build, inspect, govern, recover, or transfer capability.",
        kind: DocumentKind::Reference,
        text: include_str!("../framework/0.1.0/supporting-literacies.md"),
    },
    Document {
        slug: "builds",
        title: "Builds",
        description: "Consult when selecting, running, challenging, or reviewing a meaningful project through which capability becomes inspectable.",
        kind: DocumentKind::Reference,
        text: include_str!("../framework/0.1.0/builds.md"),
    },
];

pub fn guide(slug: &str) -> Option<&'static Document> {
    GUIDES.iter().find(|document| document.slug == slug)
}

pub fn reference(slug: &str) -> Option<&'static Document> {
    REFERENCES.iter().find(|document| document.slug == slug)
}

pub fn manifest() -> String {
    let mut out = format!(
        "Working framework: {WORKING_VERSION}\nDocument: Framework manifest\nRole: Catalogue of Surf's current pre-production guidance.\n\n# Surf working framework {WORKING_VERSION}\n\nSurf is currently developed as one freely revisable pre-production framework. Git history and workspace decisions preserve development history; this catalogue does not promise compatibility with earlier drafts.\n\n## Quickstart\n\n- **Quickstart** (`quickstart`) — resident orientation, product spine, boundaries, and routing.\n\n## Moment guides\n\n"
    );
    for guide in GUIDES {
        out.push_str(&format!(
            "- **{}** (`{}`) — {}. {}\n",
            guide.title,
            guide.slug,
            guide.kind.label(),
            guide.description
        ));
    }
    out.push_str("\n## References\n\n");
    for reference in REFERENCES {
        out.push_str(&format!(
            "- **{}** (`{}`) — {}. {}\n",
            reference.title,
            reference.slug,
            reference.kind.label(),
            reference.description
        ));
    }
    out.push_str("\nProduct documents explain Surf itself and remain separate from this framework. MCP resources mirror the catalogue; the tools are the primary retrieval path.\n");
    out
}

#[cfg(test)]
pub fn has_complete_header(text: &str) -> bool {
    let mut lines = text.lines();
    if lines.next() != Some("Working framework: 0.1.0") {
        return false;
    }
    match lines.next() {
        Some("Document: Quickstart") => lines
            .next()
            .is_some_and(|line| line.starts_with("Role:") && line.len() > "Role:".len()),
        Some("Document: Moment guide") => lines
            .next()
            .is_some_and(|line| line.starts_with("Use when:") && line.len() > "Use when:".len()),
        Some("Document: Reference") => lines.next().is_some_and(|line| {
            line.starts_with("Consult when:") && line.len() > "Consult when:".len()
        }),
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn catalogue_has_one_working_version_and_distinct_kinds() {
        assert_eq!(WORKING_VERSION, "0.1.0");
        assert_eq!(GUIDES.len(), 5);
        assert_eq!(REFERENCES.len(), 5);
        assert!(GUIDES
            .iter()
            .all(|document| document.kind == DocumentKind::MomentGuide));
        assert!(REFERENCES
            .iter()
            .all(|document| document.kind == DocumentKind::Reference));
        let slugs = GUIDES
            .iter()
            .chain(REFERENCES)
            .map(|document| document.slug)
            .collect::<HashSet<_>>();
        assert_eq!(slugs.len(), GUIDES.len() + REFERENCES.len());
    }

    #[test]
    fn every_document_is_nonempty_and_has_its_kind_specific_header() {
        assert!(has_complete_header(QUICKSTART));
        assert!(QUICKSTART.len() > 400);
        for document in GUIDES.iter().chain(REFERENCES) {
            assert!(document.text.len() > 400, "{} is too small", document.slug);
            assert!(
                has_complete_header(document.text),
                "{} header",
                document.slug
            );
            assert!(!document.title.is_empty());
            assert!(!document.description.is_empty());
        }
    }

    #[test]
    fn manifest_names_kinds_without_calling_authored_references_resources() {
        let text = manifest();
        assert!(text.contains("## Moment guides"));
        assert!(text.contains("## References"));
        for document in GUIDES.iter().chain(REFERENCES) {
            assert!(text.contains(document.slug));
        }
    }
}
