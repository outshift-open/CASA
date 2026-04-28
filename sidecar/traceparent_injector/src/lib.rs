// Copyright 2026 Cisco Systems, Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use cfg_if::cfg_if;
use log::info;
use proxy_wasm::traits::*;
use proxy_wasm::types::*;

const TRACE_PARENT_HEADER: &str = "traceparent";

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
        Some(Box::new(HttpHeaders { context_id }))
    }
}

struct HttpHeaders {
    context_id: u32,
}

impl Context for HttpHeaders {}

impl HttpContext for HttpHeaders {
    fn on_http_request_headers(&mut self, _: usize, _: bool) -> Action {
        let existing = self.get_http_request_header(TRACE_PARENT_HEADER);
        if existing.is_none() {
            match generate_traceparent() {
                Some(tp) => self.add_http_request_header(TRACE_PARENT_HEADER, &tp),
                None => info!("Could not generate a traceparent value")
            }
        }

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _: usize, _: bool) -> Action {
        Action::Continue
    }

    fn on_log(&mut self) {
        info!("#{} completed.", self.context_id);
    }
}

fn generate_traceparent() -> Option<String> {
    cfg_if! {
        if #[cfg(all(target_arch = "wasm32", target_os = "unknown"))] {
            info!("wasm32_unknow doesn't support getrandom");
            return None;
        } else {
            let trace_id: String;
            let span_id: String;

            match get_random_bytes(16) {
                Ok(bytes) => {
                    trace_id = hex::encode(&bytes);
                }
                Err(e) => {
                    info!("Error generating trace_id: {}", e);
                    return None;
                }
            }

            match get_random_bytes(8) {
                Ok(bytes) => {
                    span_id = hex::encode(&bytes);
                }
                Err(e) => {
                    info!("Error generating span_id: {}", e);
                    return None;
                }
            }

            Some(format!("00-{trace_id}-{span_id}-01"))
        }
    }
}

fn get_random_bytes(size: usize) -> Result<Vec<u8>, getrandom::Error> {
    let mut buf = vec![0u8; size];
    getrandom::fill(&mut buf)?;
    Ok(buf)
}
