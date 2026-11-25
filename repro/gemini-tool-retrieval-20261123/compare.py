#!/usr/bin/env python3
"""Deterministic, no-network comparison of static vs deferred tool payload boundaries.
Models JSON payload shapes only; does NOT call Gemini, estimate model token costs,
or assert that a server-side tool_search enforces application authorization.
"""
from __future__ import annotations
import json

def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf8")

def build_registry(n=64):
    registry = []
    for i in range(n):
        name = ["read_docs", "search_docs", "export_document", "delete_document", "issue_refund"][i] if i < 5 else f"internal_tool_{i:03d}"
        registry.append({
            "type": "function", "name": name,
            "description": f"Specialized documented task #{i}; subject to application authorization.",
            "parameters": {
                "type": "object", "properties": {
                    "resource_id": {"type": "string", "description": "Scoped object identifier; never assume access."},
                    "options": {"type": "object", "additionalProperties": False, "properties": {
                        "format": {"type": "string", "enum": ["json", "txt"]},
                        "include_private": {"type": "boolean"}
                    }}
                }, "required": ["resource_id"]
            }
        })
    return registry

def allowlisted(registry, allowed):
    allowed = set(allowed)
    return [x for x in registry if x["name"] in allowed]

def retrieval_search(registry, allowed, term):
    return [x for x in registry if x["name"] in set(allowed) and term.lower() in x["name"].lower()]

def redacted_headers(registry):
    return [{"type": x["type"], "name": x["name"],
             "description": x["description"], "defer_loading": True} for x in registry]

def measure():
    tools = build_registry()
    permitted = ["read_docs", "search_docs", "export_document"]
    static = [{"type": "function", "name": t["name"], "description": t["description"],
               "parameters": t["parameters"]} for t in tools]
    server_deferred = [{"type": "tool_search"}] + redacted_headers(tools)
    client_deferred = [{"type": "tool_search", "execution": "client",
                        "name": "search_tools", "description": "Search authorized tool schemas only."}]
    returned_allowed = retrieval_search(tools, permitted, "docs")
    denied_search = retrieval_search(tools, permitted, "delete")
    return {
        "mode": "synthetic_static_json_shapes_no_api",
        "declared_tool_count": len(tools),
        "authorized_tool_count": len(permitted),
        "requested_search": "docs",
        "sizes_bytes_not_model_tokens": {
            "static_full_schema_payload": len(canon(static)),
            "server_deferred_initial_payload": len(canon(server_deferred)),
            "server_deferred_one_selected_full_schema": len(canon(server_deferred)) + len(canon(tools[0])),
            "client_search_initial_payload": len(canon(client_deferred)),
            "client_search_result_allowed_schemas": len(canon(returned_allowed))
        },
        "security_contract": {
            "server_deferred_headers_contain_unpermitted_names": any(
                x.get("name") == "issue_refund" for x in server_deferred),
            "client_discovery_denied_name_not_returned": not denied_search,
            "execution_requires_independent_backend_authorization": True
        },
        "api_calls": 0, "model_token_usage": None, "network_latency_ms": None,
        "provider_cost_usd": None, "model_tool_selection_accuracy": None,
        "caveat": "JSON UTF-8 size is not token count; server deferred behavior is documented, not remotely tested."
    }

if __name__ == "__main__":
    print(json.dumps(measure(), ensure_ascii=False, indent=2))

