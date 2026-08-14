// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-only

//! Minimal, stateless MCP JSON-RPC dispatch.

use serde_json::{json, Value};

use crate::{docs, framework, source, tools};

pub const PROTOCOL_VERSION: &str = "2025-06-18";
const SUPPORTED: [&str; 3] = ["2025-06-18", "2025-03-26", "2024-11-05"];

pub const PARSE_ERROR: i64 = -32700;
pub const INVALID_REQUEST: i64 = -32600;
pub const METHOD_NOT_FOUND: i64 = -32601;
pub const INVALID_PARAMS: i64 = -32602;

pub enum Outcome {
    Notification,
    RejectedNotification,
    Response(Value),
}

pub fn error_response(id: Value, code: i64, message: &str) -> Value {
    json!({
        "jsonrpc": "2.0",
        "id": id,
        "error": { "code": code, "message": message }
    })
}

fn result_response(id: Value, result: Value) -> Value {
    json!({ "jsonrpc": "2.0", "id": id, "result": result })
}

pub fn request_id(message: &Value) -> Value {
    match message.get("id") {
        Some(id @ (Value::String(_) | Value::Number(_) | Value::Null)) => id.clone(),
        _ => Value::Null,
    }
}

pub fn validate_envelope(message: &Value) -> Result<(), &'static str> {
    let Some(object) = message.as_object() else {
        return Err("JSON-RPC message must be an object; batches are not supported");
    };
    if object.get("jsonrpc") != Some(&Value::String("2.0".into())) {
        return Err("`jsonrpc` must be exactly `2.0`");
    }
    if object
        .get("method")
        .and_then(Value::as_str)
        .is_none_or(|method| method.is_empty())
    {
        return Err("`method` must be a non-empty string");
    }
    if object
        .get("id")
        .is_some_and(|id| !matches!(id, Value::String(_) | Value::Number(_) | Value::Null))
    {
        return Err("`id` must be a string, number, or null");
    }
    if object
        .get("params")
        .is_some_and(|params| !params.is_object() && !params.is_array())
    {
        return Err("`params` must be an object or array when present");
    }
    Ok(())
}

pub fn supports_protocol_version(version: &str) -> bool {
    SUPPORTED.contains(&version)
}

pub fn supported_protocol_versions() -> &'static [&'static str] {
    &SUPPORTED
}

pub fn dispatch(message: &Value) -> Outcome {
    if let Err(message) = validate_envelope(message) {
        return Outcome::Response(error_response(Value::Null, INVALID_REQUEST, message));
    }

    let method = message["method"]
        .as_str()
        .expect("validated method must be a string");
    let params = message.get("params").cloned().unwrap_or_else(|| json!({}));
    if let Err(error_message) = validate_method_params(method, &params) {
        if message.get("id").is_none() {
            return Outcome::RejectedNotification;
        }
        return Outcome::Response(error_response(
            request_id(message),
            INVALID_PARAMS,
            error_message,
        ));
    }
    if message.get("id").is_none() {
        if method == "initialize" {
            return Outcome::RejectedNotification;
        }
        return Outcome::Notification;
    }

    let id = request_id(message);
    let response = match method {
        "initialize" => result_response(id, initialize(&params)),
        "ping" => result_response(id, json!({})),
        "tools/list" => result_response(id, json!({ "tools": tools::list() })),
        "tools/call" => {
            let Some(name) = params.get("name").and_then(Value::as_str) else {
                return Outcome::Response(error_response(id, INVALID_PARAMS, "missing tool name"));
            };
            let arguments = params
                .get("arguments")
                .cloned()
                .unwrap_or_else(|| json!({}));
            match tools::call(name, &arguments) {
                Ok(text) => result_response(id, text_content(&text, false)),
                Err(message) if message.starts_with("unknown tool") => {
                    error_response(id, INVALID_PARAMS, &message)
                }
                Err(message) => result_response(id, text_content(&message, true)),
            }
        }
        "resources/list" => result_response(id, json!({ "resources": resources() })),
        "resources/read" => {
            let Some(uri) = params.get("uri").and_then(Value::as_str) else {
                return Outcome::Response(error_response(id, INVALID_PARAMS, "missing uri"));
            };
            match read_resource(uri) {
                Some(text) => result_response(
                    id,
                    json!({ "contents": [{
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": text,
                    }]}),
                ),
                None => error_response(id, INVALID_PARAMS, &format!("no resource at `{uri}`")),
            }
        }
        "prompts/list" => result_response(id, json!({ "prompts": [] })),
        "resources/templates/list" => result_response(id, json!({ "resourceTemplates": [] })),
        other => error_response(id, METHOD_NOT_FOUND, &format!("unknown method `{other}`")),
    };

    Outcome::Response(response)
}

