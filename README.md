# 🔴 CODEX — All-Red Terminal AI Chatbot

<p align="center">
<pre>
 ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝
██║     ██║   ██║██║  ██║█████╗   ╚███╔╝
██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗
╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
        ━═[ TERMINAL AI CHATBOX ]═━
</pre>
</p>

A sleek, all-red terminal AI chatbot powered by **OpenRouter API** with real-time streaming, multi-model switching, and massive text input support.

**Zero dependencies** — runs on pure Python 3 standard library. No `pip install` needed.

---

## ⚡ Quick Start

### 1. Get an API Key (free)
Go to [openrouter.ai/keys](https://openrouter.ai/keys) and create a free API key.

### 2. Run CODEX

**Windows:**
```cmd
python codex.py
```
Or double-click `codex.bat`

**Linux / macOS:**
```bash
python3 codex.py
```

**Termux (Android):**
```bash
pkg install python
python codex.py
```

### 3. Paste your API key when prompted
CODEX will ask for your key on first run and save it locally. You only do this once.

---

## 🛠️ Features

- **🔴 Full Red ANSI Aesthetic** — Deep maroon frames, neon red banners, coral bot text, vibrant red prompts
- **⚡ Real-Time Streaming** — Watch tokens appear live as the AI generates them
- **🤖 400+ AI Models** — Switch between DeepSeek, GPT-4o, Claude, Llama, Gemini, and more via `/model`
- **📄 Massive Input Support** — Paste millions of characters via `/paste` or load entire files via `/file`
- **💾 Auto-Load Context** — Drop a `deepseek.txt` next to `codex.py` and it auto-loads into every session
- **🔧 Zero Dependencies** — Pure Python 3 standard library, no pip install required
- **📱 Cross-Platform** — Windows, Linux, macOS, and Termux (Android)
- **💬 Conversation Memory** — Maintains full dialogue context across messages
- **📝 Transcript Export** — Save entire chat history to file with `/save`

---

## 🎮 Commands

| Command | Description |
|---|---|
| `/help` | Show command list |
| `/paste` | Multi-line paste mode (unlimited text size) |
| `/file <path> [prompt]` | Load a file into the AI prompt |
| `/tokens [num]` | Set max response tokens (default: 8192) |
| `/model [id]` | Switch AI model or view current |
| `/models` | List recommended models |
| `/system [text]` | View or change system prompt |
| `/key [key]` | View or update API key |
| `/reset` | Clear conversation memory |
| `/history` | Show message count |
| `/save [file]` | Export chat transcript |
| `/clear` | Clear screen |
| `/exit` | Quit |

---

## 🤖 Recommended Models

| Model | Speed | Best For |
|---|---|---|
| `deepseek/deepseek-v4-flash` | ⚡ Blazing | Quick chat, fast answers (default) |
| `deepseek/deepseek-chat` | 🚀 Fast | Elite coding, complex logic |
| `deepseek/deepseek-r1` | 🧠 Slow | Deep reasoning, math proofs |
| `openai/gpt-4o-mini` | ⚡ Fast | Reliable, accurate |
| `openrouter/auto` | 🔄 Auto | Routes to best available |

Switch models on the fly:
```
/model deepseek/deepseek-chat
```

---

## 📄 Auto-Load Files

Place a file named `deepseek.txt` (or any context file) next to `codex.py`. It will be automatically loaded into every conversation on startup.

---

## ⚙️ Configuration

Settings are saved in `codex_config.json` (auto-created, git-ignored). You can also set your key via environment variable:

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
python codex.py
```

---

## 📜 License

MIT — do whatever you want with it.
