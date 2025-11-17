"""
Ultimate Command Execution System
A powerful system that can execute almost any command with natural language understanding.
Integrates with Ollama, Playwright for browser automation, and system command execution.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    requests = None

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None
    Page = None


@dataclass
class CommandIntent:
    """Represents a parsed command with action and parameters."""
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    raw_command: str = ""


class OllamaClient:
    """Client for interacting with Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.available = requests is not None
    
    def _check_connection(self) -> bool:
        """Check if Ollama is available."""
        if not self.available:
            return False
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Generate a response from Ollama."""
        if not self._check_connection():
            return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            return None
        except Exception as e:
            print(f"[ollama] Error: {e}")
            return None
    
    def parse_command(self, user_input: str) -> Optional[CommandIntent]:
        """Parse a natural language command into a structured intent."""
        system_prompt = """You are an intelligent command parser. Your job is to understand user commands and convert them into structured JSON format.

Available command types:
- browser_navigate: Navigate to a URL (requires: url)
- browser_search: Search for something (requires: query)
- browser_click: Click on an element (requires: description or selector)
- browser_type: Type text into a field (requires: text, optional: selector)
- browser_scroll: Scroll the page (requires: direction: up/down/left/right, optional: amount)
- browser_wait: Wait for something (requires: condition)
- browser_get_text: Extract text from page (requires: description)
- browser_get_url: Get current URL
- browser_screenshot: Take a screenshot
- browser_back: Go back in browser history
- browser_forward: Go forward in browser history
- browser_refresh: Refresh the page
- browser_new_tab: Open a new tab
- browser_close_tab: Close current tab
- browser_switch_tab: Switch to a tab (requires: index or title)
- system_execute: Execute a system command (requires: command)
- file_read: Read a file (requires: path)
- file_write: Write to a file (requires: path, content)
- file_list: List directory (requires: path)
- file_create: Create a file (requires: path, optional: content)
- file_delete: Delete a file or directory (requires: path)
- file_move: Move/rename a file (requires: source, dest)
- file_copy: Copy a file (requires: source, dest)
- web_search: Search the web (requires: query)
- chat: General conversation or question answering (requires: query)

Return ONLY valid JSON in this exact format:
{
    "action": "command_type",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    },
    "confidence": 0.95
}

If the command is ambiguous or unclear, return the most likely interpretation with lower confidence."""

        prompt = f"""Parse this command into JSON format: "{user_input}"

