#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#define MAX_CHUNK_SIZE 1024*100
#define MAX_ACTIVE_REQUESTS 30000

typedef struct ssl_args {
    u64 ssl;     // a pointer to SSL struct
    u64 buf;     // a pointer to the HTTP payload buffer
    u64 len_ptr; // size_t pointer of the read/written bytes, used only by SSL_read_ex and SSL_write_ex
} ssl_args_t;

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
    __type(key, u64);
    __type(value, ssl_args_t);
} active_ssl_read_args SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
    __type(key, u64);
    __type(value, ssl_args_t);
} active_ssl_write_args SEC(".maps");

struct tls_data_event {
    u64 pid_tgid;
    u64 ssl;
    u32 len;
    u32 original_len;
    u64 done;
    u64 direction;
    char data[MAX_CHUNK_SIZE];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24); // 16MiB
    __type(value, struct tls_data_event);
} tls_events SEC(".maps");
