use std::collections::HashMap;
use std::time::Duration;

use log::error;
use log::info;
use proxy_wasm::traits::*;
use proxy_wasm::types::*;
use serde_json::json;

const LITELLM_CALL_ID_HEADER: &str = "x-litellm-call-id";

proxy_wasm::main! {{
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_root_context(|_| -> Box<dyn RootContext> { Box::new(HttpHeadersRoot) });
}}

struct HttpHeadersRoot;

impl Context for HttpHeadersRoot {}

impl RootContext for HttpHeadersRoot {
    fn get_type(&self) -> Option<ContextType> {
        Some(ContextType::HttpContext)
    }

    fn create_http_context(&self, context_id: u32) -> Option<Box<dyn HttpContext>> {
        let auth_srv_host =
            std::env::var("AUTH_SERVER_HOST").unwrap_or_else(|_| "localhost".to_string());
        let auth_srv_port = std::env::var("AUTH_SERVER_PORT")
            .ok()
            .and_then(|v| v.parse::<u16>().ok())
            .unwrap_or(8000);

        Some(Box::new(LlmCall {
            context_id: context_id,
            litellm_call_id: None,
            pending: HashMap::new(),
            auth_server_host: auth_srv_host,
            auth_server_port: auth_srv_port,
        }))
    }
}

enum PendingAuthSrvCall {
    StoreLlmCallEndEvent,
}

struct LlmCall {
    context_id: u32,
    litellm_call_id: Option<String>,
    pending: HashMap<u32, PendingAuthSrvCall>,
    auth_server_host: String,
    auth_server_port: u16,
}

impl Context for LlmCall {
    fn on_http_call_response(&mut self, token_id: u32, _: usize, _: usize, _: usize) {
        let call = self.pending.remove(&token_id);

        let status_code = self
            .get_http_call_response_headers()
            .iter()
            .find(|(k, _)| k == ":status")
            .and_then(|(_, v)| v.parse::<u16>().ok())
            .unwrap_or(0);
        if status_code != 200 {
            self.resume_http_response();
            return;
        }

        match call {
            Some(PendingAuthSrvCall::StoreLlmCallEndEvent) => {
                info!("LlmCallEndEvent stored");
                self.resume_http_response();
            }
            None => {
                self.resume_http_response();
            }
        }
    }
}

impl HttpContext for LlmCall {
    fn on_http_response_headers(&mut self, _: usize, _: bool) -> Action {
        let maybe_call_id = self.get_http_response_header(LITELLM_CALL_ID_HEADER);
        if let Some(call_id) = maybe_call_id {
            self.litellm_call_id = Some(call_id.clone());
        }

        Action::Continue
    }

    fn on_http_response_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        if self.litellm_call_id.is_none() {
            return Action::Continue;
        }

        if !end_of_stream {
            // Wait -- we'll be called again when the complete body is buffered
            // at the host side.
            return Action::Pause;
        }

        if let Some(body_bytes) = self.get_http_response_body(0, body_size) {
            let body_str = String::from_utf8(body_bytes).unwrap();
            info!("LITELLM response body = {}", body_str);

            let trace_body = json!({
                "call_id": self.litellm_call_id.as_deref().unwrap(),
                "response": body_str,
            });

            match serde_json::to_vec(&trace_body) {
                Ok(payload) => {
                    info!("sending event payload = {}", trace_body);

                    let ret_token = self
                        .dispatch_http_call(
                            format!("outbound|{}||{}", self.auth_server_port, self.auth_server_host).as_str(),
                            vec![
                                (":method", "POST"),
                                (":path", "/k8s/trace/llm/call_end"),
                                (":authority", format!("{}:{}", self.auth_server_host, self.auth_server_port).as_str()),
                                ("content-type", "application/json"),
                            ],
                            Some(&payload),
                            vec![],
                            Duration::from_secs(300),
                        )
                        .unwrap();

                    self.pending
                        .insert(ret_token, PendingAuthSrvCall::StoreLlmCallEndEvent);

                    return Action::Pause;
                }
                Err(err) => {
                    error!("error serializing trace_body to json {}", err);
                }
            }
        }

        Action::Continue
    }

    fn on_log(&mut self) {
        info!("#{} completed.", self.context_id);
    }
}
