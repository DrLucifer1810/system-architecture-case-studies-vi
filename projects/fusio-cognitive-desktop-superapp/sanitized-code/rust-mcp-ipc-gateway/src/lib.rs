//! # Rust MCP & IPC Gateway Reference Implementation
//!
//! Demonstrates zero-copy IPC message routing and Model Context Protocol (MCP)
//! tool virtualization between native host desktop runtimes and external AI engines.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use thiserror::Error;
use tokio::sync::RwLock;

#[derive(Error, Debug)]
pub enum McpError {
    #[error("Tool not found: {0}")]
    ToolNotFound(String),
    #[error("Serialization failure: {0}")]
    SerializationError(#[from] serde_json::Error),
    #[error("Execution failure: {0}")]
    ExecutionError(String),
}

/// Structured IPC Frame exchanged between Tauri host and Python Brain
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct IpcMessage {
    pub id: String,
    pub session_id: String,
    pub method: String,
    pub params: serde_json::Value,
}

/// Standardized MCP Tool Definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpTool {
    pub name: String,
    pub description: String,
    pub input_schema: serde_json::Value,
}

/// Async tool handler function signature
pub type ToolHandler = Arc<
    dyn Fn(serde_json::Value) -> Result<serde_json::Value, McpError> + Send + Sync,
>;

/// Central MCP Gateway and Tool Registry
#[derive(Clone, Default)]
pub struct McpGateway {
    tools: Arc<RwLock<HashMap<String, (McpTool, ToolHandler)>>>,
}

impl McpGateway {
    pub fn new() -> Self {
        Self {
            tools: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Registers an MCP tool endpoint with its validation schema and handler
    pub async fn register_tool(
        &self,
        tool: McpTool,
        handler: ToolHandler,
    ) {
        let mut registry = self.tools.write().await;
        registry.insert(tool.name.clone(), (tool, handler));
    }

    /// Lists all currently registered MCP tools
    pub async fn list_tools(&self) -> Vec<McpTool> {
        let registry = self.tools.read().await;
        registry.values().map(|(t, _)| t.clone()).collect()
    }

    /// Dispatches an incoming tool call from an IPC frame
    pub async fn call_tool(
        &self,
        tool_name: &str,
        arguments: serde_json::Value,
    ) -> Result<serde_json::Value, McpError> {
        let registry = self.tools.read().await;
        let (_, handler) = registry
            .get(tool_name)
            .ok_or_else(|| McpError::ToolNotFound(tool_name.to_string()))?;

        handler(arguments)
    }

    /// Processes an IPC message envelope and generates a response frame
    pub async fn handle_ipc_message(&self, message: IpcMessage) -> Result<IpcMessage, McpError> {
        match message.method.as_str() {
            "mcp.list_tools" => {
                let tool_list = self.list_tools().await;
                Ok(IpcMessage {
                    id: message.id,
                    session_id: message.session_id,
                    method: "mcp.list_tools_response".to_string(),
                    params: serde_json::to_value(tool_list)?,
                })
            }
            "mcp.call_tool" => {
                let tool_name = message.params["name"]
                    .as_str()
                    .ok_or_else(|| McpError::ExecutionError("Missing tool name".to_string()))?;
                let args = message.params["arguments"].clone();
                let output = self.call_tool(tool_name, args).await?;

                Ok(IpcMessage {
                    id: message.id,
                    session_id: message.session_id,
                    method: "mcp.call_tool_response".to_string(),
                    params: output,
                })
            }
            other => Err(McpError::ExecutionError(format!("Unsupported method: {}", other))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_tool_registration_and_execution() {
        let gateway = McpGateway::new();

        let tool = McpTool {
            name: "calculate_hash".to_string(),
            description: "Calculates mock hash of input".to_string(),
            input_schema: serde_json::json!({ "type": "object" }),
        };

        let handler = Arc::new(|args: serde_json::Value| {
            let input = args["data"].as_str().unwrap_or("");
            Ok(serde_json::json!({ "hash": format!("hash_{}", input) }))
        });

        gateway.register_tool(tool, handler).await;

        let result = gateway
            .call_tool("calculate_hash", serde_json::json!({ "data": "test_payload" }))
            .await
            .unwrap();

        assert_eq!(result["hash"], "hash_test_payload");
    }

    #[tokio::test]
    async fn test_ipc_envelope_routing() {
        let gateway = McpGateway::new();

        let req = IpcMessage {
            id: "msg_101".to_string(),
            session_id: "sess_alpha".to_string(),
            method: "mcp.list_tools".to_string(),
            params: serde_json::json!({}),
        };

        let resp = gateway.handle_ipc_message(req).await.unwrap();
        assert_eq!(resp.id, "msg_101");
        assert_eq!(resp.method, "mcp.list_tools_response");
    }
}