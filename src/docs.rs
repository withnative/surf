// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-or-later

//! Current product documentation, compiled from the repository's canonical Markdown.
//!
//! This catalogue is deliberately explicit. Adding a file under `docs/` does not
//! silently publish it through MCP or HTTP; a maintainer must choose its public
//! title, description, and stable slug here.

pub struct Doc {
    pub slug: &'static str,
    pub title: &'static str,
    pub description: &'static str,
    pub markdown: &'static str,
}

pub static DOCS: &[Doc] = &[
    Doc {
        slug: "index",
        title: "Surf documentation",
        description: "Catalogue of Surf's current product documentation.",
        markdown: include_str!("../docs/index.md"),
    },
    Doc {
        slug: "faq",
        title: "Frequently asked questions",
        description:
            "Short answers about Surf, its boundaries, working framework, and support posture.",
        markdown: include_str!("../docs/faq.md"),
    },
    Doc {
        slug: "why-surf",
        title: "Why Surf",
        description: "Richard Ng's canonical account of why Surf exists.",
        markdown: include_str!("../docs/why-surf.md"),
    },
    Doc {
        slug: "why-mcp",
        title: "Why Surf uses MCP",
        description: "Why Surf delivers a current framework through a managed MCP host.",
        markdown: include_str!("../docs/why-mcp.md"),
    },
    Doc {
        slug: "why-open-source",
        title: "Why Surf is free and open source",
        description: "Why free access and open source follow from Surf's mission and agency.",
        markdown: include_str!("../docs/why-open-source.md"),
    },
    Doc {
        slug: "how-surf-works",
        title: "How Surf works",
        description:
            "The server, agent, local practice, working framework, and delivery architecture.",
        markdown: include_str!("../docs/how-surf-works.md"),
    },
    Doc {
        slug: "privacy-and-data",
        title: "Privacy and data",
        description:
            "What reaches Surf, what stays local, and the boundaries Surf does not control.",
        markdown: include_str!("../docs/privacy-and-data.md"),
    },
    Doc {
        slug: "compatibility",
        title: "Client compatibility",
        description: "Verified, expected, and untested Surf client surfaces.",
        markdown: include_str!("../docs/compatibility.md"),
    },
    Doc {
        slug: "about-richard",
        title: "About Richard",
        description: "Richard Ng's creator story, biography, and relationship to Native.",
        markdown: include_str!("../docs/about-richard.md"),
    },
    Doc {
        slug: "releases-and-source",
        title: "Working framework and source",
        description: "Surf's pre-production framework policy and exact running source.",
        markdown: include_str!("../docs/releases-and-source.md"),
    },
];

pub fn all() -> &'static [Doc] {
    DOCS
}

pub fn find(slug: &str) -> Option<&'static Doc> {
    DOCS.iter().find(|doc| doc.slug == slug)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn catalogue_is_the_explicit_ten_document_public_set() {
        let slugs: Vec<_> = all().iter().map(|doc| doc.slug).collect();
        assert_eq!(
            slugs,
            [
                "index",
                "faq",
                "why-surf",
                "why-mcp",
                "why-open-source",
                "how-surf-works",
                "privacy-and-data",
                "compatibility",
                "about-richard",
                "releases-and-source",
            ]
        );
        assert_eq!(slugs.iter().copied().collect::<HashSet<_>>().len(), 10);
    }

    #[test]
    fn compiled_markdown_is_nonempty_and_lf_normalized() {
        for doc in all() {
            assert!(!doc.title.is_empty(), "{}", doc.slug);
            assert!(!doc.description.is_empty(), "{}", doc.slug);
            assert!(!doc.markdown.trim().is_empty(), "{}", doc.slug);
            assert!(!doc.markdown.contains('\r'), "{} is not LF-only", doc.slug);
            assert!(doc.markdown.ends_with('\n'), "{} lacks final LF", doc.slug);
        }
    }

    #[test]
    fn approved_public_copy_has_no_resolved_editorial_markers() {
        let markers = [
            ["EDITORIAL ", "LAUNCH GATE"].concat(),
            ["not approved for ", "publication"].concat(),
        ];
        for slug in ["why-surf", "why-mcp", "why-open-source", "about-richard"] {
            let markdown = find(slug).unwrap().markdown;
            for marker in &markers {
                assert!(!markdown.contains(marker), "{slug}: {marker}");
            }
        }
    }

    #[test]
    fn public_version_policy_names_independent_artifacts_and_no_historical_catalogue() {
        let policy = find("releases-and-source").unwrap().markdown;
        for required in [
            "Surf application version:** `0.1.0`",
            "Working framework version:** `0.1.0`",
            "Plugin package version:** `0.1.0`",
            "does not establish a permanent lockstep",
        ] {
            assert!(
                policy.contains(required),
                "version policy omits {required:?}"
            );
        }

        let why_mcp = find("why-mcp").unwrap().markdown;
        let compact = why_mcp.split_whitespace().collect::<Vec<_>>().join(" ");
        assert!(compact.contains("one freely revisable working framework"));
        assert!(compact.contains("does not promise exact historical framework retrieval"));
        assert!(!why_mcp.contains("exact historical releases remain available"));
    }
}
