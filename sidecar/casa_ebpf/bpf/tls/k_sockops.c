//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_endian.h>
#include <core/bpf_helpers.h>
#include <core/bpf_tracing.h>

#include <common/connection_info.h>
#include <common/http.h>
#include <common/protocol_defs.h>

#include <logger/bpf_dbg.h>

#include <pid/pid.h>

#include <tls/ssl_args.h>
#include <tls/obi_types.h>

static __always_inline void bpf_sock_ops_set_flags(struct bpf_sock_ops *skops, u8 flags) {
    bpf_sock_ops_cb_flags_set(skops, skops->bpf_sock_ops_cb_flags | flags);
}

// Extracts what we need for connection_info_t from bpf_sock_ops if the
// communication is IPv4
static __always_inline connection_info_t sk_ops_extract_key_ip4(struct bpf_sock_ops *ops) {
    connection_info_t conn = {};

    const u32 local_ip4 = ops->local_ip4;
    const u32 remote_ip4 = ops->remote_ip4;
    const u32 local_port = ops->local_port;
    const u32 remote_port = bpf_ntohl(ops->remote_port);

    __builtin_memcpy(conn.s_addr, ip4ip6_prefix, sizeof(ip4ip6_prefix));
    conn.s_ip[3] = local_ip4;
    __builtin_memcpy(conn.d_addr, ip4ip6_prefix, sizeof(ip4ip6_prefix));
    conn.d_ip[3] = remote_ip4;

    conn.s_port = local_port;
    conn.d_port = remote_port;

    return conn;
}

// Extracts what we need for connection_info_t from bpf_sock_ops if the
// communication is IPv6
// The order of copying the data from bpf_sock_ops matters and must match how
// the struct is laid in vmlinux.h, otherwise the verifier thinks we are modifying
// the context twice.
static __always_inline connection_info_t sk_ops_extract_key_ip6(struct bpf_sock_ops *ops) {
    connection_info_t conn = {};

    conn.d_ip[0] = ops->remote_ip6[0];
    conn.d_ip[1] = ops->remote_ip6[1];
    conn.d_ip[2] = ops->remote_ip6[2];
    conn.d_ip[3] = ops->remote_ip6[3];
    conn.s_ip[0] = ops->local_ip6[0];
    conn.s_ip[1] = ops->local_ip6[1];
    conn.s_ip[2] = ops->local_ip6[2];
    conn.s_ip[3] = ops->local_ip6[3];

    const u32 local_port = ops->local_port;
    const u32 remote_port = bpf_ntohl(ops->remote_port);

    conn.d_port = remote_port;
    conn.s_port = local_port;

    return conn;
}

static __always_inline connection_info_t get_connection_info_ops(struct bpf_sock_ops *ops) {
    return ops->family == AF_INET6 ? sk_ops_extract_key_ip6(ops) : sk_ops_extract_key_ip4(ops);
}

// Tracks all outgoing sockets (BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB)
// We don't track incoming, those would be BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB
SEC("sockops")
int parse_obi_tp_option(struct bpf_sock_ops *skops) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 1;
    }

    if (skops->op == BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB) {
        bpf_sock_ops_set_flags(skops, BPF_SOCK_OPS_WRITE_HDR_OPT_CB_FLAG);
        return 1;
    }

    if (skops->op == BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB) {
        bpf_sock_ops_set_flags(skops, BPF_SOCK_OPS_PARSE_ALL_HDR_OPT_CB_FLAG);
        return 1;
    }

    struct bpf_sock *sk = skops->sk;

    if (!sk || (skops->op != BPF_SOCK_OPS_WRITE_HDR_OPT_CB && skops->op != BPF_SOCK_OPS_PARSE_HDR_OPT_CB)) {
        return 1;
    }

    bpf_dbg_printk("=== sockops id=%d, sock=%llx ===", id, sk);

    struct obi_tp_option opt = {};
    opt.kind = k_tcp_option_kind_otel;

    const long ret = bpf_load_hdr_opt(skops, &opt, sizeof(opt), 0);

    if (ret == -ENOMSG) {
        bpf_dbg_printk("error parsing OBI TCP option: %d", ret);
        return 1;
    }

    if (ret < 0) {
        bpf_dbg_printk("error parsing OBI TCP option: %d", ret);
        return 1;
    }

    const char *tp_str = tp_string_from_opt(&opt);

    if (tp_str) {
        bpf_dbg_printk("found TP in TCP options: %s", tp_str);
    } else {
        bpf_dbg_printk("could not find TP in TCP options");
    }

    struct tls_data_event *event = bpf_ringbuf_reserve(&tls_events, sizeof(struct tls_data_event), 0);
    if (!event) {
        bpf_dbg_printk("=== failed to create tls_data_event ===");
        return 1;
    }

    __builtin_memcpy(event->tp.trace_id, opt.trace_id, sizeof(event->tp.trace_id));
    __builtin_memcpy(event->tp.span_id, opt.span_id, sizeof(event->tp.span_id));

    connection_info_t conn = get_connection_info_ops(skops);
    sort_connection_info(&conn);

    dbg_print_http_connection_info(&conn);

    event->pid_tgid = id;
    event->ssl = 0;
    event->len = 0;
    event->original_len = 0;
    event->direction = 0;
    event->type = (u64)EVENT_TP;
    event->done = 0;

    __builtin_memcpy(&event->conn, &conn, sizeof(conn));

    bpf_ringbuf_submit(event, 0);

    return 1;
}
