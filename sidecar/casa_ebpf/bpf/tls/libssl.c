//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>
#include <core/bpf_tracing.h>

#include <common/connection_info.h>
#include <common/http.h>

#include <logger/bpf_dbg.h>

#include <pid/pid.h>

#include <tls/ssl_args.h>

static __always_inline ssl_pid_connection_info_t * fetch_ssl_conn_mapping(void *ssl, u64 id) {
    const u64 ssl_ptr = (u64)ssl;
    ssl_pid_connection_info_t *conn = bpf_map_lookup_elem(&ssl_to_conn, &ssl);
    if (!conn) {
        conn = bpf_map_lookup_elem(&pid_tid_to_conn, &id);
        if (!conn) {
            // We try even harder, we might have an SSL pointer mapped on another
            // thread, since tcp_rcv_established was handled on another thread pool.
            // First we look up a pid_tid by the ssl pointer, which might've been established
            // by a prior SSL_read on another thread, then we look up in the same map.
            // Clean-up here we are done trying if we don't succeed
            u64 *pid_tid_ptr = bpf_map_lookup_elem(&ssl_to_pid_tid, &ssl_ptr);

            if (pid_tid_ptr) {
                const u64 pid_tid = *pid_tid_ptr;

                conn = bpf_map_lookup_elem(&pid_tid_to_conn, &pid_tid);
                bpf_dbg_printk(
                    "Separate pool lookup ssl=%llx, pid=%d, conn=%llx", ssl_ptr, pid_tid, conn);
            } else {
                bpf_dbg_printk("Other thread lookup failed for ssl=%llx", ssl_ptr);
            }
        }

        // If we found a connection setup by tcp_rcv_established, which means
        // we missed a SSL_do_handshake, update our ssl to connection map to be
        // used by the rest of the SSL lifecycle. We shouldn't rely on the SSL_write
        // being on the same thread as the SSL_read.
        if (conn) {
            bpf_map_delete_elem(&pid_tid_to_conn, &id);
            ssl_pid_connection_info_t c;
            bpf_probe_read(&c, sizeof(ssl_pid_connection_info_t), conn);
            bpf_map_update_elem(&ssl_to_conn, &ssl, &c, BPF_ANY);
        }
    }

    bpf_map_delete_elem(&ssl_to_pid_tid, &ssl_ptr);

    return conn;
}

static __always_inline void handle_http_operation(struct pt_regs *ctx,
                                                 u64 id,
                                                 const ssl_args_t *args,
                                                 size_t bytes_len,
                                                 const enum traffic_direction direction) {
    if (!args) {
        return;
    }

    u32 buf_len = bytes_len;

    if (buf_len > MAX_CHUNK_SIZE) {
        buf_len = MAX_CHUNK_SIZE;
    }

    struct tls_data_event *event = bpf_ringbuf_reserve(&tls_events, sizeof(struct tls_data_event), 0);
    if (!event) {
        bpf_dbg_printk("=== failed to create tls_data_event ===");
        return;
    }

    void *ssl = ((void *)args->ssl);

    ssl_pid_connection_info_t *conn = fetch_ssl_conn_mapping(ssl, id);
    if (conn) {
        bpf_dbg_printk("=== id=[%d] conn=%llx ===", id, conn);
        dbg_print_http_connection_info(&conn->p_conn.conn);
    }

    bpf_dbg_printk("=== id=[%d] buf_len=[%d] bytes_len=[%d] ===", id, buf_len, bytes_len);

    event->pid_tgid = id;
    event->ssl = args->ssl;
    event->len = buf_len;
    event->original_len = bytes_len;
    event->direction = (u64)direction;
    event->type = (u64)EVENT_DATA;
    event->done = 0;

    if (conn) {
        __builtin_memcpy(&event->conn, &conn->p_conn.conn, sizeof(conn->p_conn.conn));
    }

    bpf_probe_read(event->data, buf_len, (void *)args->buf);

    bpf_ringbuf_submit(event, 0);
}

SEC("uprobe/libssl.so:SSL_read")
int BPF_UPROBE(uprobe_ssl_read, void *ssl, void *buf, int num) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_read id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;

    bpf_map_update_elem(&active_ssl_read_args, &id, &args, BPF_ANY);
    bpf_map_update_elem(&ssl_to_pid_tid, &args.ssl, &id, BPF_NOEXIST);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read")
