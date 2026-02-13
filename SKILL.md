---
name: mem0-memory-layer
description: |
  Mem0 — Universal Memory Layer for AI Agents with Cross-Session Context

  What this skill does: Enables persistent memory across agent sessions, tracks user preferences,
  and provides automatic memory management for personalized AI interactions. Integrates with our
  governance checkpoint system to create a hybrid memory architecture (structured checkpoints +
  semantic memory).

  When to use it:
  - When the user says "remember this", "save this preference", "recall what we discussed"
  - For agents that need to learn user preferences over time
  - When building customer support bots that need conversation history
  - For multi-session workflows requiring context from previous work
  - When agent teams need shared memory across teammates
  - For personalized AI assistants that adapt to user behavior
  - When implementing recursive learning protocols with memory persistence

  What it requires:
  - Docker (for OpenMemory MCP server)
  - OpenAI API key (for memory processing with LLM)
  - OR Python 3.9+ with mem0ai package (for SDK approach)

  Research Highlights: +26% accuracy over OpenAI Memory, 91% faster responses, 90% lower token usage.
---

# Mem0 — Universal Memory Layer

Mem0 is a production-ready memory layer for AI agents with 47K+ GitHub stars. It provides persistent,
intelligent memory across sessions, enabling agents to remember user preferences, adapt to individual
needs, and continuously learn over time—without manually managing context windows.

## Purpose

Solves the problem of context loss between agent sessions. Traditional agents forget everything when
the session ends; Mem0 provides multi-level memory (User, Session, Agent) that persists across
conversations, making AI interactions truly personalized and context-aware.

---

## Process

### Step 1: Choose Your Integration Path

**Option A: OpenMemory MCP Server (Recommended for Claude Code)**
- Local-first, privacy-focused
- Runs as MCP server with UI dashboard
- Memories stored locally in Docker containers
- Best for development and personal use

**Option B: Mem0 Platform (Hosted)**
- Fully managed service at app.mem0.ai
- Automatic updates, analytics, enterprise security
- Best for production deployments

**Option C: Python SDK (Self-Hosted)**
- Direct SDK integration in Python projects
- Full control over storage backend
- Best for custom integrations

For this governance integration, use **Option A (OpenMemory MCP)**.

---

### Step 2: Set Up OpenMemory MCP Server

#### Quick Setup (One Command)

```bash
curl -sL https://raw.githubusercontent.com/mem0ai/mem0/main/openmemory/run.sh | bash
```

Ensure `OPENAI_API_KEY` is set globally:
```bash
export OPENAI_API_KEY=your_api_key
```

#### Manual Setup (More Control)

1. **Clone and configure:**
   ```bash
   cd ~/governance-ref/skills/mem0/openmemory
   cp api/.env.example api/.env
   cp ui/.env.example ui/.env
   ```

2. **Edit `api/.env`:**
   ```env
   OPENAI_API_KEY=sk-xxx
   USER=claude-agent  # Default user ID for memories
   ```

3. **Edit `ui/.env`:**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8765
   NEXT_PUBLIC_USER_ID=claude-agent
   ```

4. **Build and run:**
   ```bash
   make build  # Builds MCP server and UI
   make up     # Runs OpenMemory (MCP at :8765, UI at :3000)
   ```

After setup:
- MCP Server: http://localhost:8765
- API Docs: http://localhost:8765/docs
- UI Dashboard: http://localhost:3000

---

### Step 3: Configure Claude Code MCP Integration

Add OpenMemory to your Claude Code MCP config:

**Location:** `~/.claude/mcp.json` (or your Claude config location)

```json
{
  "mcpServers": {
    "openmemory": {
      "command": "npx",
      "args": [
        "@openmemory/install",
        "local",
        "http://localhost:8765/mcp/claude/sse/claude-agent",
        "--client",
        "claude"
      ]
    }
  }
}
```

Or use the one-step installer:
```bash
npx @openmemory/install local http://localhost:8765/mcp/claude/sse/claude-agent --client claude
```

Replace `claude-agent` with your preferred user ID (must match `api/.env`).

---

### Step 4: Use Memory in Agent Workflows

#### Core Operations

**Add Memory:**
```python
from mem0 import Memory

