// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-or-later

//! surf.withnative.ai — a public, stateless MCP briefing server.

mod docs;
mod framework;
mod landing;
mod protocol;
mod source;
mod tools;

use std::net::SocketAddr;

use axum::body::Bytes;
use axum::extract::Path;
use axum::http::{header, HeaderMap, HeaderValue, StatusCode};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::Router;
use serde_json::Value;

use protocol::Outcome;

#[tokio::main]
async fn main() {
    let port: u16 = std::env::var("PORT")
        .ok()
        .and_then(|port| port.parse().ok())
        .unwrap_or(8080);
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .unwrap_or_else(|err| panic!("cannot bind {addr}: {err}"));
    eprintln!(
        "Surf application version {} serving working framework version {} on http://{addr}",
        env!("CARGO_PKG_VERSION"),
        framework::WORKING_VERSION
    );
    axum::serve(listener, app())
        .with_graceful_shutdown(shutdown())
        .await
        .expect("server failed");
}

fn app() -> Router {
    Router::new()
        .route("/mcp", post(mcp).get(mcp_get).options(preflight))
        .route("/", get(index))
        .route("/assets/landing.css", get(stylesheet))
        .route("/docs/{slug}", get(document_markdown))
        .route("/source", get(running_source))
        .route("/framework", get(framework_manifest_markdown))
        .route("/framework/quickstart.md", get(quickstart_markdown))
        .route("/guides/{slug}", get(guide_markdown))
        .route("/references/{slug}", get(reference_markdown))
        .route("/changelog.md", get(changelog_markdown))
        .route("/health", get(|| async { "ok" }))
}

async fn shutdown() {
    let _ = tokio::signal::ctrl_c().await;
}

fn cors(response: &mut Response) {
    let headers = response.headers_mut();
    headers.insert(
        header::ACCESS_CONTROL_ALLOW_ORIGIN,
        HeaderValue::from_static("*"),
    );
    headers.insert(
        header::ACCESS_CONTROL_ALLOW_METHODS,
        HeaderValue::from_static("POST, GET, OPTIONS"),
    );
    headers.insert(
        header::ACCESS_CONTROL_ALLOW_HEADERS,
        HeaderValue::from_static("content-type, accept, mcp-protocol-version, mcp-session-id"),
    );
    headers.insert(
        header::ACCESS_CONTROL_MAX_AGE,
        HeaderValue::from_static("86400"),
    );
}

async fn preflight() -> Response {
    let mut response = StatusCode::NO_CONTENT.into_response();
    cors(&mut response);
    response
}

async fn mcp_get() -> Response {
    let mut response = (
        StatusCode::METHOD_NOT_ALLOWED,
        [(header::ALLOW, "POST, OPTIONS")],
        "This server sends no unsolicited messages. POST JSON-RPC to /mcp.",
    )
        .into_response();
    cors(&mut response);
    response
}

async fn mcp(headers: HeaderMap, body: Bytes) -> Response {
    if let Some(content_type) = headers.get(header::CONTENT_TYPE) {
        let ok = content_type
            .to_str()
            .map(|value| value.split(';').next().unwrap_or("").trim())
            .map(|value| value.eq_ignore_ascii_case("application/json"))
            .unwrap_or(false);
        if !ok {
            return json_rpc(
                StatusCode::UNSUPPORTED_MEDIA_TYPE,
                protocol::error_response(
                    Value::Null,
                    protocol::INVALID_REQUEST,
                    "Content-Type must be application/json",
                ),
            );
        }
    }

    let message: Value = match serde_json::from_slice(&body) {
        Ok(message) => message,
        Err(err) => {
            return json_rpc(
                StatusCode::BAD_REQUEST,
                protocol::error_response(
                    Value::Null,
                    protocol::PARSE_ERROR,
                    &format!("parse error: {err}"),
                ),
            )
        }
    };

    if let Err(message) = protocol::validate_envelope(&message) {
        return json_rpc(
            StatusCode::BAD_REQUEST,
            protocol::error_response(Value::Null, protocol::INVALID_REQUEST, message),
        );
    }
    if let Err(version_error) = validate_protocol_version(&headers) {
        return json_rpc(
            StatusCode::BAD_REQUEST,
            protocol::error_response(
                protocol::request_id(&message),
                protocol::INVALID_REQUEST,
                &version_error,
            ),
        );
    }

    match protocol::dispatch(&message) {
        Outcome::Notification => accepted(),
        Outcome::RejectedNotification => bad_request_without_body(),
        Outcome::Response(body) => json_rpc(StatusCode::OK, body),
    }
}

