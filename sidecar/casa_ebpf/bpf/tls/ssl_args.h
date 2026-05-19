#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

// #define MAX_CHUNK_SIZE 8192
#define MAX_CHUNK_SIZE 1024*100

typedef struct ssl_args {
    u64 ssl;     // SSL struct pointer
    u64 buf;     // pointer to the buffer we read into
    u64 len_ptr; // size_t pointer of the read/written bytes, used only by SSL_read_ex and SSL_write_ex
    u64 flags; // flags
} ssl_args_t;

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 30000);
    __type(key, u64);
    __type(value, ssl_args_t);
} active_ssl_args SEC(".maps");

struct tls_data_event {
    u64 pid_tgid;
    u64 ssl;
    u32 len;
    u32 original_len;
    u64 done;
    char data[MAX_CHUNK_SIZE];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24); // 16MiB
    __type(value, struct tls_data_event);
} tls_events SEC(".maps");
