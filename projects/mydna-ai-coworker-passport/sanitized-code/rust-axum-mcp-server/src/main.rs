use axum::{routing::get, Json, Router};
use serde_json::{json, Value};
use std::net::SocketAddr;
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub seniority: String,
    pub daily_focus: String,
}

#[tokio::main]
async fn main() {
    let state = Arc::new(AppState {
        seniority: "Senior Staff Rust Engineer".to_string(),
        daily_focus: "Tokio Async Pipelines & Zero-Copy Networking".to_string(),
    });

    let app = create_router(state);
    let addr = SocketAddr::from(([127, 0, 0, 1], 5050));
    println!("MCP User DNA Server running on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new().route("/mcp/resources/user_dna", get(move || get_user_dna(state.clone())))
}

async fn get_user_dna(state: Arc<AppState>) -> Json<Value> {
    let response = json!({
        "jsonrpc": "2.0",
        "result": {
            "name": "mydna_user_context",
            "description": "Comprehensive User DNA for AI Personalization",
            "content": {
                "seniority": state.seniority,
                "daily_focus": state.daily_focus,
                "coding_habits": {
                    "good": [
                        "Uses Result<T, E> and custom error enums",
                        "Applies RAII and strict borrow-checker ownership",
                        "Comprehensive unit tests on public interfaces"
                    ],
                    "bad_to_avoid": [
                        "Avoids excessive .clone() on large buffers",
                        "Rejects unwrap() in production paths"
                    ],
                    "principles": [
                        "Zero-knowledge data boundaries",
                        "Fail-fast on authorization breaches"
                    ]
                },
                "communication": {
                    "tone": ["Concise", "Technical", "Direct"],
                    "voice": ["Authoritative", "Empathetic"],
                    "quirks": ["Prefers code diffs over verbose textual explanations"]
                }
            }
        }
    });

    Json(response)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_user_dna_payload_schema() {
        let state = Arc::new(AppState {
            seniority: "Principal Distributed Architect".to_string(),
            daily_focus: "K3s Edge Clusters".to_string(),
        });

        let Json(payload) = get_user_dna(state).await;
        assert_eq!(payload["jsonrpc"], "2.0");
        assert_eq!(
            payload["result"]["content"]["seniority"],
            "Principal Distributed Architect"
        );
        let good_habits = payload["result"]["content"]["coding_habits"]["good"]
            .as_array()
            .unwrap();
        assert!(!good_habits.is_empty());
    }
}
