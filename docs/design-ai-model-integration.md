# AI Model Integration

## Rationale
The skeleton currently stubs out `AIModel` with a print statement. The next step
is to integrate a real model so brainstorming components can produce useful
results. OpenAI's API is a convenient default because it is widely available and
easy to mock in tests.

## Approach
- Implement `AIModel` in `src/crucible/ai.py` using the `openai` package.
- API key is read from ``OPENAI_API_KEY`` unless explicitly provided.
- `query()` sends the prompt to `ChatCompletion.create` and returns the
  assistant message text.
- The dependency is optional; if `openai` is not installed a clear
  `RuntimeError` is raised.
- Tests mock the `openai` module to avoid network calls.

## Alternatives Considered
- Supporting multiple providers via a plugin system. Premature for the current
  scope.
- Using command line flags or config files for API settings. Environment
  variables keep things simple for now.

## Risks
- API failures or rate limits could break the CLI; higher levels should handle
  exceptions gracefully (future work).
