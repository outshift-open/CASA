//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>
#include <core/bpf_tracing.h>

#include<common/http.h>
#include <logger/bpf_dbg.h>

#include <tls/ssl_args.h>

static __always_inline void handle_http_response(struct pt_regs *ctx,
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

    bpf_dbg_printk("=== id=[%d] buf_len=[%d] bytes_len=[%d] ===", id, buf_len, bytes_len);

    event->pid_tgid = id;
    event->ssl = args->ssl;
    event->len = buf_len;
    event->original_len = bytes_len;
    event->direction = (u64)direction;

    bpf_probe_read(event->data, buf_len, (void *)args->buf);

    bpf_ringbuf_submit(event, 0);
}

SEC("uprobe/libssl.so:SSL_read")
int BPF_UPROBE(uprobe_ssl_read, void *ssl, void *buf, int num) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_read id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;

    bpf_map_update_elem(&active_ssl_read_args, &id, &args, BPF_ANY);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read")
int BPF_URETPROBE(uretprobe_ssl_read, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_read_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_read id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret <= 0 || !args) {
        bpf_map_delete_elem(&active_ssl_read_args, &id);
        return 0;
    }

    handle_http_response(ctx, id, args, ret, TCP_RECV);
    bpf_map_delete_elem(&active_ssl_read_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_read_ex")
int BPF_UPROBE(uprobe_ssl_read_ex, void *ssl, void *buf, size_t num, size_t *readbytes) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_read_ex id=%d ssl=%llx ===", id, ssl);

    ssl_args_t args = {};
    args.buf = (u64)buf;
    args.ssl = (u64)ssl;
    args.len_ptr = (u64)readbytes;

    bpf_map_update_elem(&active_ssl_read_args, &id, &args, BPF_ANY);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read_ex")
int BPF_URETPROBE(uretprobe_ssl_read_ex, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_read_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_read_ex id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret != 1 || !args) {
        bpf_map_delete_elem(&active_ssl_read_args, &id);
        return 0;
    }

    size_t bytes_len = 0;
    bpf_probe_read(&bytes_len, sizeof(bytes_len), (void *)args->len_ptr);

    handle_http_response(ctx, id, args, bytes_len, TCP_RECV);
    bpf_map_delete_elem(&active_ssl_read_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write")
int BPF_UPROBE(uprobe_ssl_write, void *ssl, const void *buf, int num) {
    (void)ctx;
    const u64 id = bpf_get_current_pid_tgid();

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

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_write_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_write id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret <= 0 || !args) {
        bpf_map_delete_elem(&active_ssl_write_args, &id);
        return 0;
    }

    handle_http_response(ctx, id, args, ret, TCP_SEND);
    bpf_map_delete_elem(&active_ssl_write_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write_ex")
int BPF_UPROBE(uprobe_ssl_write_ex, void *ssl, const void *buf, size_t num, size_t *written) {
    const u64 id = bpf_get_current_pid_tgid();

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

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_write_args, &id);

    bpf_dbg_printk("=== uretprobe SSL_write_ex id=%d ret=%d args=%llx ===", id, ret, args);

    if (ret != 1 || !args) {
        bpf_map_delete_elem(&active_ssl_write_args, &id);
        return 0;
    }

    size_t bytes_len = 0;
    bpf_probe_read(&bytes_len, sizeof(bytes_len), (void *)args->len_ptr);

    handle_http_response(ctx, id, args, bytes_len, TCP_SEND);
    bpf_map_delete_elem(&active_ssl_write_args, &id);

    return 0;
}

SEC("uprobe/libssl.so:SSL_free")
int BPF_UPROBE(uprobe_ssl_free, void *ssl) {
    const u64 id = bpf_get_current_pid_tgid();

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

    bpf_dbg_printk("=== uprobe SSL_shutdown id=%d ssl=%llx ===", id, ssl);

    return 0;
}

char __license[] SEC("license") = "Dual MIT/GPL";
