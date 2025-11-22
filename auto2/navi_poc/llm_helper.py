"""LLM integration using Ollama for intelligent workflow understanding."""

import json
from typing import Dict, List, Optional

try:
    import ollama
except ImportError as exc:
    raise SystemExit(
        "Missing dependency 'ollama'. Install it with `pip install ollama`."
    ) from exc


# Default model - can be overridden
DEFAULT_MODEL = "llama3.2:latest"


def set_default_model(model: str) -> None:
    """Set the default Ollama model to use."""
    global DEFAULT_MODEL
    DEFAULT_MODEL = model


def check_ollama_connection(model: Optional[str] = None) -> bool:
    """
    Check if Ollama is running and the specified model is available.
    
    Returns True if connection is successful, False otherwise.
    """
    model = model or DEFAULT_MODEL
    try:
        # Try a simple request to check if Ollama is running
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "test"}],
        )
        return True
    except Exception:
        return False


def find_best_workflow_llm(
    command: str,
    workflows: List[Dict],
    model: Optional[str] = None,
) -> Optional[Dict]:
    """
    Use LLM to semantically match user command with workflows.
    
    Returns the best matching workflow based on semantic understanding.
    """
    if not workflows:
        return None
    
    model = model or DEFAULT_MODEL
    
    # Build context about available workflows
    workflow_summaries = []
    for idx, workflow in enumerate(workflows):
        name = workflow.get("name", "Unnamed")
        description = workflow.get("description", "")
        event_count = len(workflow.get("events", []))
        workflow_summaries.append(
            f"Workflow {idx}: '{name}' - {description} ({event_count} events)"
        )
    
    workflows_text = "\n".join(workflow_summaries)
    
    prompt = f"""You are a workflow automation assistant. Given a user's command and a list of available workflows, determine which workflow best matches the user's intent.

Available workflows:
{workflows_text}

User command: "{command}"

Analyze the user's command and determine which workflow (by index) best matches their intent. Consider:
- Semantic meaning, not just keywords
- User's actual goal
- Context and purpose

Respond with ONLY a JSON object in this exact format:
{{
    "workflow_index": <number>,
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>"
}}

If no workflow matches well (confidence < 0.3), set workflow_index to -1.
"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that matches user commands to workflows. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        
        content = response["message"]["content"].strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        workflow_idx = result.get("workflow_index", -1)
        confidence = result.get("confidence", 0.0)
        
        if workflow_idx < 0 or workflow_idx >= len(workflows) or confidence < 0.3:
            return None
        
        return {
            "workflow": workflows[workflow_idx],
            "confidence": confidence,
            "reasoning": result.get("reasoning", ""),
        }
        
    except Exception as e:
        print(f"LLM matching error: {e}")
        return None


def analyze_workflow_events(events: List[Dict], model: Optional[str] = None) -> str:
    """
    Analyze recorded events with rich context and generate an intelligent description.
    
    Uses window context, OCR text, and application information to understand
    what the workflow actually does, not just clicks and movements.
    
    Returns a natural language description of the workflow's actions.
    """
    if not events:
        return "Empty workflow with no events."
    
    model = model or DEFAULT_MODEL
    
    # Extract rich context from events
    event_summary = []
    click_count = 0
    key_count = 0
    window_changes = []
    applications_used = set()
    ocr_texts = []
    key_actions = []
    
    # Analyze events with context
    for event in events[:200]:  # Analyze more events for better context
        event_type = event.get("type", "")
        window = event.get("window", {})
        
        # Track applications used
        if window:
            app = window.get("app", "")
            title = window.get("title", "")
            if app:
                applications_used.add(app)
            if title and event_type in ["window_change", "recording_start"]:
                window_changes.append(f"{app}: {title}")
        
        # Analyze clicks with context
        if event_type == "mouse_click":
            click_count += 1
            button = event.get("button", "left")
            pressed = event.get("pressed", True)
            
            if not pressed:  # On release, we have full context
                ocr = event.get("ocr_text", "")
                window_info = f" in {window.get('app', 'unknown app')}" if window else ""
                
                action_desc = f"Click {button} button{window_info}"
                if ocr:
                    action_desc += f" (visible text: '{ocr[:50]}...')"
                    ocr_texts.append(ocr)
                
                event_summary.append(action_desc)
        
        # Analyze key presses with context
        elif event_type == "key_press":
            key_count += 1
            key = event.get("key", "")
            ocr = event.get("ocr_text", "")
            
            if key in ["Key.enter", "Key.tab", "Key.space"]:
                window_info = f" in {window.get('app', 'unknown app')}" if window else ""
                action_desc = f"Press {key}{window_info}"
                if ocr:
                    action_desc += f" (context: '{ocr[:50]}...')"
                key_actions.append(action_desc)
        
        # Track window changes
        elif event_type == "window_change":
            app = window.get("app", "")
            title = window.get("title", "")
            if app and title:
                window_changes.append(f"Switched to {app}: {title}")
    
    # Build comprehensive summary
    summary_parts = [
        f"Total events: {len(events)}",
        f"- Mouse clicks: {click_count}",
        f"- Key presses: {key_count}",
    ]
    
    if applications_used:
        summary_parts.append(f"- Applications used: {', '.join(applications_used)}")
    
    if window_changes:
        summary_parts.append(f"- Window changes: {len(window_changes)}")
        summary_parts.append(f"  Windows: {'; '.join(window_changes[:5])}")
    
    if ocr_texts:
        summary_parts.append(f"- Captured text from screen: {len(ocr_texts)} instances")
        # Show sample OCR text
        unique_texts = list(set(ocr_texts))[:5]
        for text in unique_texts:
            if text:
                summary_parts.append(f"  Text: '{text[:60]}...'")
    
    summary_parts.append("\nKey actions performed:")
    summary_parts.extend(event_summary[:30])  # Show more actions with context
    
    summary_text = "\n".join(summary_parts)
    
    prompt = f"""Analyze this workflow automation sequence with rich context and provide a clear, detailed description of what the user is actually doing.

The workflow includes:
- Application context (which apps are being used)
- Window titles and changes
- Text visible on screen (OCR)
- Mouse clicks and keyboard input

Workflow analysis:
{summary_text}

Based on this context-rich data, provide a detailed natural language description (2-3 sentences) of:
1. What application(s) the user is working with
2. What specific task or action they are performing
3. What the workflow accomplishes

Focus on understanding the USER'S INTENT and the ACTUAL TASK being performed, not just the technical actions.

Description:"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing user workflows. You understand applications, user interfaces, and can infer user intent from context-rich automation data including window titles, OCR text, and application names.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        
        return response["message"]["content"].strip()
        
    except Exception as e:
        print(f"Workflow analysis error: {e}")
        return "Workflow automation sequence"


def generate_workflow_name(description: str, model: Optional[str] = None) -> str:
    """
    Generate a concise workflow name based on description.
    
    Returns a short, descriptive name.
    """
    model = model or DEFAULT_MODEL
    
    prompt = f"""Generate a short, descriptive name (2-4 words max) for a workflow described as: "{description}"

Name:"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You generate concise, descriptive names for automation workflows.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        
        name = response["message"]["content"].strip()
        # Clean up any quotes or extra formatting
        name = name.strip('"\'')
        return name[:50]  # Limit length
        
    except Exception as e:
        print(f"Name generation error: {e}")
        # Fallback to simple name
        words = description.split()[:3]
        return "_".join(words).lower()[:30]

