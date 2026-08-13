// Copyright © 2026 AI Native Work, Inc.
// SPDX-License-Identifier: AGPL-3.0-or-later

//! The public read-only tool surface over Surf's working framework and docs.

use serde_json::{json, Map, Value};

use crate::{docs, framework};

pub struct Tool {
    pub name: &'static str,
    pub title: &'static str,
    pub description: &'static str,
    pub schema: fn() -> Value,
}

fn empty_schema() -> Value {
    json!({
        "type": "object",
        "properties": {},
        "additionalProperties": false
    })
}

fn document_schema(property: &str, description: &str, documents: &[framework::Document]) -> Value {
    let slugs = documents
        .iter()
        .map(|document| Value::String(document.slug.into()))
        .collect::<Vec<_>>();
    let choices = documents
        .iter()
        .map(|document| {
            json!({
                "const": document.slug,
                "title": document.title,
                "description": document.description,
            })
        })
        .collect::<Vec<_>>();
    json!({
        "type": "object",
        "properties": {
            property: {
                "type": "string",
                "description": description,
                "enum": slugs,
                "oneOf": choices,
            }
        },
        "required": [property],
        "additionalProperties": false
    })
}

fn guide_schema() -> Value {
    document_schema(
        "guide",
        "The moment guide matching what the person is doing now.",
        framework::GUIDES,
    )
}

fn reference_schema() -> Value {
    document_schema(
        "reference",
        "A cross-cutting reference that is relevant to the present Surf work.",
        framework::REFERENCES,
    )
}

fn doc_schema() -> Value {
    let topics = docs::all()
        .iter()
        .map(|doc| Value::String(doc.slug.into()))
        .collect::<Vec<_>>();
    let choices = docs::all()
        .iter()
        .map(|doc| {
            json!({
                "const": doc.slug,
                "title": doc.title,
                "description": doc.description,
            })
        })
        .collect::<Vec<_>>();
    json!({
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Stable slug from Surf's current product-document catalogue.",
                "enum": topics,
                "oneOf": choices,
            }
        },
        "required": ["topic"],
        "additionalProperties": false
    })
}

pub static TOOLS: &[Tool] = &[
    Tool {
        name: "quickstart",
        title: "Orient and route the Surf practice",
        description: "Call once when entering a Surf conversation. Returns bounded product documentation, the compact development model, hard boundaries, local marker routing, and the moment-guide and reference indexes. Surf reads no local practice content and stores no participant state.",
        schema: empty_schema,
    },
    Tool {
        name: "get_guide",
        title: "Read one Surf moment guide",
        description: "Fetch the primary guide for the person's present Surf moment. One guide is the focused default; use your judgement when another guide is genuinely helpful.",
        schema: guide_schema,
    },
    Tool {
        name: "get_reference",
        title: "Read one Surf reference",
        description: "Fetch cross-cutting Surf knowledge whenever it is generally relevant to good work. Begin focused and expand when useful rather than loading the catalogue by default.",
        schema: reference_schema,
    },
    Tool {
        name: "get_doc",
        title: "Read current Surf product documentation",
        description: "Fetch a document explaining Surf itself. Product documents are separate from the working framework returned by quickstart, get_guide, and get_reference.",
        schema: doc_schema,
    },
];

#[cfg(test)]
pub fn find(name: &str) -> Option<&'static Tool> {
    TOOLS.iter().find(|tool| tool.name == name)
}

pub fn list() -> Value {
    Value::Array(
        TOOLS
            .iter()
            .map(|tool| {
                json!({
                    "name": tool.name,
                    "title": tool.title,
                    "description": tool.description,
                    "inputSchema": (tool.schema)(),
                })
            })
            .collect(),
    )
}

