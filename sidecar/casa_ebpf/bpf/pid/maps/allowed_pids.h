#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <pid/maps/size.h>

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, k_max_concurrent_pids);
    __type(key, __u32);
    __type(value, __u64);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} allowed_pids SEC(".maps");
