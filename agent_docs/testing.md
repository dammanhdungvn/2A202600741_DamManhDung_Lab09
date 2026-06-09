# Testing Guidelines
- Use `python -m app.cli --question "..."` for manual isolated testing.
- Test edge cases: queries without required IDs, queries with non-existent IDs.
- Use `python -m app.cli --batch --test-file data/test.json` to verify the entire system.
- Always inspect the generated JSON trace files in `artifacts/traces/` to debug improper routing or failed tool calls.