memory = Memory()

# Store conversation context
messages = [
    {"role": "user", "content": "I prefer React over Vue"},
    {"role": "assistant", "content": "Noted! I'll recommend React for frontend."}
]
memory.add(messages, user_id="claude-agent")

# Store explicit facts
memory.add(
    "User prefers TypeScript strict mode enabled",
    user_id="claude-agent"
)
```

**Retrieve Memory:**
```python
# Search for relevant memories
results = memory.search(
    query="What are the user's frontend preferences?",
    user_id="claude-agent",
    limit=5
)

for result in results["results"]:
    print(f"- {result['memory']}")
```

**Get All Memories:**
```python
all_memories = memory.get_all(user_id="claude-agent")
```

**Update Memory:**
```python
memory.update(
    memory_id="mem_abc123",
    data="User now prefers Svelte over React"
)
```

**Delete Memory:**
```python
memory.delete(memory_id="mem_abc123")
```

#### Agent Integration Pattern

```python
from openai import OpenAI
from mem0 import Memory

openai_client = OpenAI()
memory = Memory()

def agent_with_memory(message: str, user_id: str = "claude-agent") -> str:
    # 1. Retrieve relevant memories
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(f"- {m['memory']}" for m in relevant_memories["results"])

    # 2. Build system prompt with memories
    system_prompt = f"""You are Claude, a helpful AI agent.

Previous context about this user:
{memories_str}

Use this context to provide personalized responses."""

    # 3. Generate response
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    assistant_response = response.choices[0].message.content

    # 4. Store new memories from conversation
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response
```

---

### Step 5: Integrate with Governance Checkpoint System

Mem0 complements our checkpoint system with different memory types:

**Checkpoint System (Structured):**
- Session goal, branch, changes summary
- Files modified, decisions made
- Next steps, blockers
- Written explicitly at checkpoints

**Mem0 (Semantic):**
- User preferences learned over time
- Cross-session patterns and insights
- Implicit knowledge from conversations
- Retrieved automatically via semantic search

**Hybrid Pattern:**

```python
def governance_checkpoint_with_memory(checkpoint_data: dict, user_id: str):
    """
    Writes structured checkpoint + stores semantic memories
    """
    # 1. Write traditional checkpoint files
    write_checkpoint_files(checkpoint_data)

    # 2. Extract learnable patterns for Mem0
    learnings = extract_semantic_learnings(checkpoint_data)

    # 3. Store in Mem0 for cross-session retrieval
    for learning in learnings:
        memory.add(learning, user_id=user_id, metadata={
            "type": "checkpoint_learning",
            "checkpoint_id": checkpoint_data["checkpoint_id"],
            "timestamp": checkpoint_data["timestamp"]
        })

def extract_semantic_learnings(checkpoint_data: dict) -> list[str]:
    """
    Examples of learnings to store:
    - "User prefers feature branches named: sandbox/YYYY-MM-DD-description"
    - "Project uses Wouter for routing, not react-router-dom"
    - "Always run tsc --noEmit after TypeScript changes"
    - "User's testing preference: Vitest over Jest"
    """
    learnings = []

    # Extract from decisions
    for decision in checkpoint_data.get("decisions_made", []):
        learnings.append(f"Decision pattern: {decision}")

    # Extract from blockers (anti-patterns)
    for blocker in checkpoint_data.get("blockers", []):
        learnings.append(f"Avoid: {blocker}")

    return learnings
```

**Retrieval Pattern:**

```python
def start_session_with_context(user_id: str):
    """
    Combines checkpoint recovery + Mem0 memory retrieval
    """
    # 1. Check for handoff checkpoint (explicit)
    if exists(".agent/HANDOFF.md"):
        checkpoint = read_checkpoint()
        resume_from_checkpoint(checkpoint)

    # 2. Retrieve cross-session memories (implicit)
    session_memories = memory.search(
        query="What are this user's coding preferences and patterns?",
        user_id=user_id,
        limit=10
    )

    # 3. Combine both contexts
    context = {
        "checkpoint": checkpoint if checkpoint else None,
        "preferences": [m["memory"] for m in session_memories["results"]]
    }

    return context