Return only the JSON, no additional text."""

        response = self.generate(prompt, system_prompt)
        if not response:
            return None
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return CommandIntent(
                    action=data.get("action", "unknown"),
                    parameters=data.get("parameters", {}),
                    confidence=data.get("confidence", 0.5),
                    raw_command=user_input
                )
            except json.JSONDecodeError:
                pass
        
        return None


class BrowserController:
    """Advanced browser automation using Playwright."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        self.current_page: Optional[Page] = None
        self.available = async_playwright is not None
    
    async def initialize(self) -> bool:
        """Initialize the browser."""
        if not self.available:
            print("[browser] Playwright not available. Install with: pip install playwright && playwright install")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.current_page = await self.context.new_page()
            self.pages.append(self.current_page)
            print("[browser] Browser initialized successfully")
            return True
        except Exception as e:
            print(f"[browser] Initialization error: {e}")
            return False
    
    async def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self.current_page:
            return False
        try:
            # Normalize URL
            if not url.startswith(("http://", "https://")):
                if "." in url and " " not in url:
                    url = f"https://{url}"
                else:
                    # Treat as search query
                    url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            
            await self.current_page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"[browser] Navigated to: {self.current_page.url}")
            return True
        except Exception as e:
            print(f"[browser] Navigation error: {e}")
            return False
    
    async def search(self, query: str) -> bool:
        """Search the web."""
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return await self.navigate(search_url)
    
    async def click(self, description: Optional[str] = None, selector: Optional[str] = None) -> bool:
        """Click on an element."""
        if not self.current_page:
            return False
        
        try:
            if selector:
                await self.current_page.click(selector)
            elif description:
                # Try to find element by text
                await self.current_page.click(f"text={description}", timeout=5000)
            else:
                print("[browser] No selector or description provided for click")
                return False
            return True
        except Exception as e:
            print(f"[browser] Click error: {e}")
            # Try alternative: click by visible text
            if description:
                try:
                    await self.current_page.locator(f"text={description}").first.click(timeout=5000)
                    return True
                except:
                    pass
            return False
    
    async def type_text(self, text: str, selector: Optional[str] = None) -> bool:
        """Type text into a field."""
        if not self.current_page:
            return False
        
        try:
            if selector:
                await self.current_page.fill(selector, text)
            else:
                # Click on active element and type
                await self.current_page.keyboard.press("Tab")
                await self.current_page.keyboard.type(text)
            return True
        except Exception as e:
            print(f"[browser] Type error: {e}")
            return False
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        """Scroll the page."""
        if not self.current_page:
            return False
        
        try:
            if direction.lower() == "down":
                await self.current_page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction.lower() == "up":
                await self.current_page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction.lower() == "right":
                await self.current_page.evaluate(f"window.scrollBy({amount}, 0)")
            elif direction.lower() == "left":
                await self.current_page.evaluate(f"window.scrollBy(-{amount}, 0)")
            return True
        except Exception as e:
            print(f"[browser] Scroll error: {e}")
            return False
    
    async def get_text(self, description: Optional[str] = None, selector: Optional[str] = None) -> Optional[str]:
        """Extract text from the page."""
        if not self.current_page:
            return None
        
        try:
            if selector:
                element = await self.current_page.query_selector(selector)
                if element:
                    return await element.inner_text()
            elif description:
                # Try to find by text
                locator = self.current_page.locator(f"text={description}").first
                if await locator.count() > 0:
                    return await locator.inner_text()
            else:
                # Get all visible text
                return await self.current_page.inner_text("body")
            return None
        except Exception as e:
            print(f"[browser] Get text error: {e}")
            return None
    
    async def get_url(self) -> Optional[str]:
        """Get current URL."""
        if not self.current_page:
            return None
        return self.current_page.url
    
    async def screenshot(self, path: Optional[str] = None) -> bool:
        """Take a screenshot."""
        if not self.current_page:
            return False
        
        try:
            path = path or f"screenshot_{int(asyncio.get_event_loop().time())}.png"
            await self.current_page.screenshot(path=path)
            print(f"[browser] Screenshot saved to: {path}")
            return True
        except Exception as e:
            print(f"[browser] Screenshot error: {e}")
            return False
    
    async def go_back(self) -> bool:
        """Go back in browser history."""
        if not self.current_page:
            return False
        try:
            await self.current_page.go_back()
            return True
        except:
            return False
    
    async def go_forward(self) -> bool:
        """Go forward in browser history."""
        if not self.current_page:
            return False
        try:
            await self.current_page.go_forward()
            return True
        except:
            return False
    
    async def refresh(self) -> bool:
        """Refresh the page."""
        if not self.current_page:
            return False
        try:
            await self.current_page.reload()
            return True
        except:
            return False
    
    async def new_tab(self) -> bool:
        """Open a new tab."""
        if not self.context:
            return False
        try:
            page = await self.context.new_page()
            self.pages.append(page)
            self.current_page = page
            return True
        except:
            return False
    
    async def close_tab(self) -> bool:
        """Close current tab."""
        if not self.current_page or len(self.pages) <= 1:
            print("[browser] Cannot close the last tab")
            return False
        
        try:
            await self.current_page.close()
            self.pages.remove(self.current_page)
            self.current_page = self.pages[-1] if self.pages else None
            return True
        except:
            return False
    
    async def switch_tab(self, index: Optional[int] = None, title: Optional[str] = None) -> bool:
        """Switch to a different tab."""
        if not self.pages:
            return False
        
        try:
            if index is not None and 0 <= index < len(self.pages):
                self.current_page = self.pages[index]
                await self.current_page.bring_to_front()
                return True
            elif title:
                for page in self.pages:
                    if title.lower() in (await page.title()).lower():
                        self.current_page = page
                        await page.bring_to_front()
                        return True
            return False
        except:
            return False
    
    async def wait(self, condition: str, timeout: int = 30000) -> bool:
        """Wait for a condition."""
        if not self.current_page:
            return False
        
        try:
            # Try to parse common wait conditions
            if "load" in condition.lower():
                await self.current_page.wait_for_load_state("networkidle", timeout=timeout)
            elif "selector" in condition.lower() or condition.startswith("#") or condition.startswith("."):
                await self.current_page.wait_for_selector(condition, timeout=timeout)
            else:
                await asyncio.sleep(2)  # Default wait
            return True
        except:
            return False
    
    async def close(self):
        """Close the browser."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass


class SystemExecutor:
    """Execute system commands."""
    
    @staticmethod
    def execute(command: str) -> Tuple[bool, str, str]:
        """Execute a system command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)


