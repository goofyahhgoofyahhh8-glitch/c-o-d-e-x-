#!/usr/bin/env python3
"""
CODEX — All-Red Terminal AI Chatbot
Powered by OpenRouter API
"""

import sys
import os
import json
import time
import threading
import urllib.request
import urllib.error
import shutil
from datetime import datetime

# Remove integer string conversion limits for massive digit strings (Python 3.11+)
if hasattr(sys, "set_int_max_str_digits"):
    try:
        sys.set_int_max_str_digits(0)
    except Exception:
        pass

# Ensure UTF-8 output on Windows consoles
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Windows Virtual Terminal ANSI activation
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_out = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h_out, ctypes.byref(mode))
        kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
    except Exception:
        pass

# --- RED COLOR THEME DEFINITIONS ---
RESET        = "\033[0m"
BOLD         = "\033[1m"
DIM          = "\033[2m"

# Gradients & Shades of Red
RED_BLOOD    = "\033[38;5;52m"     # Very dark red
RED_MAROON   = "\033[38;5;88m"     # Dark maroon
RED_DARK     = "\033[38;5;124m"    # Deep red
RED_CRIMSON  = "\033[38;5;160m"    # Crimson red
RED_FIRE     = "\033[38;5;196m"    # Pure vibrant neon red
RED_CORAL    = "\033[38;5;203m"    # Bright light coral-red
RED_SALMON   = "\033[38;5;210m"    # Soft rose red for bot speech
RED_PALE     = "\033[38;5;217m"    # Pale red highlight
RED_BG       = "\033[48;5;52m"     # Dark red background highlight
RED_BG_LIGHT = "\033[48;5;88m"

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "codex_config.json")
AUTO_LOAD_FILE = "deepseek.txt"  # Auto-loaded into system context on startup