```

---

## Core Capabilities

### 1. Memory Storage

**Multi-Level Memory:**
- **User-level**: Persists across all sessions for a user (preferences, learned patterns)
- **Session-level**: Specific to a conversation thread (temporary context)
- **Agent-level**: Shared across agent instances (team knowledge base)

**Storage Backends:**
- Default: In-memory (for quick testing)
- Production: PostgreSQL, Qdrant, Pinecone, ChromaDB, Weaviate
- OpenMemory: Local Docker containers

### 2. Memory Retrieval

**Semantic Search:**
```python
# Finds memories semantically related to query
results = memory.search(
    query="frontend framework preferences",
    user_id="claude-agent",
    limit=5
)
```

**Filter by Metadata:**
```python
results = memory.search(
    query="typescript config",
    user_id="claude-agent",
    filters={"category": "build_config"}
)
```

### 3. Preference Learning

Mem0 automatically extracts preferences from conversations:
- Coding style preferences (tabs vs spaces, naming conventions)
- Technology stack choices (React vs Vue, TypeScript vs JavaScript)
- Workflow patterns (git flow, testing approach, review style)
- Project-specific rules (API patterns, file structure)

### 4. Cross-Session Context

**Problem Solved:**
Traditional checkpoints require manual recovery. Mem0 automatically surfaces relevant
context when you start a new session.

**Example Flow:**
```
Session 1: User mentions "I prefer TypeScript strict mode"
→ Mem0 stores: "User prefers TypeScript strict mode enabled"

Session 2: User asks "Set up a new React project"
→ Mem0 retrieves: "User prefers TypeScript strict mode enabled"
→ Agent automatically configures tsconfig.json with strict mode
```

---

## Usage Patterns

### Pattern 1: Personal Coding Assistant

Store user preferences as you learn them:
```python
# During code review
memory.add(
    "User's code review focus: security, performance, then style",
    user_id="claude-agent"
)

# During next session
memories = memory.search(
    query="code review priorities",
    user_id="claude-agent"
)
# Returns: "security, performance, then style"
```

### Pattern 2: Agent Team Shared Memory

Share knowledge across teammates:
```python
# Team lead learns a pattern
memory.add(
    "Project uses centralized API wrapper at src/api.ts, never use raw fetch()",
    user_id="team-shared"
)

# Backend agent retrieves team knowledge
team_context = memory.search(
    query="API call patterns",
    user_id="team-shared"
)
```

### Pattern 3: Recursive Learning Loop

Combine with governance checkpoints:
```python
def checkpoint_with_learning(checkpoint_data: dict):
    # 1. Write structured checkpoint
    write_checkpoint_files(checkpoint_data)

    # 2. Extract patterns from decisions
    for decision in checkpoint_data["decisions_made"]:
        memory.add(
            f"Pattern learned: {decision}",
            user_id="claude-agent",
            metadata={"checkpoint_id": checkpoint_data["checkpoint_id"]}
        )

    # 3. Next session retrieves these automatically
```

### Pattern 4: Project-Specific Context

Store project rules in Mem0:
```python
# Bootstrap new agent on project
project_memories = [
    "Project uses Wouter for routing, not react-router-dom",
    "Database is PostgreSQL on Railway, not local",
    "Always run npx tsc --noEmit after TypeScript changes",
    "Testing framework: Vitest (check package.json first)"
]

for rule in project_memories:
    memory.add(rule, user_id="project-governance-v3")
