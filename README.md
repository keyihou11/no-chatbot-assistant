# No-Chatbot Programming Assistant 🤖

⚠️ **Experimental Preview**: This is an early-stage MVP. Expect rough edges, occasional patch failures, and limited language coverage (currently Python-focused). Use on non-sensitive code, keep a backup or version control handy, and please file issues with repro steps if you hit problems.

> **✅ MVP Complete** - A fully functional event-driven AI coding assistant ready for testing and research

An innovative VS Code extension that proactively suggests code fixes without chatbot conversations. Instead of typing prompts, No-Chatbot automatically detects issues on save and presents AI-powered fixes through native VS Code quick actions.

## 🎯 What is No-Chatbot?

No-Chatbot represents a **new paradigm** for AI coding assistants, eliminating the need for lengthy chat interactions. The workflow is simple and seamless:

- 🎯 **Automatically detects** code issues when you save Python files
- 🤖 **Generates AI-powered fixes** using state-of-the-art LLMs from leading providers
- 💡 **Shows quick actions** directly in your editor with detailed explanations and risk assessments
- ↩️ **Supports one-click undo** with full state restoration for safety
- ⚡ **Smart patch application** using content-based matching (not just line numbers)

## 📋 MVP Features

### ✅ Core Functionality (Complete)

- **Event-Driven Analysis** - Automatic code analysis triggered on file save (30-60 second response time)
- **Static Code Analysis** - Pylint integration focused on logic issues (format rules disabled for better signal)
- **Multi-LLM Support** - Choose from OpenAI, Anthropic, or Google (bring your own model + API key)
- **AI-Powered Fixes** - Detailed fix suggestions with:
  - Clear title and description
  - Unified diff format patches
  - Risk assessment and warnings
- **Smart Patch Application** - Content-based matching system that:
  - Finds correct lines by content (not just line numbers)
  - Handles line number drift (±5 line tolerance)
  - Supports delete, insert, and replace operations
  - Preserves original indentation
- **Native Code Actions UI** - Seamless integration with VS Code's quick fix interface
- **Full Undo Support** - One-click rollback with complete state restoration

## 🤖 Supported LLM Providers

No-Chatbot supports three major LLM providers with flexible model choices:

| Provider      | Notes                                      | Cost      |
| ------------- | ------------------------------------------ | --------- |
| **Anthropic** | Strong reasoning and code understanding    | $$        |
| **OpenAI**    | General-purpose models with broad coverage | $$-$$$    |
| **Google**    | Fast, cost-effective options (free tiers)  | $ (Free*) |


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- VS Code 1.80+
- API key from one of: OpenAI, Anthropic, or Google

### 1. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env and configure your LLM provider (see below)
```

### 2. Configure LLM Provider

Edit `.env` file and choose your provider:

**Option A: Use Anthropic**
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
# Optional: override default model
# ANTHROPIC_MODEL=your-anthropic-model
```

**Option B: Use OpenAI**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
# Optional: override default model
# OPENAI_MODEL=your-openai-model
```

**Option C: Use Google**
```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=AIza-your-key-here
# Optional: override default model
# GOOGLE_MODEL=your-google-model
```

### 2. Start Backend Server

```bash
# Make sure you're in the backend directory with venv activated
python main.py
```

The server will start on `http://localhost:8000`

### 3. Setup Extension

```bash
# Navigate to extension directory
cd extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile
```

### 4. Run Extension in VS Code

1. Open this workspace in VS Code
2. Press `F5` to launch Extension Development Host
3. Open a Python file
4. Save the file to trigger analysis

## 📖 Usage

### Quick Start Workflow

1. **Start the backend server** (in terminal):
   ```bash
   cd backend
   python main.py
   # Server starts on http://localhost:8000
   ```

2. **Launch the extension** (in VS Code):
   - Press `F5` to open Extension Development Host
   - Or install the packaged `.vsix` file

3. **Test it out**:
   - Open or create a Python file with some issues (e.g., unused variables)
   - Save the file (`Cmd+S` / `Ctrl+S`)
   - Wait for "No-Chatbot analyzing..." notification (30-60 seconds)
   - Issues appear with 💡 light bulb icons

### Applying AI Fixes

