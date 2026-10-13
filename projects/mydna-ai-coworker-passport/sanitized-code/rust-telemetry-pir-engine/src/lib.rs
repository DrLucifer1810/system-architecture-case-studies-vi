//! # Sanitized Reference Implementation: Telemetry PIR Scrubber & Lineage Engine
//! Demonstrates zero-leakage regex sanitization and 64-bit clipboard lineage hashing.

use regex::Regex;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::OnceLock;

// Compile regexes strictly once (Singleton pattern) for high throughput
static EMAIL_REGEX: OnceLock<Regex> = OnceLock::new();
static API_KEY_REGEX: OnceLock<Regex> = OnceLock::new();
static BEARER_TOKEN_REGEX: OnceLock<Regex> = OnceLock::new();
static CREDIT_CARD_REGEX: OnceLock<Regex> = OnceLock::new();

/// Scrubs credentials, authorization headers, emails, and PCI data before model ingestion.
pub fn redact_sensitive_data(input: &str) -> String {
    let email_re = EMAIL_REGEX.get_or_init(|| {
        Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap()
    });

    let api_key_re = API_KEY_REGEX.get_or_init(|| {
        Regex::new(r"(?i)(sk-[a-zA-Z0-9]{32,}|AIza[0-9A-Za-z-_]{35}|gh[pousr]_[A-Za-z0-9_]{36,})").unwrap()
    });

    let bearer_re = BEARER_TOKEN_REGEX.get_or_init(|| {
        Regex::new(r"(?i)Bearer\s+[A-Za-z0-9\-\._~\+/]+=*").unwrap()
    });

    let cc_re = CREDIT_CARD_REGEX.get_or_init(|| {
        Regex::new(r"\b(?:\d[ -]*?){13,16}\b").unwrap()
    });

    let mut redacted = input.to_string();
    redacted = email_re.replace_all(&redacted, "[REDACTED_EMAIL]").to_string();
    redacted = api_key_re.replace_all(&redacted, "[REDACTED_API_KEY]").to_string();
    redacted = bearer_re.replace_all(&redacted, "[REDACTED_BEARER_TOKEN]").to_string();
    redacted = cc_re.replace_all(&redacted, "[REDACTED_CREDIT_CARD]").to_string();

    redacted
}

/// Generates a fast 64-bit hexadecimal lineage identifier for clipboard content.
/// Enables cross-application tracking without storing the plaintext string in memory.
pub fn generate_lineage_id(content: &str) -> String {
    let mut hasher = DefaultHasher::new();
    content.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActiveWindowSample {
    pub title: String,
    pub process_id: u32,
    pub is_ai_surface: bool,
}

impl ActiveWindowSample {
    pub fn new(title: String, process_id: u32) -> Self {
        let lower = title.to_lowercase();
        let is_ai_surface = lower.contains("chatgpt")
            || lower.contains("gemini")
            || lower.contains("claude")
            || lower.contains("cursor");
        Self {
            title,
            process_id,
            is_ai_surface,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pir_redaction() {
        let dirty_prompt = "Dev Alice alice@corp.com with key sk-1234567890abcdef1234567890abcdef12 and auth Bearer eyJhbGciOiJIUzI1NiJ9.test";
        let sanitized = redact_sensitive_data(dirty_prompt);

        assert!(!sanitized.contains("alice@corp.com"));
        assert!(!sanitized.contains("sk-1234567890abcdef1234567890abcdef12"));
        assert!(!sanitized.contains("eyJhbGciOiJIUzI1NiJ9"));
        assert!(sanitized.contains("[REDACTED_EMAIL]"));
        assert!(sanitized.contains("[REDACTED_API_KEY]"));
        assert!(sanitized.contains("[REDACTED_BEARER_TOKEN]"));
    }

    #[test]
    fn test_lineage_deterministic_hashing() {
        let code = "fn main() { println!(\"Hello Production\"); }";
        let id1 = generate_lineage_id(code);
        let id2 = generate_lineage_id(code);
        assert_eq!(id1, id2);
        assert_eq!(id1.len(), 16);
    }

    #[test]
    fn test_ai_surface_detection() {
        let sample = ActiveWindowSample::new("Google Gemini — Mozilla Firefox".to_string(), 4120);
        assert!(sample.is_ai_surface);

        let ide_sample = ActiveWindowSample::new("main.rs — rust-analyzer — VS Code".to_string(), 9012);
        assert!(!ide_sample.is_ai_surface);
    }
}