```

---

## Guard Rails

**Safety Rules:**
- NEVER store sensitive data (API keys, passwords, tokens) in Mem0
- NEVER delete all memories without explicit user confirmation
- ALWAYS validate user_id is consistent across session
- ALWAYS check if OpenMemory server is running before memory operations
- If memory retrieval fails, gracefully continue without memories (don't block execution)

**Privacy Rules:**
- Memories are user-scoped (user_id required for all operations)
- OpenMemory data lives locally (Docker volumes), never sent to Mem0 cloud
- For production, review Mem0 Platform's data retention policies

**Performance Rules:**
- Limit memory search results (default: 3-5 per query)
- Use filters to narrow semantic search scope
- Cache frequently accessed memories in session state

---

## Output Format

**When storing memories:**
```
✓ Stored 3 memories for user: claude-agent
  - "User prefers TypeScript strict mode"
  - "Project uses Wouter for routing"
  - "Testing framework: Vitest"

Memory IDs:
  - mem_abc123
  - mem_def456
  - mem_ghi789
```

**When retrieving memories:**
```
📚 Retrieved 5 relevant memories:

1. [Score: 0.92] User prefers TypeScript strict mode enabled
2. [Score: 0.87] Project uses Wouter for routing, not react-router-dom
3. [Score: 0.81] Always run tsc --noEmit after TypeScript changes
4. [Score: 0.76] Testing framework: Vitest (check package.json)
5. [Score: 0.72] Git workflow: feature branches from main

Applied to current task: Setting up new React component with TypeScript strict mode.
```

---

## Integration

**Related Skills:**
- `/checkpoint` — Stores structured session state; Mem0 stores semantic learnings
- `/bootstrap-project` — Use Mem0 to retrieve user's project preferences during setup
- `/build-mvp` — Mem0 surfaces learned patterns from previous MVPs

**Governance Dependencies:**
- Complements checkpoint system (structured + semantic memory)
- Enhances recursive learning protocol with cross-session context
- Integrates with agent teams via shared user_id (`team-shared`)

**Triggers From:**
- User explicitly says "remember this" → store in Mem0
- Agent makes a decision → extract pattern, store in Mem0
- Checkpoint written → extract learnings, store in Mem0

**Triggers To:**
- Session start → retrieve Mem0 memories for context
- Agent spawned → load team-shared memories
- User asks about preferences → query Mem0

---

## Notes

**Current Limitations:**
- OpenMemory MCP requires Docker (not portable to non-Docker environments)
- Default LLM is OpenAI (gpt-4.1-nano) — requires API key even for local storage
- Memory extraction quality depends on LLM prompt engineering

**Future Enhancements:**
- Auto-checkpoint memory sync: write Mem0 memories at every checkpoint
- Memory dashboard skill: `/memory-review` to audit and curate stored memories
- Team memory inheritance: new teammates auto-inherit team-shared memories
- Memory decay: auto-archive stale memories after N days

**Production Checklist:**
- [ ] Choose backend: OpenMemory (local) vs Mem0 Platform (hosted)
- [ ] Configure user_id strategy (per-user vs per-project vs team-shared)
- [ ] Set up memory retention policies (how long to keep memories)
- [ ] Implement memory review workflow (periodic human curation)
- [ ] Monitor memory retrieval accuracy (are memories actually useful?)

**Research Paper:**
If implementing advanced memory architectures, cite the Mem0 research:
```
Chhikara, P., Khant, D., Aryan, S., Singh, T., & Yadav, D. (2025).
Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory.
arXiv preprint arXiv:2504.19413.
```

---

## Quick Reference

**Start OpenMemory:**
```bash
cd ~/governance-ref/skills/mem0/openmemory
make up
```

**Stop OpenMemory:**
```bash
cd ~/governance-ref/skills/mem0/openmemory
make down
```

**View Memories (UI):**
```
http://localhost:3000
```

**API Docs:**
```
http://localhost:8765/docs
```

**Install MCP Client:**
```bash
npx @openmemory/install local http://localhost:8765/mcp/claude/sse/<user-id> --client claude
```

**Python SDK Quick Start:**
```bash
pip install mem0ai
```
```python
from mem0 import Memory
memory = Memory()
memory.add("Your memory here", user_id="claude-agent")
results = memory.search("query", user_id="claude-agent")
```