fn validate_protocol_version(headers: &HeaderMap) -> Result<(), String> {
    let values: Vec<_> = headers.get_all("mcp-protocol-version").iter().collect();
    if values.is_empty() {
        return Ok(());
    }
    if values.len() != 1 {
        return Err("MCP-Protocol-Version must appear exactly once".into());
    }
    let version = values[0]
        .to_str()
        .map_err(|_| "MCP-Protocol-Version is malformed".to_string())?;
    let bytes = version.as_bytes();
    let well_formed = bytes.len() == 10
        && bytes[4] == b'-'
        && bytes[7] == b'-'
        && bytes
            .iter()
            .enumerate()
            .all(|(index, byte)| matches!(index, 4 | 7) || byte.is_ascii_digit());
    if !well_formed {
        return Err(format!("malformed MCP-Protocol-Version `{version}`"));
    }
    if !protocol::supports_protocol_version(version) {
        return Err(format!(
            "unsupported MCP-Protocol-Version `{version}`; supported: {}",
            protocol::supported_protocol_versions().join(", ")
        ));
    }
    Ok(())
}

fn accepted() -> Response {
    let mut response = StatusCode::ACCEPTED.into_response();
    cors(&mut response);
    response
}

fn bad_request_without_body() -> Response {
    let mut response = StatusCode::BAD_REQUEST.into_response();
    cors(&mut response);
    response
}

fn json_rpc(status: StatusCode, body: Value) -> Response {
    let mut response = (status, axum::Json(body)).into_response();
    cors(&mut response);
    response
}

fn html(body: &'static str) -> Response {
    ([(header::CONTENT_TYPE, "text/html; charset=utf-8")], body).into_response()
}

fn markdown(body: String) -> Response {
    (
        [(header::CONTENT_TYPE, "text/markdown; charset=utf-8")],
        body,
    )
        .into_response()
}

async fn index() -> Response {
    html(landing::INDEX)
}

