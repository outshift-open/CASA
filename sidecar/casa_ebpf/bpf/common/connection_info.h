#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <common/protocol_defs.h>

#include <logger/bpf_dbg.h>

#define IP_V6_ADDR_LEN 16
#define IP_V6_ADDR_LEN_WORDS 4

// Struct to keep information on the connections in flight
// s = source, d = destination
// h = high word, l = low word
// used as hashmap key, must be 4 byte aligned?
typedef struct connection_info {
    union {
        u8 s_addr[IP_V6_ADDR_LEN];
        u32 s_ip[IP_V6_ADDR_LEN_WORDS];
    };
    union {
        u8 d_addr[IP_V6_ADDR_LEN];
        u32 d_ip[IP_V6_ADDR_LEN_WORDS];
    };
    u16 s_port;
    u16 d_port;
} connection_info_t;

typedef struct http_pid_connection_info {
    connection_info_t conn;
    u32 pid;
} pid_connection_info_t;

typedef struct ssl_pid_connection_info {
    pid_connection_info_t p_conn;
    u16 orig_dport;
    u8 _pad[6];
} ssl_pid_connection_info_t;

const u8 ip4ip6_prefix[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xff, 0xff};

static __always_inline bool likely_ephemeral_port(u16 port) {
    return port >= EPHEMERAL_PORT_MIN;
}

#define __SWAP(T, x, y)                                                                            \
    {                                                                                              \
        T TMP = x;                                                                                 \
        x = y;                                                                                     \
        y = TMP;                                                                                   \
    }

static __always_inline void swap_connection_info_order(connection_info_t *info) {
    __SWAP(u16, info->s_port, info->d_port);
    u8 tmp_addr[IP_V6_ADDR_LEN];
    __builtin_memcpy(tmp_addr, info->s_addr, sizeof(tmp_addr));
    __builtin_memcpy(info->s_addr, info->d_addr, sizeof(info->s_addr));
    __builtin_memcpy(info->d_addr, tmp_addr, sizeof(info->d_addr));
}

// Since we track both send and receive connections, we need to sort the source and destination
// pairs in a standardized way, we choose the server way of sorting, such that the ephemeral port
// on the client is first.
static __always_inline void sort_connection_info(connection_info_t *info) {
    if (likely_ephemeral_port(info->s_port) && !likely_ephemeral_port(info->d_port)) {
        return;
    }

    if ((likely_ephemeral_port(info->d_port) && !likely_ephemeral_port(info->s_port)) ||
        (info->d_port > info->s_port)) {
        // Only sort if they are explicitly reversed, otherwise always sort source to be the larger
        // of the two ports
        swap_connection_info_order(info);
    }
}

static __always_inline void dbg_print_http_connection_info(connection_info_t *info) {
    // TODO: enable this
    // if (!g_bpf_debug) {
    //     return;
    // }

    bpf_dbg_printk("[conn] s_h=%llx, s_l=%llx, s_port=%d",
                   (u64)(info->s_addr),
                   (u64)(info->s_addr[8]),
                   info->s_port);
    bpf_dbg_printk("[conn] d_h=%llx, d_l=%llx, d_port=%d",
                   (u64)(info->d_addr),
                   (u64)(info->d_addr[8]),
                   info->d_port);
}