fn validate_method_params(method: &str, params: &Value) -> Result<(), &'static str> {
    if !params.is_object() {
        return Err("MCP method parameters must use named object form");
    }
    if method != "initialize" {
        return Ok(());
    }
    if !params.get("protocolVersion").is_some_and(Value::is_string) {
        return Err("initialize requires string `protocolVersion`");
    }
    if !params.get("capabilities").is_some_and(Value::is_object) {
        return Err("initialize requires object `capabilities`");
    }
    let Some(client_info) = params.get("clientInfo").and_then(Value::as_object) else {
        return Err("initialize requires object `clientInfo`");
    };
    if !client_info.get("name").is_some_and(Value::is_string) {
        return Err("initialize requires string `clientInfo.name`");
    }
    if !client_info.get("version").is_some_and(Value::is_string) {
        return Err("initialize requires string `clientInfo.version`");
    }
    Ok(())
}

fn initialize(params: &Value) -> Value {
    let requested = params
        .get("protocolVersion")
        .and_then(Value::as_str)
        .expect("initialize params were validated");
    let negotiated = if supports_protocol_version(requested) {
        requested
    } else {
        PROTOCOL_VERSION
    };

    json!({
        "protocolVersion": negotiated,
        "capabilities": {
            "tools": { "listChanged": false },
            "resources": {},
        },
        "serverInfo": {
            "name": "surf",
            "title": "Surf, with Native AI",
            "version": env!("CARGO_PKG_VERSION"),
        },
        "instructions": format!(
            "A public, stateless briefing server for Surf's working pre-production framework. \
             Call `quickstart` once when entering a Surf conversation, then use `get_guide` \
             for the primary moment and `get_reference` whenever cross-cutting knowledge is \
             relevant. `get_doc` explains Surf itself. The application receives no local \
             participant practice content and retains no participant state. Surf application version: {}. \
             Working framework version: {}. {}",
            env!("CARGO_PKG_VERSION"),
            framework::WORKING_VERSION,
            source::instruction(),
        ),
    })
}

fn text_content(text: &str, is_error: bool) -> Value {
    json!({
        "content": [{ "type": "text", "text": text }],
        "isError": is_error,
    })
}

fn resources() -> Value {
    let mut resources = vec![
        json!({
            "uri": "surf://framework/quickstart",
            "name": "Surf quickstart",
            "description": "Resident orientation, product spine, boundaries, and routing for the working framework.",
            "mimeType": "text/markdown",
        }),
        json!({
            "uri": "surf://framework/manifest",
            "name": "Surf working framework manifest",
            "description": "The current quickstart, moment-guide, and reference catalogue.",
            "mimeType": "text/markdown",
        }),
    ];
    resources.extend(framework::GUIDES.iter().map(|guide| {
        json!({
            "uri": format!("surf://guide/{}", guide.slug),
            "name": guide.title,
            "description": guide.description,
            "mimeType": "text/markdown",
        })
    }));
    resources.extend(framework::REFERENCES.iter().map(|reference| {
        json!({
            "uri": format!("surf://reference/{}", reference.slug),
            "name": reference.title,
            "description": reference.description,
            "mimeType": "text/markdown",
        })
    }));
    resources.push(json!({
        "uri": "surf://changelog",
        "name": "Working framework changelog",
        "description": "Useful development landmarks for Surf's pre-production framework.",
        "mimeType": "text/markdown",
    }));
    resources.extend(docs::all().iter().map(|doc| {
        json!({
            "uri": format!("surf://docs/{}", doc.slug),
            "name": doc.title,
            "description": doc.description,
            "mimeType": "text/markdown",
        })
    }));
    resources.push(json!({
        "uri": "surf://source",
        "name": "Source for this running version",
        "description": "Surf application version, working framework version, and verified public source revision, or a visible unavailable result.",
        "mimeType": "text/markdown",
    }));
    Value::Array(resources)
}

