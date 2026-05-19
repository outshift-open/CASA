//go:build ignore

#include <core/vmlinux.h>
#include <core/bpf_helpers.h>
#include <core/bpf_tracing.h>

#include<common/http.h>
#include <logger/bpf_dbg.h>

#include <tls/ssl_args.h>

// struct {
//     __uint(type, BPF_MAP_TYPE_LRU_HASH);
//     __uint(max_entries, MAX_CONCURRENT_SHARED_REQUESTS);
//     __type(key, u64);
//     __type(value, ssl_args_t);
//     __uint(pinning, OBI_PIN_INTERNAL);
// } active_ssl_write_args SEC(".maps");

static __always_inline void handle_http_response(struct pt_regs *ctx,
                                                 u64 id,
                                                 const ssl_args_t *args,
                                                 const enum traffic_direction direction) {
    if (!args) {
        return;
    }

    size_t bytes_len = 0;
    bpf_probe_read(&bytes_len, sizeof(bytes_len), (void *)args->len_ptr);

    u32 buf_len = bytes_len;

    if (buf_len > MAX_CHUNK_SIZE) {
        buf_len = MAX_CHUNK_SIZE;
    }

    struct tls_data_event *event = bpf_ringbuf_reserve(&tls_events, sizeof(struct tls_data_event), 0);
    if (!event) {
        bpf_dbg_printk("=== failed to create tls_data_event ===");
        bpf_map_delete_elem(&active_ssl_args, &id);
        return;
    }

    bpf_dbg_printk("=== id=[%d] buf_len=[%d] bytes_len=[%d] ===", id, buf_len, bytes_len);

    event->pid_tgid = id;
    event->ssl = args->ssl;
    event->len = buf_len;
    event->original_len = bytes_len;

    bpf_probe_read(event->data, buf_len, (void *)args->buf);

    bpf_ringbuf_submit(event, 0);

    bpf_map_delete_elem(&active_ssl_args, &id);
}

SEC("uprobe/libssl.so:SSL_read")
int BPF_UPROBE(uprobe_ssl_read, void *ssl, void *buf, int num) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_read id=%d ssl=%llx ===", id, ssl);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read")
int BPF_URETPROBE(uretprobe_ssl_read, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uretprobe SSL_read id=%d ret=%d ===", id, ret);

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
    args.flags = 0;

    bpf_map_update_elem(&active_ssl_args, &id, &args, BPF_ANY);

    return 0;
}

SEC("uretprobe/libssl.so:SSL_read_ex")
int BPF_URETPROBE(uretprobe_ssl_read_ex, int ret) {
    const u64 id = bpf_get_current_pid_tgid();

    ssl_args_t *args = bpf_map_lookup_elem(&active_ssl_args, &id);

    if (args) {
        bpf_dbg_printk("=== uretprobe SSL_read_ex id=%d ret=%d ssl=%x args=%llx ===", id, ret, args->ssl, args);
    } else {
        bpf_dbg_printk("=== uretprobe SSL_read_ex id=%d ret=%d args=%llx ===", id, ret, args);
    }

    if (ret != 1 || !args) {
        bpf_map_delete_elem(&active_ssl_args, &id);
        return 0;
    }

    handle_http_response(ctx, id, args, TCP_RECV);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write")
int BPF_UPROBE(uprobe_ssl_write, void *ssl, const void *buf, int num) {
    (void)ctx;
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_write id=%d ssl=%llx ===", id, ssl);

    return 0;
}

SEC("uprobe/libssl.so:SSL_write_ex")
int BPF_UPROBE(uprobe_ssl_write_ex, void *ssl, const void *buf, size_t num, size_t *written) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_write_ex id=%d ssl=%llx ===", id, ssl);

    // ssl_args_t args = {};
    // args.buf = (u64)buf;
    // args.ssl = (u64)ssl;
    // args.len_ptr = num;
    // args.flags = 0;

    return 0;
}

SEC("uprobe/libssl.so:SSL_free")
int BPF_UPROBE(uprobe_ssl_free, void *ssl) {
    const u64 id = bpf_get_current_pid_tgid();

    bpf_dbg_printk("=== uprobe SSL_free id=%d ssl=%llx ===", id, ssl);

    struct tls_data_event *event = bpf_ringbuf_reserve(&tls_events, sizeof(struct tls_data_event), 0);
    if (!event) {
        bpf_dbg_printk("=== uretprobe SSL_read_ex failed to create tls_data_event ===");
        bpf_map_delete_elem(&active_ssl_args, &id);
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