1. **View available fixes**:
   - Click on a line with an issue (yellow/red squiggle)
   - Click the 💡 light bulb icon that appears
   - Or press `Cmd+.` (Mac) / `Ctrl+.` (Windows/Linux)

2. **Review the fix**:
   - Read the fix title and detailed description
   - Check the risk assessment
   - Preview the code changes (shown as a diff)

3. **Apply the fix**:
   - Click "Apply" to accept the fix
   - The code updates automatically
   - File is saved automatically

### Undo a Fix

If you're not satisfied with a fix:
- Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
- Run: `No-Chatbot: Undo Last Fix`
- Or use standard VS Code undo (`Cmd+Z` / `Ctrl+Z`)

### Manual Analysis

You can also trigger analysis manually:
- Command Palette → `No-Chatbot: Analyze Current File`
- Useful when `autoAnalyzeOnSave` is disabled

### Tips for Best Results

- **Start with simple files** - Test on files with obvious issues first
- **Review each fix** - Don't blindly apply all suggestions
- **Check the risks** - AI-generated fixes may have edge cases
- **Test after applying** - Run your tests to ensure nothing broke
- **Use different LLMs** - Experiment with providers to balance quality, speed, and cost

## 💡 Key Innovation: Smart Patch Application

One of the major technical achievements of No-Chatbot is its **content-based patch application system**, which overcomes a common limitation of AI-generated code fixes.

### The Problem

Traditional patch application relies on absolute line numbers:
- **Issue**: Line numbers in AI-generated patches may be inaccurate
- **Cause**: File edits between analysis and application, LLM estimation errors
- **Result**: Fixes applied to wrong lines, causing bugs or crashes

### Our Solution

No-Chatbot uses **intelligent content matching** instead:

```typescript
// 1. Extract the content to modify from the patch
targetContent = "x = 10"  // From AI-generated diff

// 2. Search for matching line near the hinted position
lineNumber = findLineContaining(document, "x = 10", lineHint=24, tolerance=5)

// 3. Apply the fix at the correct location
if (lineNumber !== -1) {
    applyPatch(lineNumber)
}
```

### Benefits

- ✅ **Robust to line drift** - Handles ±5 line offset from hint
- ✅ **Content verification** - Ensures we're modifying the right code
- ✅ **Handles imperfect AI** - Works even when LLM provides wrong line numbers
- ✅ **Preserves indentation** - Maintains code formatting
- ✅ **Multiple operations** - Supports delete, insert, and replace

This makes No-Chatbot significantly more reliable than naive line-based patching systems.


## 🏗️ Architecture

```
┌─────────────────────┐
│  VS Code Extension  │
│  (TypeScript)       │
│  - Save Handler     │
│  - Code Actions     │
│  - Backend Client   │
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (Python)           │
│  - Analyzer         │
│  - LLM Client       │
│  - Patch Generator  │
└──────────┬──────────┘
           │
      ┌────┴─────┐
      ▼          ▼
┌──────────┐  ┌──────────────────┐
│  Pylint  │  │  LLM Providers   │
│  Static  │  │  - Anthropic API │
│ Analysis │  │  - OpenAI API    │
└──────────┘  │  - Google API    │
              └──────────────────┘
```

**Key Workflow:**
1. User saves Python file → Extension triggers analysis
2. Backend runs Pylint → Identifies code issues
3. For each issue → LLM generates fix with explanation
4. Extension displays diagnostics → User sees 💡 light bulb
5. User clicks quick fix → Smart patch application
6. Code updated automatically → File saved

## 📁 Project Structure

```
repo/
├── backend/
│   ├── main.py                 # FastAPI server with /analyze endpoint
│   ├── analyzer.py             # Pylint wrapper with custom config
│   ├── llm_client.py           # Multi-LLM client (OpenAI, Anthropic, Google)
│   ├── patch_generator.py      # Patch parsing and utilities
│   ├── models.py               # Pydantic data models
│   ├── requirements.txt        # Python dependencies
│   └── tests/                  # Backend tests
├── extension/
│   ├── src/
│   │   ├── extension.ts        # Entry point and command registration
│   │   ├── backendClient.ts    # HTTP client for backend API
│   │   ├── codeActions.ts      # Code actions provider with smart patch application
│   │   └── saveHandler.ts      # File save event handler
│   ├── package.json            # Extension manifest and metadata
│   ├── tsconfig.json           # TypeScript configuration
│   └── out/                    # Compiled JavaScript
├── .env.example                # Environment variables template
├── .pylintrc                   # Pylint configuration (format rules disabled)
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## ⚙️ Configuration

### Extension Settings

File > Preferences > Settings > No-chatbot:

- `no-chatbot.backendUrl` - Backend server URL (default: `http://localhost:8000`)
- `no-chatbot.autoAnalyzeOnSave` - Enable/disable auto-analysis (default: `true`)

