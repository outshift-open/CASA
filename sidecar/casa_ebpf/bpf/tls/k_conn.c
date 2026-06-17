//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>
#include <core/bpf_tracing.h>

#include <logger/bpf_dbg.h>

#include <pid/pid.h>

#include <tls/ssl_helpers.h>

static __always_inline void
setup_connection_to_pid_mapping(u64 id, pid_connection_info_t *p_conn, u16 orig_dport) {
    ssl_pid_connection_info_t *prev_info = bpf_map_lookup_elem(&pid_tid_to_conn, &id);
    // We only update here when we don't know the direction if we haven't previously
    // set the information in sys_accept or sys_connect
    if (!prev_info || (prev_info->p_conn.conn.d_port != p_conn->conn.d_port) ||
        (prev_info->p_conn.conn.s_port != p_conn->conn.s_port)) {
        ssl_pid_connection_info_t ssl_conn = {0};
        ssl_conn.orig_dport = orig_dport;
        ssl_conn.p_conn = *p_conn;

        bpf_map_update_elem(&pid_tid_to_conn, &id, &ssl_conn, BPF_ANY);
    }
}

SEC("kprobe/tcp_recvmsg")
int BPF_KPROBE(kprobe_tcp_recvmsg_tls, struct sock *sk, struct msghdr *msg, size_t len,
		       int flags, int *addr_len) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== kprobe/tcp_recvmsg id=%d, sock=%llx ===", id, sk);

    connect_ssl_to_sock(id, sk, TCP_RECV);

    return 0;
}

SEC("kprobe/sock_recvmsg")
int BPF_KPROBE(kprobe_sock_recvmsg_tls, struct socket *sock, struct msghdr *msg, int flags) {
    (void)ctx;
    (void)flags;

    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    struct sock *sk = 0;
    BPF_CORE_READ_INTO(&sk, sock, sk);

    bpf_dbg_printk("=== kprobe/sock_recvmsg sock=%llx, socket=%llx ===", sk, sock);
    if (sk) {
        connect_ssl_to_sock(id, sk, TCP_RECV);
    }

    connection_info_t conn = {};

    if (parse_sock_info(sk, &conn)) {
        const u16 orig_dport = conn.d_port;
        dbg_print_http_connection_info(&conn);
        bpf_dbg_printk("=== kprobe/sock_recvmsg orig_dport=%d ===", orig_dport);
    }

    return 0;
}

static __always_inline void handle_sendmsg(u64 id, struct sock *sk) {
    pid_connection_info_t p_conn = {};

    if (parse_sock_info(sk, &p_conn.conn)) {
        const u16 orig_dport = p_conn.conn.d_port;
        dbg_print_http_connection_info(&p_conn.conn);

        bpf_dbg_printk("=== kprobe/handle_sendmsg orig_dport=%d ===", orig_dport);

        sort_connection_info(&p_conn.conn);
        p_conn.pid = pid_from_pid_tgid(id);

        connect_ssl_to_connection(id, &p_conn, TCP_SEND, orig_dport);
        setup_connection_to_pid_mapping(id, &p_conn, orig_dport);

        u64 *ssl = is_ssl_connection(&p_conn);

        bpf_dbg_printk("id=%d, ssl=%llx", id, ssl);

        if (ssl) {
            ssl_pid_connection_info_t ssl_conn = {
                .orig_dport = orig_dport,
            };
            __builtin_memcpy(&ssl_conn.p_conn, &p_conn, sizeof(pid_connection_info_t));
            bpf_map_update_elem(&ssl_to_conn, &ssl, &ssl_conn, BPF_ANY);
        }
    }
}

SEC("kprobe/tcp_sendmsg")
int BPF_KPROBE(kprobe_tcp_sendmsg_tls, struct sock *sk, struct msghdr *msg, size_t size) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== kprobe/tcp_sendmsg id=%d, sock=%llx, size=%d ===", id, sk, size);

    handle_sendmsg(id, sk);

    return 0;
}

// This is a backup path kprobe in case tcp_sendmsg doesn't fire, which
// happens on certain kernels if sk_msg is attached.
SEC("kprobe/tcp_rate_check_app_limited")
int BPF_KPROBE(kprobe_tcp_rate_check_app_limited_tls, struct sock *sk) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== kprobe/tcp_rate_check_app_limited id=%d, sock=%llx ===", id, sk);

    handle_sendmsg(id, sk);

    return 0;
}
