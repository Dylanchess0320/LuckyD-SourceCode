# Configuration

## Environment Variables

LuckyD Code is configured via environment variables, typically set in a `.env` file.

### Provider Configuration

Choose **one** provider by setting its API key:

=== "DeepSeek (Default)"

    ```env
    DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

=== "OpenAI"

    ```env
    OPENAI_API_KEY=sk-your-openai-key
    OPENAI_MODEL=gpt-4o
    OPENAI_BASE_URL=https://api.openai.com/v1
    ```

=== "Anthropic"

    ```env
    ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
    ANTHROPIC_MODEL=claude-sonnet-4-20250514
    ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
    ```

=== "Google Gemini"

    ```env
    GOOGLE_API_KEY=your-google-api-key
    GOOGLE_MODEL=gemini-2.0-flash
    GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta
    ```

=== "Ollama (Local)"

    ```env
    OLLAMA_MODEL=codellama
    OLLAMA_HOST=http://localhost:11434
    ```

### Global Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `CODING_AGENT_PROVIDER` | auto-detect | Explicit provider: `deepseek`, `openai`, `anthropic`, `google`, `ollama` |
| `CODING_AGENT_MODEL` | `auto` | Model override (`auto`, `flash`, `pro`, or specific name) |
| `CODING_AGENT_THINKING` | `false` | Enable reasoning/thinking mode |
| `CODING_AGENT_TEMP` | `0.0` | Temperature for LLM responses |
| `CODING_AGENT_MAX_TOKENS` | `8192` | Maximum tokens per response |
| `CODING_AGENT_MAX_TURNS` | `30` | Maximum conversation turns |
| `CODING_AGENT_TIMEOUT` | `120` | API timeout in seconds |
| `CODING_AGENT_LOG_LEVEL` | `INFO` | Logging level |
| `CODING_AGENT_LOG_FORMAT` | `readable` | Log format (`readable` or `json`) |

## CLI Arguments

| Argument | Description |
|----------|-------------|
| `--model NAME` | Model: `auto` (default), `flash`, `pro`, or specific name |
| `--thinking` | Use reasoning/thinking mode |
| `--temp FLOAT` | Temperature (default: 0.0) |
| `--help` | Show help message |

## Model Auto-Detection

When `CODING_AGENT_MODEL=auto`, the agent fetches available models from your
provider's API and selects the best one. The result is cached for 24 hours.
Use `/refresh` in the REPL to force re-fetch.
