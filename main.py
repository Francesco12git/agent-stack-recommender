from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json

app = FastAPI(title="Agent Stack Recommender")

# Knowledge base of agent frameworks and protocols
STACK_DB = {
    "orchestration": [
        {
            "name": "LangGraph",
            "type": "framework",
            "best_for": ["complex workflows", "stateful agents", "production systems"],
            "maturity": "high",
            "language": "Python",
            "note": "Most popular orchestration framework. ~400 companies in production. Graph-based execution model."
        },
        {
            "name": "CrewAI",
            "type": "framework",
            "best_for": ["role-based agents", "team simulation", "quick prototypes"],
            "maturity": "medium",
            "note": "Great for multi-agent role play. May hit scaling walls after 6-12 months."
        },
        {
            "name": "OpenAI Agents SDK",
            "type": "framework",
            "best_for": ["simple agents", "minimal setup", "handoff patterns"],
            "maturity": "medium",
            "language": "Python",
            "note": "Minimalist: 4 primitives (agents, handoffs, guardrails, sessions)."
        },
        {
            "name": "Google ADK",
            "type": "framework",
            "best_for": ["google ecosystem", "enterprise", "multimodal"],
            "maturity": "early",
            "note": "Powers Google Agentspace internally. Early for external use."
        }
    ],
    "communication": [
        {
            "name": "MCP (Model Context Protocol)",
            "type": "protocol",
            "best_for": ["tool integration", "agent-to-tool communication", "context injection"],
            "maturity": "high",
            "note": "Created by Anthropic. De facto standard for connecting agents to tools and data."
        },
        {
            "name": "A2A (Agent-to-Agent)",
            "type": "protocol",
            "best_for": ["multi-agent communication", "task delegation", "agent discovery"],
            "maturity": "medium",
            "note": "Created by Google. Standard for agent-to-agent collaboration. Under Linux Foundation."
        },
        {
            "name": "ACP (Agent Communication Protocol)",
            "type": "protocol",
            "best_for": ["lightweight messaging", "local agent communication"],
            "maturity": "early",
            "note": "Merged into A2A ecosystem via IBM contribution."
        }
    ],
    "memory": [
        {
            "name": "Mem0",
            "type": "infrastructure",
            "best_for": ["persistent memory", "user preferences", "long-term context"],
            "maturity": "medium",
            "note": "Open-source memory layer for AI agents. Stores and retrieves across sessions."
        },
        {
            "name": "Zep",
            "type": "infrastructure",
            "best_for": ["conversation history", "entity extraction", "session memory"],
            "maturity": "medium",
            "note": "Long-term memory for AI assistants. Auto-extracts entities and summaries."
        },
        {
            "name": "LangMem",
            "type": "infrastructure",
            "best_for": ["langchain integration", "memory management"],
            "maturity": "early",
            "note": "Memory system designed for LangChain/LangGraph pipelines."
        }
    ],
    "observability": [
        {
            "name": "LangSmith",
            "type": "platform",
            "best_for": ["tracing", "evaluation", "debugging agent runs"],
            "maturity": "high",
            "note": "Leading observability platform. Multi-turn evaluation, failure categorization."
        },
        {
            "name": "Arize Phoenix",
            "type": "platform",
            "best_for": ["open-source tracing", "OpenTelemetry", "production monitoring"],
            "maturity": "medium",
            "note": "Open-source, built on OpenTelemetry/OpenInference standards."
        },
        {
            "name": "Braintrust",
            "type": "platform",
            "best_for": ["CI/CD evaluation", "experiment tracking", "pull request gates"],
            "maturity": "medium",
            "note": "Most CI/CD-native. Used by Notion, Stripe, Zapier."
        },
        {
            "name": "Langfuse",
            "type": "platform",
            "best_for": ["open-source observability", "cost tracking", "prompt management"],
            "maturity": "medium",
            "note": "Acquired by ClickHouse in early 2026. Validates AI observability as core infra."
        }
    ],
    "execution": [
        {
            "name": "E2B",
            "type": "infrastructure",
            "best_for": ["code sandboxing", "safe execution", "agent code running"],
            "maturity": "medium",
            "note": "Cloud sandboxes for AI agents to safely execute code."
        },
        {
            "name": "OpenClaw",
            "type": "framework",
            "best_for": ["personal agents", "always-on agents", "multi-channel messaging"],
            "maturity": "early",
            "note": "Open-source, local-first. Persistent memory as Markdown. Heartbeat scheduler."
        },
        {
            "name": "Amazon Bedrock AgentCore",
            "type": "platform",
            "best_for": ["enterprise deployment", "framework-agnostic hosting", "policy enforcement"],
            "maturity": "high",
            "note": "Managed platform. Runs LangGraph, CrewAI, Google ADK, or OpenAI Agents SDK."
        }
    ]
}

# Keywords mapped to categories
KEYWORD_MAP = {
    "orchestration": ["orchestrat", "workflow", "pipeline", "chain", "graph", "coordinate"],
    "communication": ["communicat", "protocol", "mcp", "a2a", "multi-agent", "message", "discover"],
    "memory": ["memory", "remember", "context", "persist", "history", "long-term", "session"],
    "observability": ["observ", "trace", "eval", "debug", "monitor", "log", "test"],
    "execution": ["execut", "sandbox", "run code", "deploy", "host", "runtime", "personal agent"]
}


def match_categories(use_case: str) -> list[str]:
    use_case_lower = use_case.lower()
    scores = {}
    for category, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in use_case_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return ["orchestration", "communication"]

    sorted_cats = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    return sorted_cats[:3]


@app.get("/recommend")
def recommend(use_case: str = Query(..., description="Describe your agent use case in plain English")):
    categories = match_categories(use_case)

    recommendations = []
    for cat in categories:
        tools = STACK_DB.get(cat, [])
        recommendations.append({
            "category": cat,
            "tools": tools[:3]
        })

    return {
        "use_case": use_case,
        "matched_categories": categories,
        "recommendations": recommendations,
        "total_tools_suggested": sum(len(r["tools"]) for r in recommendations)
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