### LLM Provider Configuration

Configure in `.env` file:

```bash
# Choose provider: openai, claude, or google
LLM_PROVIDER=claude

# Anthropic API (if using claude)
ANTHROPIC_API_KEY=sk-ant-xxxx
# Optional: ANTHROPIC_MODEL=your-anthropic-model

# OpenAI API (if using openai)
OPENAI_API_KEY=sk-proj-xxxx
# Optional: OPENAI_MODEL=your-openai-model

# Google API (if using google)
GOOGLE_API_KEY=AIza-xxxx
# Optional: GOOGLE_MODEL=your-google-model
```

## 🧪 Example

**Before:**
```python
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    x = 42  # Unused variable
    return total
```

**No-Chatbot detects:**
- Line 5: "Unused variable 'x'" (W0612)

**AI suggests:**
- 💡 **Remove unused variable**
- Description: "The variable 'x' is assigned but never used..."
- Patch: Removes the line
- Risks: "If planned for future use, may break functionality"

**After applying:**
```python
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
```

## 🔒 Privacy & Security

⚠️ **Important**: Code snippets are sent to external LLM APIs for analysis.

**What is sent:**
- Only problematic code sections (not your entire file)
- Issue context from Pylint (e.g., "unused variable")
- Surrounding lines for context

**Security considerations:**
- No code is stored permanently by this extension
- Your code is subject to the privacy policy of your chosen LLM provider:
  - **OpenAI**: [Privacy Policy](https://openai.com/policies/privacy-policy)
  - **Anthropic**: [Privacy Policy](https://www.anthropic.com/privacy)
  - **Google**: [Privacy Policy](https://policies.google.com/privacy)
- Use only on non-sensitive projects or configure environment-specific API keys
- Consider self-hosted LLM solutions for proprietary code

**Recommendations:**
- Review your LLM provider's data policies
- Use separate API keys for work vs. personal projects
- Disable auto-analysis for sensitive files (set `no-chatbot.autoAnalyzeOnSave` to `false`)

See [PRIVACY.md](PRIVACY.md) for detailed information.

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Extension tests (coming soon)
cd extension
npm test
```

### Building Extension Package

```bash
cd extension
npm run package
# Creates no-chatbot-0.1.0.vsix
```

## 🗺️ Roadmap

### ✅ Completed (MVP)

- [x] Pylint static analysis integration
- [x] Multi-LLM support (OpenAI, Anthropic, Google)
- [x] Event-driven file save trigger
- [x] Code Actions UI with quick fixes
- [x] Smart content-based patch application
- [x] Undo functionality with full state restoration
- [x] Comprehensive documentation
- [x] Backend API with FastAPI
- [x] VS Code extension with TypeScript

### 🎯 Near-term (Post-MVP)

- [ ] Package as .vsix for easy installation
- [ ] Publish to VS Code Marketplace
- [ ] Add extension analytics and telemetry
- [ ] Performance optimizations and caching
- [ ] Support for batch fix application

### 🔮 Future Enhancements

- [ ] Additional analyzers (Mypy, Flake8, Bandit, Ruff)
- [ ] Pytest failure detection and fix suggestion
- [ ] Runtime exception handling with stack trace analysis
- [ ] Custom Webview UI for richer fix presentation
- [ ] Multi-file refactoring support
- [ ] Request caching to reduce API costs
- [ ] User study and metrics collection for research
- [ ] Support for additional languages (JavaScript, TypeScript, etc.)

## 📝 License

This is a research project for the Autonomy Technologies MSc program.  
Licensed under the MIT License - see [LICENSE](LICENSE) file for details.
