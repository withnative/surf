// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-only

//! Verified source identity for the running binary.
//!
//! `build.rs` writes `VERIFIED_SOURCE` only after checking an explicit commit
//! and exact public URL. It never reads `.git`: an ordinary checkout, archive,
//! or private predecessor therefore reports source metadata as unavailable
//! instead of manufacturing a plausible but false link.

use crate::framework;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct VerifiedSource {
    pub git_sha: &'static str,
    pub url: &'static str,
    pub build_date: Option<&'static str>,
}

include!(concat!(env!("OUT_DIR"), "/source_metadata.rs"));

pub const SURF_APPLICATION_VERSION: &str = env!("CARGO_PKG_VERSION");

pub fn verified() -> Option<&'static VerifiedSource> {
    VERIFIED_SOURCE.as_ref()
}

pub fn instruction() -> String {
    instruction_for(verified())
}

fn instruction_for(source: Option<&VerifiedSource>) -> String {
    match source {
        Some(source) => format!(
            "Source for this running version: {} (Surf application version {}; working framework version {}; full Git commit {}).",
            source.url,
            SURF_APPLICATION_VERSION,
            framework::LATEST,
            source.git_sha,
        ),
        None => format!(
            "Source for this running version is unavailable: this build has no verified SURF_GIT_SHA and SURF_SOURCE_URL metadata (Surf application version {}; working framework version {}).",
            SURF_APPLICATION_VERSION,
            framework::LATEST,
        ),
    }
}

pub fn markdown() -> String {
    let mut body = format!("# Source for this running version\n\n{}\n", instruction());
    if let Some(source) = verified() {
        if let Some(date) = source.build_date {
            body.push_str(&format!("\n- Build date: `{date}`\n"));
        }
        body.push_str(
            "\nThe URL identifies the immutable public revision compiled into this service.\n",
        );
    } else {
        body.push_str(
            "\nThis fail-closed response is expected for ordinary local and source-archive builds. Production builds must supply both values explicitly; Surf does not infer a public source URL from the checkout that happens to run the build.\n",
        );
    }
    body
}

#[cfg(test)]
mod tests {
    use super::*;

    const SHA: &str = "0123456789abcdef0123456789abcdef01234567";
    const URL: &str =
        "https://github.com/withnative/surf/commit/0123456789abcdef0123456789abcdef01234567";

    #[test]
    fn verified_instruction_names_every_required_identity() {
        let source = VerifiedSource {
            git_sha: SHA,
            url: URL,
            build_date: Some("2026-08-12T20:00:00Z"),
        };
        let text = instruction_for(Some(&source));
        assert!(text.contains(URL));
        assert!(text.contains(SHA));
        assert!(text.contains(SURF_APPLICATION_VERSION));
        assert!(text.contains(framework::LATEST));
        assert!(text.contains("Surf application version"));
        assert!(text.contains("working framework version"));
    }

    #[test]
    fn ordinary_build_fails_closed_without_inventing_a_repository_revision() {
        let text = instruction_for(None);
        assert!(text.contains("unavailable"));
        assert!(text.contains("SURF_GIT_SHA"));
        assert!(!text.contains("github.com/withnative/surf/commit/"));
    }

    #[test]
    fn resource_document_repeats_the_initialization_source_statement() {
        assert!(markdown().contains(&instruction()));
    }
}
