# Code Patterns
- Use Python's `TypedDict` for the LangGraph state.
- Keep agent functions pure and state-driven.
- Wrap data access functions with `@tool` from Langchain.
- Use `app.utils.extract_json_payload` to safely parse LLM outputs.
- Prefer explicit state updates over hidden mutations.
