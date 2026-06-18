#pragma once

#include <core/vmlinux.h>
#include <core/bpf_endian.h>
#include <core/bpf_helpers.h>

#include <common/connection_info.h>
#include <common/protocol_defs.h>

static __always_inline bool parse_sock_info(struct sock *s, connection_info_t *info) {
    short unsigned int skc_family;
    BPF_CORE_READ_INTO(&skc_family, s, __sk_common.skc_family);

    // We always store the IP addresses in IPV6 format, simplifies the code and
    // it matches natively what our Golang userspace processing will require.
    if (skc_family == AF_INET) {
        u32 ip4_s_l;
        u32 ip4_d_l;
        BPF_CORE_READ_INTO(
            &info->s_port, s, __sk_common.skc_num); // weirdly not in network byte order
        BPF_CORE_READ_INTO(&ip4_s_l, s, __sk_common.skc_rcv_saddr);
        BPF_CORE_READ_INTO(&info->d_port, s, __sk_common.skc_dport);
        info->d_port = bpf_ntohs(info->d_port);
        BPF_CORE_READ_INTO(&ip4_d_l, s, __sk_common.skc_daddr);

        __builtin_memcpy(info->s_addr, ip4ip6_prefix, sizeof(ip4ip6_prefix));
        __builtin_memcpy(info->d_addr, ip4ip6_prefix, sizeof(ip4ip6_prefix));
        __builtin_memcpy(info->s_addr + sizeof(ip4ip6_prefix), &ip4_s_l, sizeof(ip4_s_l));
        __builtin_memcpy(info->d_addr + sizeof(ip4ip6_prefix), &ip4_d_l, sizeof(ip4_d_l));

        return true;
    } else if (skc_family == AF_INET6) {
        BPF_CORE_READ_INTO(
            &info->s_port, s, __sk_common.skc_num); // weirdly not in network byte order
        BPF_CORE_READ_INTO(&info->s_addr, s, __sk_common.skc_v6_rcv_saddr.in6_u.u6_addr8);
        BPF_CORE_READ_INTO(&info->d_port, s, __sk_common.skc_dport);
        info->d_port = bpf_ntohs(info->d_port);
        BPF_CORE_READ_INTO(&info->d_addr, s, __sk_common.skc_v6_daddr.in6_u.u6_addr8);

        return true;
    }

    return false;
}
