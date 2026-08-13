// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-or-later

use std::env;
use std::fs;
use std::path::PathBuf;

const PUBLIC_COMMIT_PREFIX: &str = "https://github.com/withnative/surf/commit/";

fn main() {
    println!("cargo:rerun-if-env-changed=SURF_GIT_SHA");
    println!("cargo:rerun-if-env-changed=SURF_SOURCE_URL");
    println!("cargo:rerun-if-env-changed=SURF_BUILD_DATE");

    let sha = env::var("SURF_GIT_SHA");
    let url = env::var("SURF_SOURCE_URL");
    let build_date = env::var("SURF_BUILD_DATE");

    let generated = match (sha, url) {
        (Err(env::VarError::NotPresent), Err(env::VarError::NotPresent)) => {
            match build_date {
                Err(env::VarError::NotPresent) => {}
                Ok(_) => panic!("SURF_BUILD_DATE cannot identify source by itself; set both SURF_GIT_SHA and SURF_SOURCE_URL"),
                Err(env::VarError::NotUnicode(_)) => {
                    panic!("SURF_BUILD_DATE must be valid UTF-8 when set")
                }
            }
            "pub const VERIFIED_SOURCE: Option<VerifiedSource> = None;\n".to_string()
        }
        (Ok(sha), Ok(url)) => {
            validate_sha(&sha);
            let expected = format!("{PUBLIC_COMMIT_PREFIX}{sha}");
            if url != expected {
                panic!(
                    "SURF_SOURCE_URL must be the exact public Surf commit URL `{expected}` for SURF_GIT_SHA"
                );
            }
            let build_date = match build_date {
                Ok(value) => {
                    if value.trim().is_empty()
                        || value != value.trim()
                        || value.contains('\r')
                        || value.contains('\n')
                    {
                        panic!("SURF_BUILD_DATE must be a non-empty, single-line value when set");
                    }
                    format!("Some({value:?})")
                }
                Err(env::VarError::NotPresent) => "None".to_string(),
                Err(env::VarError::NotUnicode(_)) => {
                    panic!("SURF_BUILD_DATE must be valid UTF-8 when set")
                }
            };
            format!(
                "pub const VERIFIED_SOURCE: Option<VerifiedSource> = Some(VerifiedSource {{ git_sha: {sha:?}, url: {url:?}, build_date: {build_date} }});\n"
            )
        }
        (Err(env::VarError::NotUnicode(_)), _) => panic!("SURF_GIT_SHA must be valid UTF-8"),
        (_, Err(env::VarError::NotUnicode(_))) => panic!("SURF_SOURCE_URL must be valid UTF-8"),
        _ => panic!("SURF_GIT_SHA and SURF_SOURCE_URL must either both be set or both be absent"),
    };

    let out = PathBuf::from(env::var_os("OUT_DIR").expect("Cargo must set OUT_DIR"));
    fs::write(out.join("source_metadata.rs"), generated)
        .expect("failed to write verified source metadata");
}

fn validate_sha(sha: &str) {
    if sha.len() != 40
        || !sha
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        panic!("SURF_GIT_SHA must be a full 40-character lowercase hexadecimal commit SHA");
    }
}
