#pragma once

#define AF_INET 2   /* Internet IP Protocol */
#define AF_INET6 10 /* IP version 6 */

// Most Linux distros use 32768 to 61000 for the ephemeral ports, so we look up from 32768
// IANA suggests that the range should be 49152-65535, which is what Windows uses
#define EPHEMERAL_PORT_MIN 32768
