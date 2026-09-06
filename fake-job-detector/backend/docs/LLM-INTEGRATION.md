# SentinelJob AI — LLM Intelligence Layer & Provider Integration

## 1. Provider Architecture
The LLM intelligence layer uses an abstract factory pattern in `backend/app/llm/`:

- **Google Gemini Provider** (`app.llm.gemini_provider.GeminiLLMProvider`): Uses Gemini 1.5 Flash with structured response MIME type.
- **OpenAI Provider** (`app.llm.openai_provider.OpenAILLMProvider`): Uses GPT-4o-mini with `json_object` enforcement.
- **Anthropic Provider** (`app.llm.anthropic_provider.AnthropicLLMProvider`): Uses Claude 3.5 Sonnet.
- **Local Provider** (`app.llm.local_provider.LocalLLMProvider`): Connects to local Ollama / vLLM / OpenAI-compatible server at `http://localhost:11434/v1`.

---

## 2. Prompt Governance & Security Safeguards

### Versioning
- `SENTINELJOB_LLM_PROMPT_VERSION = "v1.0"`

### Anti-Prompt Injection Delimiters
All untrusted candidate inputs are wrapped inside explicit XML tags:
```xml
<UNTRUSTED_JOB_CONTENT>
[Sanitized job description text]
</UNTRUSTED_JOB_CONTENT>
```
System instructions mandate that instructions inside `<UNTRUSTED_JOB_CONTENT>` are treated as raw data and cannot alter evaluation rules or prompt directives.

---

## 3. Guaranteed Deterministic Fallback (`LLM_SYNTHESIS_UNAVAILABLE`)
If external LLM APIs timeout, fail authentication, or return invalid JSON, the orchestrator synthesizes an empirical fallback based on:
1. Triggered Rule Engine Indicators
2. Salary Benchmarking percentiles
3. 8-Layer Signal Stack metrics
4. ML probability distribution

The fallback sets:
```json
"uncertainty_statement": "LLM_SYNTHESIS_UNAVAILABLE: Synthesized via deterministic 8-layer forensic telemetry and ML probability calibration."
```
This guarantees the user receives a 100% complete, explainable report without crashes.
