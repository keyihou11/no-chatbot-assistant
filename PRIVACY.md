# No-Chatbot Privacy Policy

## Data Collection and Usage

This extension collects and processes the following data:

### Code Analysis
- **What we collect**: Python code snippets containing detected issues
- **Why**: To generate AI-powered fix suggestions
- **Where it goes**: Your configured LLM provider's API servers
- **Retention**: Not stored permanently; processed in real-time only

### Telemetry
This MVP does **not** collect usage telemetry or analytics.

## Third-Party Services

### LLM API Providers
- Code snippets are sent to the LLM provider you configure (e.g., OpenAI, Anthropic, or Google)
- Subject to the provider's privacy policy:
  - **OpenAI**: [Privacy Policy](https://openai.com/privacy)
  - **Anthropic**: [Privacy Policy](https://www.anthropic.com/privacy)
  - **Google**: [Privacy Policy](https://policies.google.com/privacy)
- Providers may use data for service improvement (see their policies)

## User Control

### Opt-Out
- Disable auto-analysis: Set `no-chatbot.autoAnalyzeOnSave` to `false`
- Uninstall the extension to stop all data processing

### Manual Analysis
- Use `No-Chatbot: Analyze Current File` command for on-demand analysis only
- No automatic background processing when auto-analysis is disabled

## Data Security

- Communication with backend uses HTTP (HTTPS recommended for production)
- API keys stored in local `.env` file (not transmitted)
- No code is logged or persisted by the backend

## Recommendations

⚠️ **Do not use this extension on:**
- Proprietary or confidential code
- Code containing secrets, credentials, or PII
- Production systems without approval

✅ **Safe to use on:**
- Personal learning projects
- Open-source code
- Educational assignments

## Updates

This privacy policy may be updated. Check the repository for the latest version.

## Contact

For privacy concerns, contact: [Your Email]

Last updated: 2024-11-23
