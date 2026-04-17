use cfg_if::cfg_if;
use log::info;
use proxy_wasm::traits::*;
use proxy_wasm::types::*;
use uuid::Uuid;

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
        Some(Box::new(LlmCall { context_id: context_id, litellm_call_id: None }))
    }
}

struct LlmCall {
    context_id: u32,
    litellm_call_id: Option<String>,
}

impl Context for LlmCall {}

impl HttpContext for LlmCall {
    fn on_http_request_headers(&mut self, _: usize, _: bool) -> Action {
        // let existing = self.get_http_request_header(LITELLM_CALL_ID_HEADER);
        // if existing.is_none() {
        //     match generate_uuid() {
        //         Some(id) => {
        //             self.add_http_request_header(LITELLM_CALL_ID_HEADER, &id);
        //             self.litellm_call_id = Some(id);
        //         }
        //         None => info!("Could not generate a {} value", LITELLM_CALL_ID_HEADER)
        //     }
        // }

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _: usize, _: bool) -> Action {
        let maybe_call_id = self.get_http_response_header(LITELLM_CALL_ID_HEADER);
        if let Some(call_id) = maybe_call_id {
            info!("{} = {}", LITELLM_CALL_ID_HEADER, call_id);
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
        }

        Action::Continue
    }

    fn on_log(&mut self) {
        info!("#{} completed.", self.context_id);
    }
}

fn generate_uuid() -> Option<String> {
    cfg_if! {
        if #[cfg(all(target_arch = "wasm32", target_os = "unknown"))] {
            info!("wasm32_unknow doesn't support getrandom");
            return None;
        } else {
            let id = Uuid::new_v4();
            Some(id.to_string())
        }
    }
}
