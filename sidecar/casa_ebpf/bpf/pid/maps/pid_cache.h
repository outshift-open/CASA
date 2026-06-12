#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <pid/maps/size.h>

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, k_max_concurrent_pids);
    __type(key, __u32);
    __type(value, __u32);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} pid_cache SEC(".maps");