class FileOperations:
    """File system operations."""
    
    @staticmethod
    def read_file(path: str) -> Tuple[bool, str]:
        """Read a file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return True, f.read()
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def write_file(path: str, content: str) -> Tuple[bool, str]:
        """Write to a file."""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"File written: {path}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def list_directory(path: str) -> Tuple[bool, List[str]]:
        """List directory contents."""
        try:
            p = Path(path) if path else Path(".")
            if not p.exists():
                return False, []
            items = [str(item) for item in p.iterdir()]
            return True, items
        except Exception as e:
            return False, []
    
    @staticmethod
    def create_file(path: str, content: str = "") -> Tuple[bool, str]:
        """Create a file."""
        return FileOperations.write_file(path, content)
    
    @staticmethod
    def delete_file(path: str) -> Tuple[bool, str]:
        """Delete a file or directory."""
        try:
            p = Path(path)
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
            else:
                p.unlink()
            return True, f"Deleted: {path}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def move_file(source: str, dest: str) -> Tuple[bool, str]:
        """Move/rename a file."""
        try:
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(source).rename(dest)
            return True, f"Moved {source} to {dest}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def copy_file(source: str, dest: str) -> Tuple[bool, str]:
        """Copy a file."""
        try:
            import shutil
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            return True, f"Copied {source} to {dest}"
        except Exception as e:
            return False, str(e)


class UltimateCommandSystem:
    """The ultimate command execution system."""
    
    def __init__(self, ollama_model: str = "llama3.2", ollama_url: str = "http://localhost:11434"):
        self.ollama = OllamaClient(ollama_url, ollama_model)
        self.browser = BrowserController()
        self.system = SystemExecutor()
        self.files = FileOperations()
        self.running = False
    
    async def initialize(self):
        """Initialize all components."""
        print("[system] Initializing Ultimate Command System...")
        if not self.ollama._check_connection():
            print("[warning] Ollama not available. Some features may be limited.")
        await self.browser.initialize()
        print("[system] Ready! Type commands or 'exit' to quit.")
        print("[system] Example commands:")
        print("  - 'go to google.com'")
        print("  - 'search for python tutorials'")
        print("  - 'click on the login button'")
        print("  - 'scroll down'")
        print("  - 'execute ls -la'")
        print("  - 'read file.txt'")
        print("  - 'write hello.txt with content Hello World'")
        print()
    
    async def execute_command(self, command: CommandIntent) -> bool:
        """Execute a parsed command."""
        action = command.action
        params = command.parameters
        
        print(f"[executing] {action} with params: {params}")
        
        try:
            # Browser commands
            if action == "browser_navigate":
                url = params.get("url", "")
                return await self.browser.navigate(url)
            
            elif action == "browser_search":
                query = params.get("query", "")
                return await self.browser.search(query)
            
            elif action == "browser_click":
                selector = params.get("selector")
                description = params.get("description")
                return await self.browser.click(description=description, selector=selector)
            
            elif action == "browser_type":
                text = params.get("text", "")
                selector = params.get("selector")
                return await self.browser.type_text(text, selector=selector)
            
            elif action == "browser_scroll":
                direction = params.get("direction", "down")
                amount = int(params.get("amount", 500))
                return await self.browser.scroll(direction, amount)
            
            elif action == "browser_get_text":
                selector = params.get("selector")
                description = params.get("description")
                text = await self.browser.get_text(description=description, selector=selector)
                if text:
                    print(f"[result] {text[:500]}")  # Print first 500 chars
                    return True
                return False
            
            elif action == "browser_get_url":
                url = await self.browser.get_url()
                if url:
                    print(f"[result] Current URL: {url}")
                    return True
                return False
            
            elif action == "browser_screenshot":
                path = params.get("path")
                return await self.browser.screenshot(path)
            
            elif action == "browser_back":
                return await self.browser.go_back()
            
            elif action == "browser_forward":
                return await self.browser.go_forward()
            
            elif action == "browser_refresh":
                return await self.browser.refresh()
            
            elif action == "browser_new_tab":
                return await self.browser.new_tab()
            
            elif action == "browser_close_tab":
                return await self.browser.close_tab()
            
            elif action == "browser_switch_tab":
                index = params.get("index")
                title = params.get("title")
                return await self.browser.switch_tab(index=index, title=title)
            
            elif action == "browser_wait":
                condition = params.get("condition", "")
                return await self.browser.wait(condition)
            
            # System commands
            elif action == "system_execute":
                cmd = params.get("command", "")
                success, stdout, stderr = self.system.execute(cmd)
                if stdout:
                    print(f"[stdout]\n{stdout}")
                if stderr:
                    print(f"[stderr]\n{stderr}")
                return success
            
            # File operations
            elif action == "file_read":
                path = params.get("path", "")
                success, content = self.files.read_file(path)
                if success:
                    print(f"[file content]\n{content[:1000]}")  # Print first 1000 chars
                    return True
                else:
                    print(f"[error] {content}")
                    return False
            
            elif action == "file_write":
                path = params.get("path", "")
                content = params.get("content", "")
                success, msg = self.files.write_file(path, content)
                print(f"[result] {msg}")
                return success
            
            elif action == "file_list":
                path = params.get("path", ".")
                success, items = self.files.list_directory(path)
                if success:
                    print(f"[directory listing]\n" + "\n".join(items[:50]))
                    return True
                return False
            
            elif action == "file_create":
                path = params.get("path", "")
                content = params.get("content", "")
                success, msg = self.files.create_file(path, content)
                print(f"[result] {msg}")
                return success
            
            elif action == "file_delete":
                path = params.get("path", "")
                success, msg = self.files.delete_file(path)
                print(f"[result] {msg}")
                return success
            
            elif action == "file_move":
                source = params.get("source", "")
                dest = params.get("dest", "")
                success, msg = self.files.move_file(source, dest)
                print(f"[result] {msg}")
                return success
            
            elif action == "file_copy":
                source = params.get("source", "")
                dest = params.get("dest", "")
                success, msg = self.files.copy_file(source, dest)
                print(f"[result] {msg}")
                return success
            
            # Chat/conversation
            elif action == "chat":
                query = params.get("query", command.raw_command)
                response = self.ollama.generate(query)
                if response:
                    print(f"[ollama]\n{response}")
                    return True
                return False
            
            else:
                print(f"[error] Unknown action: {action}")
                return False
        
        except Exception as e:
            print(f"[error] Execution error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def process_input(self, user_input: str) -> Optional[bool]:
        """Process user input and execute command."""
        user_input = user_input.strip()
        if not user_input:
            return None
        
        # Special exit command
        if user_input.lower() in ("exit", "quit", "stop"):
            return False
        
        # Try to parse with Ollama
        intent = self.ollama.parse_command(user_input)
        if intent:
            print(f"[parsed] Action: {intent.action}, Confidence: {intent.confidence:.2f}")
            if intent.confidence < 0.3:
                print("[warning] Low confidence parsing. Result may be incorrect.")
            
            success = await self.execute_command(intent)
            if not success and intent.confidence < 0.5:
                # If command failed and confidence was low, try treating as chat
                print("[fallback] Treating as chat query...")
                chat_intent = CommandIntent(
                    action="chat",
                    parameters={"query": user_input},
                    raw_command=user_input
                )
                await self.execute_command(chat_intent)
        else:
            # Fallback: treat as chat or system command
            print("[fallback] Could not parse command. Trying as chat...")
            chat_intent = CommandIntent(
                action="chat",
                parameters={"query": user_input},
                raw_command=user_input
            )
            await self.execute_command(chat_intent)
        
        return None
    
    async def run_interactive(self):
        """Run interactive command loop."""
        await self.initialize()
        self.running = True
        
        while self.running:
            try:
                user_input = input("\nCommand> ").strip()
                if not user_input:
                    continue
                
                result = await self.process_input(user_input)
                if result is False:
                    break
            
            except KeyboardInterrupt:
                print("\n[system] Interrupted. Exiting...")
                break
            except EOFError:
                break
        
        await self.browser.close()
        print("[system] Shutdown complete.")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultimate Command Execution System")
    parser.add_argument("--model", default="llama3.2", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--command", help="Execute a single command and exit")
    
    args = parser.parse_args()
    
    system = UltimateCommandSystem(
        ollama_model=args.model,
        ollama_url=args.ollama_url
    )
    
    if args.command:
        await system.initialize()
        await system.process_input(args.command)
        await system.browser.close()
    else:
        await system.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())

