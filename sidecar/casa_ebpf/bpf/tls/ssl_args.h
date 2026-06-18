#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <common/connection_info.h>

#include <tls/tp_value.h>

#define MAX_CHUNK_SIZE 1024*100
#define MAX_ACTIVE_REQUESTS 30000

#define FLAG_CONNECTED 0x01

typedef struct ssl_args {
    u64 ssl;     // a pointer to SSL struct
    u64 buf;     // a pointer to the HTTP payload buffer
    u64 len_ptr; // size_t pointer of the read/written bytes, used only by SSL_read_ex and SSL_write_ex
    u64 flags;   // useful to know whether the SSL connection is mapped with a sock
} ssl_args_t;

static __always_inline u8 ssl_args_connected(ssl_args_t *args) {
    return args->flags & FLAG_CONNECTED;
}

static __always_inline void set_ssl_args_connected(ssl_args_t *args) {
    args->flags |= FLAG_CONNECTED;
}

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

enum event_type {
  EVENT_DATA,
  EVENT_TP,
};

struct tls_data_event {
    u64 pid_tgid;
    u64 ssl;
    u32 len;
    u32 original_len;
    u64 done;
    u64 direction;
    u64 type;
    connection_info_t conn;
    char data[MAX_CHUNK_SIZE];
    struct tp_value tp;
    u8 _pad[4];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24); // 16MiB
    __type(value, struct tls_data_event);
} tls_events SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, pid_connection_info_t); // connection that's SSL
    __type(value, u64);                 // ssl
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} active_ssl_connections SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u64);                         // the SSL struct pointer
    __type(value, ssl_pid_connection_info_t); // the pointer to the file descriptor matching ssl
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} ssl_to_conn SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u64);   // the ssl pointer
    __type(value, u64); // the pid tid of the thread in ssl read
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
} ssl_to_pid_tid SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __type(key, u64);                         // the pid-tid pair
    __type(value, ssl_pid_connection_info_t); // the pointer to the file descriptor matching ssl
    __uint(max_entries, MAX_ACTIVE_REQUESTS);
} pid_tid_to_conn SEC(".maps");
