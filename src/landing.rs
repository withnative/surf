// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-only

//! Minimal source-level front door. Framework content stays in the MCP artefacts.
//!
//! The page is authored as plain files under `web/landing/` and embedded at
//! compile time: no framework, no build step, and no template engine.

pub const INDEX: &str = include_str!("../web/landing/index.html");

pub const CSS: &str = include_str!("../web/landing/_landing.css");
