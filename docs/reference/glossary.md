# Glossary

Terms are used with exactly these meanings throughout the specification.

**ABI** Binary interface between two compiled components. In CDIN: C ABI. See [abi-and-compatibility.md](../architecture/abi-and-compatibility.md).

**Anchor (code anchor)** A pointer from an `EXISTING` statement to the file or section in `cdin` that proves it.

**Backend** The headless core process logic of CDIN: session management, hosting of kernel and runtime, OS services and the Frontend Protocol server. It has no knowledge of any display toolkit. Not a "server" in the network sense. See [backend.md](../components/backend.md).

**Byte offset** Position counted in bytes from the start of a document. The canonical position in the kernel API.

**Capability** A feature a frontend declares during the protocol handshake (for example images, mouse, 24-bit colour). The backend sends only what the frontend accepted.

**cdin** Two things, always disambiguated: *cdin the composition root* (the repository and build that assembles and releases the product), and *cdin the product*. This specification says "the `cdin` repository" or "the composition root" when it means the former.

**cdin-x** The optional extension ecosystem, a separate repository. Sees only the extension contract.

**Code point** A Unicode scalar value. Not a user-perceived character.

**Component** A unit of the architecture with one responsibility and a contract. A component is not necessarily a repository. See [repositories.md](../architecture/repositories.md).

**Composition root** The one place that wires concrete components together: builds, bundles, launches. It contains no domain logic.

**Conformance vector** A data-driven test case expressed against a public contract, runnable against any implementation of it. Described in [conformance.md](../testing/conformance.md); none are written yet.

**`data` (the directory)** In the current `cdin` repository, `data/` is the *Lua runtime source tree* (`data/core/`) and, in a build output, the assembled directory of plugins, themes and fonts. It is **not** the same as the `DATA` component below. See [data.md](../components/data.md).

**DATA (the component)** Persistence and serialization responsibilities (file load/save, atomic write, session storage). `DEFERRED` as a repository; see [data.md](../components/data.md).

**Document** A kernel-owned unit of text with identity, version and its own undo history.

**Extension contract** The Lua-level API and protocol that `cdin` guarantees to extensions. Defined today in `docs/architecture/extension-contract.md` of the `cdin` repository.

**Frontend** A program or module that presents the editor and collects input: GUI, TUI, CLI, headless, web. It speaks only the Frontend Protocol. Frontends are peers.

**Frontend Protocol** The versioned message contract between backend and frontends. See [frontend-protocol.md](../architecture/frontend-protocol.md).

**Grapheme cluster** A user-perceived character as defined by Unicode text segmentation, relative to a pinned Unicode version.

**Handle** An opaque reference to a kernel or protocol object. Carries a generation so stale handles are detectable.

**Host** In older notes, "Backend / Host" meant the OS-facing side. In this specification the OS-facing part is the *OS services* of the backend.

**Kernel** The generic text engine. Owns documents. Independent of every other component. See [kernel/overview.md](../kernel/overview.md).

**Logical position** A position in document content (byte offset, code point, grapheme). Contrasted with *visual position*.

**OS services** The part of the backend that wraps files, paths, processes, jobs, time. Independent of any display toolkit.

**Raw region** A maximal run of document bytes that is not valid UTF-8. Preserved exactly.

**Runtime** The Lua 5.4 policy layer and extension host: commands, keymaps, configuration, plugin loading, UI model.

**Snapshot** An immutable, reference-counted view of a document at one committed version. Used for concurrent reads.

**Spec** This repository.

**UI model** The semantic description of what the editor shows (windows, views, status line, prompt, panels), produced by the runtime and relayed by the backend. Contains no pixels.

**View** A logical editing surface onto a document: owns selections and logical scroll anchor. Distinct from the frontend's *visual layout*.

**Version** A per-document, monotonically increasing integer identifying one committed state.

**Visual column / visual layout** Where text lands on a screen after wrapping, shaping, bidi reordering and tab expansion. Owned by frontends; never by the kernel.
