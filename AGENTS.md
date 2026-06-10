# Vibe-Coding Master Plan: Multi-Agent Shopping Assistant

## Project Overview
- **Name:** Multi-Agent Shopping Assistant
- **Goal:** Build an intelligent online shopping assistant using LangGraph to route queries, perform RAG on policies, and look up JSON mock data.
- **Stack:** Python 3.11+, LangGraph, Chroma DB, `sentence-transformers`, Custom LLM (`langchain-openai`).
- **Current Phase:** Phase 1 (Setup & Data Access)

## How I Should Think
1. **Understand:** Read the requirements and current phase goals before writing code.
2. **Ask:** If IDs are missing or requirements are vague, return `clarification_needed`. 
3. **Plan:** Follow the sequential phases strictly. Test one component before moving to the next.
4. **Verify:** Check trace JSON files to ensure tools are called properly and routing is accurate.
5. **Explain:** Provide concise updates and link to relevant logs or code files.

## Workflow: Plan -> Execute -> Verify
1. **Plan:** Review the checklist for the current phase.
2. **Execute:** Write code, focusing on robust tool definitions, clean markdown chunking, and accurate LangGraph edge conditions.
3. **Verify:** Run CLI tests (single query and batch) and verify output formats strictly adhere to `Success`, `Clarification`, or `Not found`.

## Context Files
- **Project Brief:** `agent_docs/project_brief.md`
- **Product Requirements:** `agent_docs/product_requirements.md`
- **Tech Stack:** `agent_docs/tech_stack.md`
- **Code Patterns:** `agent_docs/code_patterns.md`
- **Testing:** `agent_docs/testing.md`
- **PRD:** `docs/PRD.md`
- **Technical Design:** `docs/TechDesign-ShoppingAssistant-MVP.md`

## Roadmap
- [x] **Phase 1:** Setup & Data Access (Worker 2)
- [x] **Phase 2:** RAG Engine (Worker 1)
- [x] **Phase 3:** Prompt Engineering
- [ ] **Phase 4:** Graph Orchestration
- [ ] **Phase 5:** CLI Integration & Single Testing
- [ ] **Phase 6:** Batch Processing & Traceability

## What NOT To Do
- DO NOT use an LLM provider other than the custom one defined in `.env`.
- DO NOT hallucinate IDs; if missing, ask for clarification.
- DO NOT build one monolithic tool for Data Worker; keep them as 4 distinct tools.
- DO NOT modify the `data/policy_mock_vi.md` or `data/order_customer_mock_data.json` mock files.