pub fn call(name: &str, arguments: &Value) -> Result<String, String> {
    let arguments = arguments
        .as_object()
        .ok_or_else(|| "tool arguments must be an object".to_string())?;

    match name {
        "quickstart" => {
            validate_keys(arguments, &[])?;
            Ok(framework::QUICKSTART.to_string())
        }
        "get_guide" => {
            validate_keys(arguments, &["guide"])?;
            let slug = required_string(arguments, "guide")?;
            framework::guide(slug)
                .map(|document| document.text.to_string())
                .ok_or_else(|| unknown("guide", slug, framework::GUIDES))
        }
        "get_reference" => {
            validate_keys(arguments, &["reference"])?;
            let slug = required_string(arguments, "reference")?;
            framework::reference(slug)
                .map(|document| document.text.to_string())
                .ok_or_else(|| unknown("reference", slug, framework::REFERENCES))
        }
        "get_doc" => {
            validate_keys(arguments, &["topic"])?;
            let topic = required_string(arguments, "topic")?;
            docs::find(topic)
                .map(|doc| doc.markdown.to_string())
                .ok_or_else(|| {
                    format!(
                        "unknown product document `{topic}`; available: {}",
                        docs::all()
                            .iter()
                            .map(|doc| doc.slug)
                            .collect::<Vec<_>>()
                            .join(", ")
                    )
                })
        }
        _ => Err(format!("unknown tool `{name}`")),
    }
}

fn unknown(kind: &str, slug: &str, documents: &[framework::Document]) -> String {
    format!(
        "unknown {kind} `{slug}`; available: {}",
        documents
            .iter()
            .map(|document| document.slug)
            .collect::<Vec<_>>()
            .join(", ")
    )
}

fn validate_keys(arguments: &Map<String, Value>, allowed: &[&str]) -> Result<(), String> {
    if let Some(key) = arguments
        .keys()
        .find(|key| !allowed.contains(&key.as_str()))
    {
        return Err(format!("unsupported argument `{key}`"));
    }
    Ok(())
}

fn required_string<'a>(arguments: &'a Map<String, Value>, key: &str) -> Result<&'a str, String> {
    arguments
        .get(key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| format!("`{key}` is required and must be a non-empty string"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn public_surface_has_four_clear_read_tools() {
        assert_eq!(
            TOOLS.iter().map(|tool| tool.name).collect::<Vec<_>>(),
            ["quickstart", "get_guide", "get_reference", "get_doc"]
        );
        assert_eq!(
            (find("quickstart").unwrap().schema)()["required"],
            Value::Null
        );
        assert_eq!(
            (find("get_guide").unwrap().schema)()["required"],
            json!(["guide"])
        );
        assert_eq!(
            (find("get_reference").unwrap().schema)()["required"],
            json!(["reference"])
        );
    }

    #[test]
    fn schemas_expose_the_complete_kind_specific_catalogues() {
        let guides = (find("get_guide").unwrap().schema)();
        let references = (find("get_reference").unwrap().schema)();
        assert_eq!(
            guides["properties"]["guide"]["enum"],
            json!([
                "setting-up",
                "returning-and-capture",
                "evidence-review",
                "intensive-foundation",
                "teaching-and-practice"
            ])
        );
        assert_eq!(
            references["properties"]["reference"]["enum"],
            json!([
                "shared-map-of-development",
                "context-and-local-practice",
                "capabilities",
                "supporting-literacies",
                "builds"
            ])
        );
    }

    #[test]
    fn every_framework_document_round_trips_through_its_tool() {
        assert_eq!(
            call("quickstart", &json!({})).unwrap(),
            framework::QUICKSTART
        );
        for guide in framework::GUIDES {
            assert_eq!(
                call("get_guide", &json!({ "guide": guide.slug })).unwrap(),
                guide.text
            );
        }
        for reference in framework::REFERENCES {
            assert_eq!(
                call("get_reference", &json!({ "reference": reference.slug })).unwrap(),
                reference.text
            );
        }
    }

    #[test]
    fn invalid_arguments_fail_closed_and_name_available_choices() {
        assert!(call("quickstart", &json!({ "version": "0.1.0" })).is_err());
        assert!(call("get_guide", &json!({})).is_err());
        assert!(call("get_reference", &json!({ "reference": "missing" }))
            .unwrap_err()
            .contains("shared-map-of-development"));
        assert!(call("missing", &json!({})).is_err());
    }
}
