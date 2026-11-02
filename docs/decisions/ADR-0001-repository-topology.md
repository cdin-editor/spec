# Legacy decision pointer — repository topology

This file is retained for old links only. The canonical repository-topology decision is maintained in [`docs/adr/`](../adr/README.md), with the current no-shared-repository rule in [ADR-0014](../adr/ADR-0014-no-shared-repositories.md).

The protocol reference codec placement is now settled by [ADR-0018](../adr/ADR-0018-frontend-protocol-wire.md): it is the independently linkable `cdin_protocol` target inside the Backend repository, not a separate repository. The PUC Lua 5.4 bridge is settled by [ADR-0019](../adr/ADR-0019-runtime-bridge.md).
