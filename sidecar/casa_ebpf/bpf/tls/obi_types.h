#pragma once

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>

#include <tls/tp_value.h>

enum { k_tcp_option_kind_otel = 25 };

#define TRACE_ID_SIZE_BYTES 16
#define SPAN_ID_SIZE_BYTES 8

#ifndef ENOMSG
#define ENOMSG 42
#endif

struct obi_tp_option {
    u8 kind;
    u8 len;
    unsigned char trace_id[TRACE_ID_SIZE_BYTES];
    unsigned char span_id[SPAN_ID_SIZE_BYTES];
};

struct conn_key {
    u32 saddr;
    u32 daddr;
    u16 sport;
    u16 dport;
};

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 65536);
    __type(key, struct conn_key);
    __type(value, struct tp_value);
} tp_by_conn SEC(".maps");

///////////

#define SCRATCH_MEM_SIZED(NAME, SIZE)                                                              \
    struct {                                                                                       \
        __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);                                                   \
        __uint(key_size, sizeof(u32));                                                             \
        __uint(value_size, SIZE);                                                                  \
        __uint(max_entries, 1);                                                                    \
    } NAME##_storage SEC(".maps");                                                                 \
                                                                                                   \
    static __always_inline void *NAME##_mem(void) {                                                \
        return bpf_map_lookup_elem(&NAME##_storage, &(u32){0});                                    \
    }

#define SCRATCH_MEM_TYPED(NAME, TYPE) SCRATCH_MEM_SIZED(NAME, sizeof(TYPE))
#define SCRATCH_MEM(NAME) SCRATCH_MEM_TYPED(NAME, NAME)

SCRATCH_MEM_SIZED(tp_str_buf, 64)

#define TRACE_ID_CHAR_LEN 32
#define SPAN_ID_CHAR_LEN 16

static unsigned char *hex = (unsigned char *)"0123456789abcdef";

static __always_inline void encode_hex(unsigned char *dst, const unsigned char *src, u32 src_len) {
    for (u32 i = 0, j = 0; i < src_len; i++) {
        unsigned char p = src[i];
        dst[j++] = hex[(p >> 4) & 0xff];
        dst[j++] = hex[p & 0x0f];
    }
}

static __always_inline const char *tp_string_from_opt(const struct obi_tp_option *opt) {
    unsigned char *buf = tp_str_buf_mem();

    if (!buf) {
        return NULL;
    }

    unsigned char *ptr = buf;

    // Version
    *ptr++ = '0';
    *ptr++ = '0';
    *ptr++ = '-';

    // Trace ID
    encode_hex(ptr, opt->trace_id, TRACE_ID_SIZE_BYTES);
    ptr += TRACE_ID_CHAR_LEN;

    *ptr++ = '-';

    // SpanID
    encode_hex(ptr, opt->span_id, SPAN_ID_SIZE_BYTES);
    ptr += SPAN_ID_CHAR_LEN;

    *ptr++ = '-';

    *ptr++ = '0';
    *ptr++ = '\0';

    return (const char *)buf;
}
