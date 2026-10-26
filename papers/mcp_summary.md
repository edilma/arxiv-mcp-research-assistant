# Model Context Protocol (MCP) – Architecture Summary

> Source: https://modelcontextprotocol.io/docs/concepts/architecture

---

## 1. Overview

The **Model Context Protocol (MCP)** is an open protocol that standardises how AI applications exchange context with external servers. It focuses solely on the **protocol for context exchange** — it does not dictate how AI applications use LLMs or manage the context they receive.

The MCP ecosystem consists of four projects:
- **MCP Specification** – Defines implementation requirements for clients and servers.
- **MCP SDKs** – Language-specific libraries that implement the protocol.
- **MCP Development Tools** – Utilities such as the MCP Inspector for building and debugging.
- **MCP Reference Server Implementations** – Ready-made reference servers.

---

## 2. Participants

MCP follows a **client-server architecture** with three key roles:

| Participant  | Role |
|---|---|
| **MCP Host**   | The AI application (e.g., Claude Desktop, VS Code) that manages one or more MCP clients. |
| **MCP Client** | A component created by the host to maintain a dedicated connection with a single MCP server. |
| **MCP Server** | A program that provides context (tools, resources, prompts) to MCP clients. |

Key rules:
- One **MCP client** is instantiated per **MCP server** connection.
- **Local servers** (STDIO transport) typically serve a single client.
- **Remote servers** (Streamable HTTP transport) typically serve many clients simultaneously.

---

## 3. Layers

MCP is split into two conceptual layers:

### 3a. Data Layer (Inner Layer)
Defines the **JSON-RPC 2.0** based protocol for client-server communication. It includes:

- **Discovery** – `server/discover` lets clients query a server's supported protocol versions, capabilities, and identity.
- **Server Features (Primitives)**:
  - 🔧 **Tools** – Executable functions AI can invoke (e.g., file operations, API calls, DB queries). Discovered via `tools/list`, executed via `tools/call`.
  - 📦 **Resources** – Data sources providing contextual information (e.g., file contents, DB records). Discovered via `resources/list`, retrieved via `resources/get`.
  - 💬 **Prompts** – Reusable interaction templates (e.g., system prompts, few-shot examples).
- **Client Features (Primitives)**:
  - **Elicitation** – Servers can request additional input from users via `elicitation/create`.
  - ~~Sampling~~ – *(Deprecated as of 2026-07-28)* Servers requesting LLM completions from the client.
  - ~~Logging~~ – *(Deprecated as of 2026-07-28)* Servers sending logs to clients.
- **Utility Features**:
  - **Notifications** – Real-time push updates (e.g., `notifications/tools/list_changed` when a server's tool list changes). Change notifications are opt-in via `subscriptions/listen`.
  - **Progress Tracking** – Support for tracking long-running operations.
  - **Tasks Extension** – Servers return a durable handle for long-running requests so clients can poll for results later.

### 3b. Transport Layer (Outer Layer)
Manages **communication channels** and **authentication** between clients and servers. MCP supports two transport mechanisms:

| Transport          | Description |
|---|---|
| **STDIO Transport**        | Uses standard input/output streams for local process-to-process communication. No network overhead, optimal for local servers. |
| **Streamable HTTP Transport** | Uses HTTP POST for client-to-server messages, with optional Server-Sent Events (SSE) for streaming. Supports bearer tokens, API keys, custom headers, and OAuth. Ideal for remote servers. |

The transport layer abstracts communication details so that the same **JSON-RPC 2.0** message format works across all transports.

---

## 4. Statelessness & Discovery

MCP is a **stateless protocol**. Every request carries:
- The **protocol version** in its `_meta` field.
- The client's **capabilities and identity** in the `_meta` field.

Servers advertise their capabilities via the mandatory `server/discover` request. The discovery response is **cacheable** (`ttlMs` / `cacheScope` fields), so it does not need to be repeated on every request.

Discovery enables:
1. **Protocol Version Negotiation** – Client and server agree on a mutually supported version.
2. **Capability Discovery** – Each side learns which primitives the other supports.
3. **Identity Exchange** – Client/server identify themselves for debugging and compatibility.

---

## 5. Core Primitives Summary

| Primitive    | Direction      | Discovery Method   | Action Method    |
|---|---|---|---|
| Tools        | Server → Client | `tools/list`       | `tools/call`     |
| Resources    | Server → Client | `resources/list`   | `resources/read` |
| Prompts      | Server → Client | `prompts/list`     | `prompts/get`    |
| Elicitation  | Client → Server | N/A                | `elicitation/create` |

---

## 6. Key Design Principles

- **Stateless by design** – Each request is self-contained.
- **Transport-agnostic** – Same JSON-RPC 2.0 messages regardless of transport.
- **Composable** – A single host can connect to multiple servers simultaneously.
- **Dynamic** – Tool/resource lists can change at runtime; servers notify clients of changes.
- **Extensible** – Optional protocol extensions (e.g., Tasks) build on the core without breaking it.

---

*Summary generated from the official MCP Architecture Overview documentation.*