def find_auto_load_file():
    """Search for the auto-load file in common locations."""
    candidates = [
        os.path.join(SCRIPT_DIR, AUTO_LOAD_FILE),
        os.path.join(SCRIPT_DIR, "..", AUTO_LOAD_FILE),
        os.path.join(os.path.expanduser("~"), AUTO_LOAD_FILE),
        os.path.join(os.path.expanduser("~"), "Downloads", AUTO_LOAD_FILE),
        os.path.join(os.path.expanduser("~"), "storage", "downloads", AUTO_LOAD_FILE),  # Termux
        os.path.join(os.path.expanduser("~"), "storage", "shared", AUTO_LOAD_FILE),     # Termux shared
        AUTO_LOAD_FILE,  # current working directory
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None

def load_config():
    cfg = {
        "api_key": DEFAULT_API_KEY,
        "model": "deepseek/deepseek-v4-flash",
        "system_prompt": "You are CODEX, an elite, hyper-intelligent, sharp terminal AI entity. You speak with high precision, speed, and technical mastery. Keep explanations direct, punchy, and provide flawless code and answers.",
        "temperature": 0.7,
        "max_tokens": 8192
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                cfg.update(user_cfg)
        except Exception:
            pass
    return cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def get_terminal_width():
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80

def red_line(char="━", length=None):
    width = length or min(get_terminal_width(), 95)
    return f"{RED_DARK}{char * width}{RESET}"

def red_box(text, title=None, style=RED_CRIMSON):
    width = min(get_terminal_width() - 4, 90)
    lines = text.split("\n")
    top_border = f"┏━{' [' + title + '] ' if title else ''}"
    top_border += "━" * (width - len(title or "") - (6 if title else 2)) + "┓"
    
    out = [f"{style}{top_border}{RESET}"]
    for line in lines:
        out.append(f"{style}┃ {RESET}{RED_CORAL}{line}{RESET}")
    out.append(f"{style}┗{'━' * width}┛{RESET}")
    return "\n".join(out)

BANNER = f"""{RED_FIRE}{BOLD}
 ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝
██║     ██║   ██║██║  ██║█████╗   ╚███╔╝ 
██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗ 
╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝{RESET}
{RED_CRIMSON}       ━═[ TERMINAL AI CHATBOX ]═━{RESET}
"""

class Spinner:
    def __init__(self, message="CODEX is synthesizing"):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None
        self.chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.is_tty = sys.stdout.isatty()

    def _spin(self):
        if not self.is_tty:
            return
        idx = 0
        while not self.stop_event.is_set():
            c = self.chars[idx % len(self.chars)]
            pulse = RED_FIRE if idx % 2 == 0 else RED_CRIMSON
            sys.stdout.write(f"\r\033[2K{RED_DARK}│ {pulse}{c}{RESET} {RED_CORAL}{self.message}...{RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            idx += 1
        sys.stdout.write(f"\r\033[2K{RED_DARK}│ {RESET}")
        sys.stdout.flush()

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.stop_event.set()
            self.thread.join(timeout=0.5)
            if self.is_tty:
                sys.stdout.write(f"\r\033[2K{RED_DARK}│ {RESET}")
                sys.stdout.flush()

class CodexClient:
    def __init__(self, config):
        self.config = config
        self.history = []
        self._init_history()

    def _init_history(self):
        self.history = [
            {"role": "system", "content": self.config["system_prompt"]}
        ]

    def reset_history(self):
        self._init_history()

    def set_system_prompt(self, new_prompt):
        self.config["system_prompt"] = new_prompt
        self.history[0] = {"role": "system", "content": new_prompt}
        save_config(self.config)

    def set_model(self, new_model):
        self.config["model"] = new_model
        save_config(self.config)

    def set_api_key(self, key):
        self.config["api_key"] = key
        save_config(self.config)

    def set_tokens(self, tokens):
        self.config["max_tokens"] = tokens
        save_config(self.config)

    def stream_chat(self, user_input, on_token=None, on_error=None):
        self.history.append({"role": "user", "content": user_input})
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": self.config["model"],
            "messages": self.history,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 8192),
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://codex.local",
            "X-Title": "Codex Red Terminal"
        }

        full_reply = []
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str or not line_str.startswith("data:"):
                        continue
                    if line_str == "data: [DONE]":
                        break
                    raw_json = line_str[5:].strip()
                    try:
                        chunk = json.loads(raw_json)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                full_reply.append(token)
                                if on_token:
                                    on_token(token)
                    except json.JSONDecodeError:
                        continue
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace")
            if on_error:
                on_error(f"HTTP Error {he.code}: {err_body}")
            # Revert user prompt if failed
            self.history.pop()
            return None
        except Exception as e:
            if on_error:
                on_error(f"Network / Stream Error: {str(e)}")
            self.history.pop()
            return None

        assistant_msg = "".join(full_reply)
        self.history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

def print_help():
    help_text = f"""
{RED_FIRE}{BOLD}CODEX COMMAND MATRIX:{RESET}
  {RED_CRIMSON}/help{RESET}               {RED_CORAL}Show this command manual{RESET}
  {RED_CRIMSON}/paste{RESET}              {RED_CORAL}Paste huge text / millions of words without buffer limits{RESET}
  {RED_CRIMSON}/file <path> [p]{RESET}    {RED_CORAL}Load entire local file into prompt (huge files supported){RESET}
  {RED_CRIMSON}/tokens [num]{RESET}       {RED_CORAL}Set maximum response tokens (e.g. 8192, 16384, 32768){RESET}
  {RED_CRIMSON}/clear{RESET}              {RED_CORAL}Wipe screen and display CODEX banner{RESET}
  {RED_CRIMSON}/model [id]{RESET}         {RED_CORAL}Switch active AI model or check current{RESET}
  {RED_CRIMSON}/models{RESET}             {RED_CORAL}List top high-performance recommended models{RESET}
  {RED_CRIMSON}/system [text]{RESET}      {RED_CORAL}View or update CODEX persona / system prompt{RESET}
  {RED_CRIMSON}/key [key]{RESET}          {RED_CORAL}View or update OpenRouter API key{RESET}
  {RED_CRIMSON}/reset{RESET}              {RED_CORAL}Clear memory and restart conversation{RESET}
  {RED_CRIMSON}/history{RESET}            {RED_CORAL}Inspect dialogue token & message count{RESET}
  {RED_CRIMSON}/save [file]{RESET}        {RED_CORAL}Dump conversation transcript to file{RESET}
  {RED_CRIMSON}/exit{RESET}               {RED_CORAL}Shut down CODEX{RESET}
"""
    print(help_text)

def print_models():
    models_info = f"""
{RED_FIRE}{BOLD}RECOMMENDED OPENROUTER MODELS:{RESET}
  {RED_CRIMSON}openrouter/auto{RESET}                 {RED_CORAL}(Default - Auto-routes to best available){RESET}
  {RED_CRIMSON}deepseek/deepseek-chat{RESET}          {RED_CORAL}(DeepSeek V3 - High IQ, Fast, 64k Context){RESET}
  {RED_CRIMSON}deepseek/deepseek-v4-flash{RESET}      {RED_CORAL}(DeepSeek Flash - Ultra low latency){RESET}
  {RED_CRIMSON}deepseek/deepseek-r1{RESET}            {RED_CORAL}(DeepSeek R1 - Heavy Reasoning){RESET}
  {RED_CRIMSON}meta-llama/llama-3.3-70b-instruct{RESET} {RED_CORAL}(Llama 3.3 70B - 128k Context){RESET}
  {RED_CRIMSON}openai/gpt-4o-mini{RESET}               {RED_CORAL}(GPT-4o Mini - Ultra-fast & Light, 128k Context){RESET}
  {RED_CRIMSON}anthropic/claude-3.5-haiku{RESET}       {RED_CORAL}(Claude 3.5 Haiku - Sharp & concise){RESET}

  {RED_DARK}Use {RED_FIRE}/model <id>{RED_DARK} to set any model!{RESET}
"""
    print(models_info)

def clear_screen(config=None):
    os.system("cls" if sys.platform == "win32" else "clear")
    print(BANNER)
    print(f"{RED_DARK}Type {RED_FIRE}/help{RED_DARK} for command matrix or type your query below.{RESET}\n")

def main():
    config = load_config()
    client = CodexClient(config)
    clear_screen(config)

    # First-run: prompt for API key if not set
    if not config.get("api_key"):
        print(f"{RED_FIRE}{BOLD}[!] No API key found.{RESET}")
        print(f"{RED_CORAL}Get a free key at: {RED_FIRE}https://openrouter.ai/keys{RESET}")
        sys.stdout.write(f"{RED_FIRE}Paste your OpenRouter API key: {RED_CORAL}")
        sys.stdout.flush()
        try:
            key = input().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{RED_DARK}[!] No key provided. Exiting.{RESET}")
            return
        sys.stdout.write(RESET)
        if key:
            client.set_api_key(key)
            print(f"{RED_FIRE}[✓] API key saved. You won't be asked again.{RESET}\n")
        else:
            print(f"{RED_DARK}[!] No key provided. Use /key <your-key> later.{RESET}\n")

    # Auto-load deepseek.txt into system context on startup
    auto_file = find_auto_load_file()
    if auto_file:
        try:
            with open(auto_file, "r", encoding="utf-8", errors="replace") as f:
                auto_content = f.read()
            # Inject file content into system prompt context
            client.history.append({"role": "user", "content": f"[AUTO-LOADED FILE: {os.path.basename(auto_file)}]\n{auto_content}"})
            client.history.append({"role": "assistant", "content": "File loaded and internalized. Ready."})
            print(f"{RED_FIRE}[✓] Auto-loaded '{os.path.basename(auto_file)}' ({len(auto_content):,} chars / ~{len(auto_content.split()):,} words){RESET}")
        except Exception as e:
            print(f"{RED_DARK}[!] Could not auto-load {AUTO_LOAD_FILE}: {e}{RESET}")
    else:
        print(f"{RED_DARK}[i] No '{AUTO_LOAD_FILE}' found. Place it next to codex.py to auto-load.{RESET}")

    print(f"{RED_DARK}[i] Model: {RED_FIRE}{config['model']}{RESET}\n")

    while True:
        try:
            # Styled Red Prompt
            sys.stdout.write(f"\n{RED_DARK}┌─[{RED_FIRE}{BOLD}YOU{RESET}{RED_DARK}]─────────────────────────────────────────────{RESET}\n")
            sys.stdout.write(f"{RED_FIRE}└─► {RED_CORAL}")
            sys.stdout.flush()

            try:
                user_input = input()
            except EOFError:
                break

            sys.stdout.write(RESET)
            user_input = user_input.strip()

            if not user_input:
                continue

            # Command Handling
            if user_input.startswith("/"):
                parts = user_input.split(" ", 1)
                cmd = parts[0].lower()
                arg = parts[1].strip() if len(parts) > 1 else ""

                if cmd in ("/exit", "/quit", "/q"):
                    print(f"\n{RED_FIRE}{BOLD}[!] Terminating CODEX session. Goodbye.{RESET}\n")
                    break

                elif cmd in ("/help", "/h", "/?"):
                    print_help()
                    continue

                elif cmd in ("/clear", "/cls"):
                    clear_screen(config)
                    continue

                elif cmd == "/paste":
                    print(f"\n{RED_DARK}┌─[{RED_FIRE}{BOLD}CODEX MULTI-LINE / PASTE MODE - UNLIMITED SIZE{RESET}{RED_DARK}]─────────────────────{RESET}")
                    print(f"{RED_DARK}│ {RED_CORAL}Paste your text, code, or large content (millions of words supported).{RESET}")
                    print(f"{RED_DARK}│ {RED_FIRE}Instructions:{RESET} {RED_CORAL}Type {RED_FIRE}///{RED_CORAL} on an empty line and press Enter to send.{RESET}")
                    print(f"{RED_DARK}│               {RED_CORAL}Or type {RED_FIRE}/cancel{RED_CORAL} on a new line to abort.{RESET}")
                    print(f"{RED_DARK}└─────────────────────────────────────────────────────────────────────────────{RESET}")
                    paste_lines = []
                    while True:
                        try:
                            line = sys.stdin.readline()
                            if not line:
                                break
                            clean_line = line.rstrip("\r\n")
                            if clean_line == "///":
                                break
                            if clean_line == "/cancel":
                                paste_lines = []
                                print(f"{RED_DARK}[!] Paste cancelled.{RESET}")
                                break
                            paste_lines.append(clean_line)
                        except (KeyboardInterrupt, EOFError):
                            break
                    if not paste_lines:
                        continue
                    user_input = "\n".join(paste_lines)
                    print(f"{RED_FIRE}[✓] Ingested {len(user_input):,} characters (~{len(user_input.split()):,} words). Transmitting...{RESET}")

                elif cmd == "/file":
                    if not arg:
                        print(f"\n{RED_DARK}[!] Usage: /file <path-to-file> [optional instruction]{RESET}")
                        continue
                    arg_parts = arg.split(" ", 1)
                    filepath = arg_parts[0].strip('"').strip("'")
                    instruction = arg_parts[1] if len(arg_parts) > 1 else ""

                    # Smart Path Resolution (current dir, parent dir, and common extensions)
                    resolved = None
                    candidates = [filepath, os.path.join("..", filepath)]
                    base, ext = os.path.splitext(filepath)
                    if ext in ("", ".file"):
                        for alt_ext in [".txt", ".md", ".json", ".py", ".csv", ".log", ".doc"]:
                            candidates.extend([base + alt_ext, os.path.join("..", base + alt_ext)])
                    for c in candidates:
                        if os.path.isfile(c):
                            resolved = os.path.abspath(c)
                            break

                    if not resolved:
                        print(f"\n{RED_DARK}[✗] File not found: {filepath}{RESET}")
                        print(f"{RED_DARK}Tip: Drag and drop the file into the terminal window, or specify full path.{RESET}")
                        continue

                    try:
                        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                            file_content = f.read()
                        print(f"\n{RED_FIRE}[✓] Loaded file '{os.path.basename(resolved)}' ({len(file_content):,} chars / ~{len(file_content.split()):,} words){RESET}")
                        if instruction:
                            user_input = f"{instruction}\n\n[FILE: {os.path.basename(resolved)}]\n{file_content}"
                        else:
                            user_input = f"[FILE: {os.path.basename(resolved)}]\n{file_content}"
                    except Exception as e:
                        print(f"\n{RED_DARK}[✗] Could not read file: {e}{RESET}")
                        continue

                elif cmd == "/tokens":
                    if arg:
                        try:
                            num = int(arg)
                            client.set_tokens(num)
                            print(f"\n{RED_FIRE}[✓] Max output tokens set to: {RED_CORAL}{num:,}{RESET}")
                        except ValueError:
                            print(f"\n{RED_DARK}[!] Provide a valid integer token limit.{RESET}")
                    else:
                        print(f"\n{RED_FIRE}Current max tokens: {RED_CORAL}{client.config.get('max_tokens', 8192):,}{RESET}")
                    continue

                elif cmd == "/models":
                    print_models()
                    continue

                elif cmd == "/model":
                    if arg:
                        client.set_model(arg)
                        print(f"\n{RED_FIRE}[✓] Model switched to: {RED_CORAL}{arg}{RESET}")
                    else:
                        print(f"\n{RED_DARK}Current active model: {RED_FIRE}{config['model']}{RESET}")
                        print(f"{RED_DARK}Change with: {RED_FIRE}/model <model-id>{RESET}")
                    continue

                elif cmd == "/key":
                    if arg:
                        client.set_api_key(arg)
                        print(f"\n{RED_FIRE}[✓] API key updated successfully.{RESET}")
                    else:
                        print(f"\n{RED_DARK}Current key: {RED_FIRE}{config['api_key'][:16]}...{config['api_key'][-6:]}{RESET}")
                    continue

                elif cmd == "/system":
                    if arg:
                        client.set_system_prompt(arg)
                        print(f"\n{RED_FIRE}[✓] System prompt updated.{RESET}")
                    else:
                        print(f"\n{RED_FIRE}Current System Prompt:{RESET}\n{RED_CORAL}{config['system_prompt']}{RESET}")
                    continue

                elif cmd == "/reset":
                    client.reset_history()
                    print(f"\n{RED_FIRE}[✓] Memory wiped. Conversation context reset.{RESET}")
                    continue

                elif cmd == "/history":
                    count = len(client.history) - 1
                    print(f"\n{RED_FIRE}Active Context turns: {RED_CORAL}{count}{RESET} messages in memory.")
                    continue

                elif cmd == "/save":
                    fname = arg if arg else f"codex_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    try:
                        with open(fname, "w", encoding="utf-8") as f:
                            f.write(f"CODEX CHAT TRANSCRIPT - {datetime.now().isoformat()}\n")
                            f.write("=" * 60 + "\n\n")
                            for m in client.history:
                                f.write(f"[{m['role'].upper()}]:\n{m['content']}\n\n")
                        print(f"\n{RED_FIRE}[✓] Transcript saved to: {RED_CORAL}{fname}{RESET}")
                    except Exception as e:
                        print(f"\n{RED_DARK}[✗] Failed to save file: {e}{RESET}")
                    continue

                else:
                    print(f"\n{RED_DARK}[!] Unknown command '{cmd}'. Type {RED_FIRE}/help{RED_DARK} for command list.{RESET}")
                    continue

            # Stream bot response
            print(f"\n{RED_DARK}┌─[{RED_FIRE}{BOLD}CODEX{RESET}{RED_DARK}]───────────────────────────────────────────{RESET}")
            sys.stdout.write(f"{RED_DARK}│ {RESET}")
            sys.stdout.flush()

            spinner = Spinner("Transmitting to neural core")
            spinner.start()

            first_token_received = False

            def on_token(token):
                nonlocal first_token_received
                if not first_token_received:
                    spinner.stop()
                    first_token_received = True

                # Format tokens in red aesthetic with proper indentation for linebreaks
                token_formatted = token.replace("\n", f"\n{RED_DARK}│ {RESET}{RED_CORAL}")
                sys.stdout.write(f"{RED_CORAL}{token_formatted}{RESET}")
                sys.stdout.flush()

            def on_error(err):
                spinner.stop()
                sys.stdout.write(f"\n{RED_DARK}│ {RED_FIRE}[ERROR] {err}{RESET}\n")
                sys.stdout.flush()

            reply = client.stream_chat(user_input, on_token=on_token, on_error=on_error)

            if not first_token_received:
                spinner.stop()

            sys.stdout.write(f"\n{RED_DARK}└{'─' * 55}{RESET}\n")
            sys.stdout.flush()

        except KeyboardInterrupt:
            sys.stdout.write(f"\n\n{RED_DARK}[!] Interrupted. Press Ctrl+C again or type /exit to terminate.{RESET}\n")
            try:
                time.sleep(0.3)
            except KeyboardInterrupt:
                print(f"\n{RED_FIRE}{BOLD}[!] Force exiting CODEX.{RESET}\n")
                break

if __name__ == "__main__":
    main()
