use std::collections::HashMap;
use std::time::Duration;

use log::error;
// use log::info;
use log::warn;
use proxy_wasm::traits::*;
use proxy_wasm::types::*;
use serde_json::Value;

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
        Some(Box::new(LlmCall {
            context_id: context_id,
            litellm_call_id: None,
            pending: HashMap::new(),
        }))
    }
}

enum PendingAuthSrvCall {
    GetLlmCallMapping,
    StoreLlmCallEndEvent,
}

struct LlmCall {
    context_id: u32,
    litellm_call_id: Option<String>,
    pending: HashMap<u32, PendingAuthSrvCall>,
}

impl Context for LlmCall {
    fn on_http_call_response(&mut self, token_id: u32, _: usize, body_size: usize, _: usize) {
        let call = self.pending.remove(&token_id);

        let status_code = self.get_http_call_response_headers()
            .iter()
            .find(|(k, _)| k == ":status")
            .and_then(|(_, v)| v.parse::<u16>().ok())
            .unwrap_or(0);
        if status_code != 200 {
            self.resume_http_response();
            return;
        }

        match call {
            Some(PendingAuthSrvCall::GetLlmCallMapping) => {
                if let Some(body) = self.get_http_call_response_body(0, body_size) {
                    match serde_json::from_slice::<Value>(&body) {
                        Ok(json) => {
                            if let Some(app_id) = json.get("app_id").and_then(|v| v.as_str()) {
                                warn!("app_id = {}", app_id);
                            } 
                            if let Some(user_input_id) = json.get("user_input_id").and_then(|v| v.as_str()) {
                                warn!("user_input_id = {}", user_input_id);
                            } 
                        }
                        Err(err) => {
                            error!("error parsing json {}", err);
                        }
                    }
                }

                self.resume_http_response();
            }
            Some(PendingAuthSrvCall::StoreLlmCallEndEvent) => {
                warn!("LlmCallEndEvent stored");
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
            warn!("{} = {}", LITELLM_CALL_ID_HEADER, call_id.clone());

            // let path = format!(
            //     "/k8s/cache/load-llm-call-mapping/{}",
            //     self.litellm_call_id.as_deref().unwrap_or("")
            // );

            // let ret_token = self
            //     .dispatch_http_call(
            //         "outbound|8000||zta-control-plane-auth-service.zta-sidecar.svc.cluster.local",
            //         vec![
            //             (":method", "GET"),
            //             (":path", &path),
            //             (":authority", "zta-control-plane-auth-service.zta-sidecar.svc.cluster.local:8000"),
            //             ("content-type", "application/json"),
            //         ],
            //         None,
            //         vec![],
            //         Duration::from_secs(5),
            //     )
            //     .unwrap();

            // self.pending.insert(ret_token, PendingAuthSrvCall::GetLlmCallMapping);

            // return Action::Pause;
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
            warn!("LITELLM response body = {}", body_str);

            let response = body_str.replace("\"", "\\\"");
            let trace_body = format!("{{\"call_id\": \"{}\", \"response\": \"{}\"}}", self.litellm_call_id.as_deref().unwrap(), response);
            warn!("sending event payload = {}", trace_body);

            let ret_token = self
                .dispatch_http_call(
                    "outbound|8000||zta-control-plane-auth-service.zta-sidecar.svc.cluster.local",
                    vec![
                        (":method", "POST"),
                        (":path", "/k8s/trace/llm/call_end"),
                        (":authority", "zta-control-plane-auth-service.zta-sidecar.svc.cluster.local:8000"),
                        ("content-type", "application/json"),
                    ],
                    Some(trace_body.as_bytes()),
                    vec![],
                    Duration::from_secs(5),
                )
                .unwrap();

            self.pending.insert(ret_token, PendingAuthSrvCall::StoreLlmCallEndEvent);

            return Action::Pause;
        }

        Action::Continue
    }

    fn on_log(&mut self) {
        warn!("#{} completed.", self.context_id);
    }
}
