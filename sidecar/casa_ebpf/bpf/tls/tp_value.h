#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

struct tp_value {
    u8 trace_id[16];
    u8 span_id[8];
};