fn read_resource(uri: &str) -> Option<String> {
    match uri {
        "surf://framework/quickstart" => Some(framework::QUICKSTART.to_string()),
        "surf://framework/manifest" => Some(framework::manifest()),
        "surf://changelog" => Some(framework::CHANGELOG.to_string()),
        "surf://source" => Some(source::markdown()),
        _ => uri
            .strip_prefix("surf://guide/")
            .and_then(framework::guide)
            .map(|document| document.text.to_string())
            .or_else(|| {
                uri.strip_prefix("surf://reference/")
                    .and_then(framework::reference)
                    .map(|document| document.text.to_string())
            })
            .or_else(|| {
                uri.strip_prefix("surf://docs/")
                    .and_then(docs::find)
                    .map(|doc| doc.markdown.to_string())
            }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn request(method: &str, params: Value) -> Value {
        match dispatch(&json!({
            "jsonrpc": "2.0", "id": 1, "method": method, "params": params
        })) {
            Outcome::Response(body) => body,
            Outcome::Notification => panic!("{method} answered as a notification"),
            Outcome::RejectedNotification => panic!("{method} rejected as a notification"),
        }
    }

    fn initialize_params(version: &str) -> Value {
        json!({
            "protocolVersion": version,
            "capabilities": {},
            "clientInfo": { "name": "test-client", "version": "1.0.0" }
        })
    }

    #[test]
    fn initialization_names_the_working_surface_and_stateless_boundary() {
        let response = request("initialize", initialize_params("2025-06-18"));
        let instructions = response["result"]["instructions"].as_str().unwrap();
        for required in [
            "quickstart",
            "get_guide",
            "get_reference",
            "get_doc",
            "0.1.0",
        ] {
            assert!(instructions.contains(required), "{required}");
        }
        assert!(instructions.contains("retains no participant state"));
        assert!(instructions.contains("Surf application version: 0.1.0"));
        assert!(instructions.contains("Working framework version: 0.1.0"));
        assert_eq!(response["result"]["serverInfo"]["name"], "surf");
        assert_eq!(response["result"]["serverInfo"]["version"], "0.1.0");
    }

    #[test]
    fn tools_round_trip_through_json_rpc() {
        let listed = request("tools/list", json!({}));
        let names = listed["result"]["tools"]
            .as_array()
            .unwrap()
            .iter()
            .map(|tool| tool["name"].as_str().unwrap())
            .collect::<Vec<_>>();
        assert_eq!(
            names,
            ["quickstart", "get_guide", "get_reference", "get_doc"]
        );
        for (name, arguments) in [
            ("quickstart", json!({})),
            ("get_guide", json!({ "guide": "setting-up" })),
            ("get_reference", json!({ "reference": "capabilities" })),
            ("get_doc", json!({ "topic": "index" })),
        ] {
            let response = request(
                "tools/call",
                json!({ "name": name, "arguments": arguments }),
            );
            assert_eq!(response["result"]["isError"], false, "{name}");
            assert!(!response["result"]["content"][0]["text"]
                .as_str()
                .unwrap()
                .is_empty());
        }
    }

    #[test]
    fn resources_mirror_every_kind_and_all_are_readable() {
        let listed = request("resources/list", json!({}));
        let uris = listed["result"]["resources"]
            .as_array()
            .unwrap()
            .iter()
            .map(|resource| resource["uri"].as_str().unwrap().to_string())
            .collect::<Vec<_>>();
        assert!(uris.contains(&"surf://framework/quickstart".to_string()));
        assert!(uris.contains(&"surf://guide/setting-up".to_string()));
        assert!(uris.contains(&"surf://reference/shared-map-of-development".to_string()));
        assert!(!uris.iter().any(|uri| uri.starts_with("surf://releases/")));
        for uri in uris {
            let response = request("resources/read", json!({ "uri": uri }));
            assert!(response.get("error").is_none(), "{response}");
        }

        for doc in docs::all() {
            let uri = format!("surf://docs/{}", doc.slug);
            let resource = request("resources/read", json!({ "uri": uri }));
            assert_eq!(
                resource["result"]["contents"][0]["text"], doc.markdown,
                "{}",
                doc.slug
            );

            let tool = request(
                "tools/call",
                json!({ "name": "get_doc", "arguments": { "topic": doc.slug } }),
            );
            assert_eq!(
                tool["result"]["content"][0]["text"], doc.markdown,
                "{}",
                doc.slug
            );
        }
    }

    #[test]
    fn malformed_requests_and_unknown_resources_fail_cleanly() {
        assert!(validate_envelope(&json!([])).is_err());
        let response = request(
            "resources/read",
            json!({ "uri": "surf://reference/missing" }),
        );
        assert_eq!(response["error"]["code"], INVALID_PARAMS);
        let response = request("missing", json!({}));
        assert_eq!(response["error"]["code"], METHOD_NOT_FOUND);
    }
}