int BPF_URETPROBE(uretprobe_ssl_read, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_read_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_read id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret <= 0 || !args) {
        bpf_map_delete_elem(&active_ssl_read_args, &id);
        return 0;
    }

    handle_http_operation(ctx, id, args, ret, TCP_RECV);
    bpf_map_delete_elem(&active_ssl_read_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_read_ex")
int BPF_UPROBE(uprobe_ssl_read_ex, void *ssl, void *buf, size_t num, size_t *readbytes) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_read_ex id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;
    args.len_ptr = (u64)readbytes;

    bpf_map_update_elem(&active_ssl_read_args, &id, &args, BPF_ANY);
    bpf_map_update_elem(&ssl_to_pid_tid, &args.ssl, &id, BPF_NOEXIST);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read_ex")
int BPF_URETPROBE(uretprobe_ssl_read_ex, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_read_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_read_ex id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret != 1 || !args) {
        bpf_map_delete_elem(&active_ssl_read_args, &id);
        return 0;
    }

    size_t bytes_len = 0;
    bpf_probe_read(&bytes_len, sizeof(bytes_len), (void *)args->len_ptr);

    handle_http_operation(ctx, id, args, bytes_len, TCP_RECV);
    bpf_map_delete_elem(&active_ssl_read_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write")
int BPF_UPROBE(uprobe_ssl_write, void *ssl, const void *buf, int num) {
    (void)ctx;
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_write id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;
    args.len_ptr = num;

    bpf_map_update_elem(&active_ssl_write_args, &id, &args, BPF_ANY);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_write")
int BPF_URETPROBE(uretprobe_ssl_write, int ret) {
    (void)ctx;
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_write_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_write id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret <= 0 || !args) {
        bpf_map_delete_elem(&active_ssl_write_args, &id);
        return 0;
    }

    handle_http_operation(ctx, id, args, ret, TCP_SEND);
    bpf_map_delete_elem(&active_ssl_write_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write_ex")
int BPF_UPROBE(uprobe_ssl_write_ex, void *ssl, const void *buf, size_t num, size_t *written) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_write_ex id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;
    args.len_ptr = (u64)written;

    bpf_map_update_elem(&active_ssl_write_args, &id, &args, BPF_ANY);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_write_ex")
int BPF_URETPROBE(uretprobe_ssl_write_ex, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_write_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_write_ex id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret != 1 || !args) {
        bpf_map_delete_elem(&active_ssl_write_args, &id);
        return 0;
    }

    size_t bytes_len = 0;
    bpf_probe_read(&bytes_len, sizeof(bytes_len), (void *)args->len_ptr);

    handle_http_operation(ctx, id, args, bytes_len, TCP_SEND);
    bpf_map_delete_elem(&active_ssl_write_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_free")
int BPF_UPROBE(uprobe_ssl_free, void *ssl) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_free id=%d ssl=%llx ===", id, ssl);

    struct tls_data_event *event = bpf_ringbuf_reserve(&tls_events, sizeof(struct tls_data_event), 0);
    if (!event) {
        bpf_dbg_printk("=== uretprobe SSL_read_ex failed to create tls_data_event ===");
        bpf_map_delete_elem(&active_ssl_read_args, &id);
        return 0;
    }

    event->pid_tgid = id;
    event->ssl = (u64)ssl;
    event->done = 1;

    bpf_ringbuf_submit(event, 0);

    return 0;
}

SEC("uprobe/libssl.so:SSL_shutdown")
int BPF_UPROBE(uprobe_ssl_shutdown, void *ssl) {
    const u64 id = bpf_get_current_pid_tgid();

    if (!allowed_pid(id)) {
        return 0;
    }

    bpf_dbg_printk("=== uprobe SSL_shutdown id=%d ssl=%llx ===", id, ssl);

    ssl_pid_connection_info_t *s_conn = bpf_map_lookup_elem(&ssl_to_conn, &ssl);
    if (s_conn) {
        bpf_map_delete_elem(&active_ssl_connections, &s_conn->p_conn);
    }

    bpf_map_delete_elem(&ssl_to_conn, &ssl);
    bpf_map_delete_elem(&ssl_to_pid_tid, &ssl);

    bpf_map_delete_elem(&pid_tid_to_conn, &id);

    return 0;
}
