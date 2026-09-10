# KARYA MCP

The `mcp` directory contains Model Context Protocol integrations for KARYA.

## What is MCP?

MCP provides a standardized interface through which AI systems can interact with tools and external context.

In KARYA, MCP helps connect AI agents to controlled enterprise capabilities.

---

## Architecture

```text
KARYA Agent
     │
     ▼
    MCP
     │
 ┌───┼───────────────┐
 ▼   ▼               ▼
API DB              Tools
 │   │               │
 └───┴───────────────┘
          │
          ▼
   Controlled Action
```

---

## Use Cases

MCP can be used to connect:

* Internal APIs
* Enterprise databases
* File systems
* Business tools
* Industrial systems
* Search services
* Automation systems

---

## Security

MCP tools should never be treated as unrestricted access.

Every tool should have:

* Explicit permissions
* Input validation
* Authentication
* Authorization
* Logging
* Controlled execution
* Failure handling

The goal is:

> **Give agents capabilities without giving them uncontrolled access.**
