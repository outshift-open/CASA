//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <logger/bpf_dbg.h>

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 1);
} pkt_count SEC(".maps");

SEC("xdp")
int count_packets() {
    __u32 key = 0;
    __u64 *count = bpf_map_lookup_elem(&pkt_count, &key);
    if (count) {
        __sync_fetch_and_add(count, 1);
    }

    bpf_dbg_printk("=== xdp called ===");

    return XDP_PASS;
}

char __license[] SEC("license") = "Dual MIT/GPL";
