# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [2.1.0] - 2026-07-22

### Added
- `core/agent_loop.py` — modular CodingAgent using `core/llm_client.py`
- 30+ new pytest tests covering agent, memory, core modules, and tools
- `test_agent.py` — live agent tests with mocked LLM client
- `test_memory.py` — memory store, graph, persistence tests
- `test_core_modules.py` — message builder, context manager, hooks, checkpoint
- `test_modular_agent.py` — modular agent init, run loop, error handling
- `test_tools.py` — file tools, bash tool, registry tests

### Changed
- `agent.py` rewritten as backward-compatibility shim re-exporting `core.agent_loop.CodingAgent`
- `LLMResult` now has `get()` and `to_dict()` for dict-like interface compatibility
- `MemoryGraph.summarize()` implemented (was missing)
- `core/agent_loop.py` — fixed parameter names (`on_token`/`on_think`), added `_emit_event()`, added `try/except` around `chat_stream`

### Fixed
- SyntaxError: stray `]` in `logging_setup.py`
- `ProjectDetector().detect()` throwing `AttributeError` (missing `_detect_package_manager`)
- `toml` hard dependency in `config.py` — now falls back to JSON if `pyproject.toml` missing
- All Python files now parse cleanly (verified with `ast.parse` sweep)

### Security
- No real API keys or network calls in test suite (all mocked)
- Sensitive keys redacted in logs

---


## [2.0.0] - 2026-07-22

### Added
- Complete project infrastructure overhaul
- `pyproject.toml` with Ruff, Black, Mypy, pytest config
- `setup.py` for pip-installable package
- `requirements.txt` and `requirements-dev.txt` with pinned dependencies
- `Makefile` with 30+ commands (test, lint, format, security, docker, etc.)
- `.pre-commit-config.yaml` with 15+ automated checks
- `.editorconfig` for consistent editor settings
- `.github/workflows/ci.yml` — full CI/CD pipeline with 5 job stages
- `Dockerfile` — multi-stage build (builder → slim runtime)
- `docker-compose.yml` with optional Ollama and Redis services
- `logging_setup.py` — structured JSON logging with redaction and timing
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- `docs/` directory — MkDocs-based documentation site
- Test directory structure with conftest.py and async fixtures
- `.env.example` template with all providers documented
- `.dockerignore` for lean images

### Changed
- Enhanced `.gitignore` to cover all build artifacts and secrets
- Project version bumped from 1.3.6 → 2.0.0

### Fixed
- [List fixed issues]

### Security
- Added dependency scanning (Safety) to CI
- Bandit security scanning in CI pipeline
- Sensitive data redaction in logging
- Pre-commit hooks for detecting private keys

## [1.3.6] - 2026-07-XX

### Added
- Initial public release
- Multi-provider LLM support (DeepSeek, OpenAI, Anthropic, Google, Ollama)
- 20+ coding tools
- Memory graph with BM25 search and ONNX embeddings
- VS Code extension integration
- Web chat interface
- Project intelligence engine