async fn stylesheet() -> Response {
    (
        [
            (header::CONTENT_TYPE, "text/css; charset=utf-8"),
            (header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        landing::CSS,
    )
        .into_response()
}

async fn document_markdown(Path(slug): Path<String>) -> Response {
    match docs::find(&slug) {
        Some(doc) => markdown(doc.markdown.to_string()),
        None => not_found(format!("No product document `{slug}`. See /docs/index.\n")),
    }
}

async fn running_source() -> Response {
    match source::verified() {
        Some(source) => (
            StatusCode::TEMPORARY_REDIRECT,
            [(header::LOCATION, source.url)],
            source::markdown(),
        )
            .into_response(),
        None => (
            StatusCode::SERVICE_UNAVAILABLE,
            [(header::CONTENT_TYPE, "text/markdown; charset=utf-8")],
            source::markdown(),
        )
            .into_response(),
    }
}

async fn framework_manifest_markdown() -> Response {
    markdown(framework::manifest())
}

async fn quickstart_markdown() -> Response {
    markdown(framework::QUICKSTART.to_string())
}

async fn guide_markdown(Path(slug): Path<String>) -> Response {
    let slug = slug.strip_suffix(".md").unwrap_or(&slug);
    match framework::guide(slug) {
        Some(document) => markdown(document.text.to_string()),
        None => not_found(format!("No moment guide `{slug}`. See /framework.\n")),
    }
}

async fn reference_markdown(Path(slug): Path<String>) -> Response {
    let slug = slug.strip_suffix(".md").unwrap_or(&slug);
    match framework::reference(slug) {
        Some(document) => markdown(document.text.to_string()),
        None => not_found(format!("No reference `{slug}`. See /framework.\n")),
    }
}

async fn changelog_markdown() -> Response {
    markdown(framework::CHANGELOG.to_string())
}

fn not_found(message: String) -> Response {
    (
        StatusCode::NOT_FOUND,
        [(header::CONTENT_TYPE, "text/plain; charset=utf-8")],
        message,
    )
        .into_response()
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Method, Request};
    use http_body_util::BodyExt;
    use serde_json::json;
    use tower::ServiceExt;

    async fn send(request: Request<Body>) -> (StatusCode, Vec<u8>) {
        let response = app().oneshot(request).await.unwrap();
        let status = response.status();
        let body = response.into_body().collect().await.unwrap().to_bytes();
        (status, body.to_vec())
    }

    fn request(method: Method, uri: &str, body: Body) -> Request<Body> {
        Request::builder()
            .method(method)
            .uri(uri)
            .body(body)
            .unwrap()
    }

    fn mcp_request(message: Value) -> Request<Body> {
        Request::builder()
            .method(Method::POST)
            .uri("/mcp")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(message.to_string()))
            .unwrap()
    }

    #[tokio::test]
    async fn current_http_catalogue_is_readable_and_old_release_routes_are_gone() {
        for path in [
            "/framework",
            "/framework/quickstart.md",
            "/guides/setting-up.md",
            "/references/shared-map-of-development.md",
            "/changelog.md",
            "/docs/index",
        ] {
            let (status, body) = send(request(Method::GET, path, Body::empty())).await;
            assert_eq!(status, StatusCode::OK, "{path}");
            assert!(!body.is_empty(), "{path}");
        }
        for path in [
            "/releases/0.3.0",
            "/releases/0.3.0/quickstart.md",
            "/guides/missing.md",
            "/references/missing.md",
        ] {
            let (status, _) = send(request(Method::GET, path, Body::empty())).await;
            assert_eq!(status, StatusCode::NOT_FOUND, "{path}");
        }
    }

    #[tokio::test]
    async fn http_product_documents_match_the_canonical_markdown_bytes() {
        for doc in docs::all() {
            let path = format!("/docs/{}", doc.slug);
            let (status, body) = send(request(Method::GET, &path, Body::empty())).await;
            assert_eq!(status, StatusCode::OK, "{}", doc.slug);
            assert_eq!(body, doc.markdown.as_bytes(), "{}", doc.slug);
        }
    }

    #[tokio::test]
    async fn landing_names_the_application_and_working_framework_versions() {
        let (status, body) = send(request(Method::GET, "/", Body::empty())).await;
        assert_eq!(status, StatusCode::OK);
        let body = String::from_utf8(body).unwrap();
        assert!(body.contains(concat!(
            "Surf application version ",
            env!("CARGO_PKG_VERSION")
        )));
        assert!(body.contains(&format!(
            "Working framework version {}",
            framework::WORKING_VERSION
        )));
    }

    #[tokio::test]
    async fn real_mcp_surface_exposes_all_four_tools() {
        let (_, response) = send(mcp_request(json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })))
        .await;
        let response: Value = serde_json::from_slice(&response).unwrap();
        let names = response["result"]["tools"]
            .as_array()
            .unwrap()
            .iter()
            .map(|tool| tool["name"].as_str().unwrap())
            .collect::<Vec<_>>();
        assert_eq!(
            names,
            ["quickstart", "get_guide", "get_reference", "get_doc"]
        );
    }

    #[tokio::test]
    async fn cors_and_protocol_validation_remain_explicit() {
        let response = app()
            .oneshot(request(Method::OPTIONS, "/mcp", Body::empty()))
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::NO_CONTENT);
        assert_eq!(response.headers()[header::ACCESS_CONTROL_ALLOW_ORIGIN], "*");

        let mut request = mcp_request(json!({
            "jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}
        }));
        request.headers_mut().insert(
            "mcp-protocol-version",
            HeaderValue::from_static("not-a-date"),
        );
        let (status, _) = send(request).await;
        assert_eq!(status, StatusCode::BAD_REQUEST);
    }
}
