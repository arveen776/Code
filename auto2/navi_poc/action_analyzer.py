"""Analyze and understand actions at a semantic level."""

from typing import Dict, List, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    ollama = None
    OLLAMA_AVAILABLE = False


class ActionAnalyzer:
    """Understands the semantic meaning of user actions."""
    
    def __init__(self, use_llm: bool = True, model: str = "llama3.2:latest"):
        self.use_llm = use_llm and OLLAMA_AVAILABLE
        self.model = model
    
    def analyze_action(self, event: Dict, previous_events: List[Dict]) -> Dict[str, object]:
        """
        Analyze a single action and extract its semantic meaning.
        
        Returns an enhanced event with semantic information.
        """
        event_type = event.get("type", "")
        enhanced = event.copy()
        
        # Extract semantic information based on event type
        if event_type == "mouse_click":
            enhanced = self._analyze_click(event, previous_events)
        elif event_type in ["key_press", "key_release"]:
            enhanced = self._analyze_keyboard(event, previous_events)
        elif event_type == "mouse_scroll":
            enhanced = self._analyze_scroll(event, previous_events)
        
        return enhanced
    
    def _analyze_click(self, event: Dict, previous_events: List[Dict]) -> Dict:
        """Understand what was clicked."""
        enhanced = event.copy()
        
        x = event.get("x", 0)
        y = event.get("y", 0)
        ocr_text = event.get("ocr_text", "")
        window = event.get("window", {})
        
        # Determine action intent
        intent = "click"
        
        # Analyze OCR text to understand what was clicked
        if ocr_text:
            text_lower = ocr_text.lower()
            
            # Common button patterns
            if any(word in text_lower for word in ["save", "submit", "ok", "confirm"]):
                intent = "click_save_button"
            elif any(word in text_lower for word in ["cancel", "close", "exit"]):
                intent = "click_cancel_button"
            elif any(word in text_lower for word in ["delete", "remove"]):
                intent = "click_delete_button"
            elif any(word in text_lower for word in ["edit", "modify"]):
                intent = "click_edit_button"
            elif any(word in text_lower for word in ["search", "find"]):
                intent = "click_search_button"
            elif any(word in text_lower for word in ["menu", "options", "settings"]):
                intent = "click_menu"
            elif any(word in text_lower for word in ["input", "field", "text"]):
                intent = "click_input_field"
        
        enhanced["intent"] = intent
        enhanced["semantic_target"] = ocr_text if ocr_text else f"element at ({x}, {y})"
        
        # Use LLM for deeper understanding if available
        if self.use_llm and ocr_text:
            enhanced["llm_analysis"] = self._llm_analyze_click(ocr_text, window)
        
        return enhanced
    
    def _analyze_keyboard(self, event: Dict, previous_events: List[Dict]) -> Dict:
        """Understand keyboard input intent."""
        enhanced = event.copy()
        
        key = str(event.get("key", ""))
        window = event.get("window", {})
        
        # Look for text input patterns
        if len(key) == 1 and key.isprintable():
            # Check if we're in a text input context
            recent_clicks = [e for e in previous_events[-5:] if e.get("type") == "mouse_click"]
            if recent_clicks:
                last_click = recent_clicks[-1]
                if "input" in last_click.get("intent", "").lower() or "field" in last_click.get("ocr_text", "").lower():
                    enhanced["intent"] = "type_text"
                    enhanced["semantic_target"] = "text_input_field"
        
        # Special keys
        if key in ["Key.enter", "enter"]:
            enhanced["intent"] = "submit_or_confirm"
        elif key in ["Key.tab", "tab"]:
            enhanced["intent"] = "navigate_next_field"
        elif key in ["Key.escape", "Key.esc", "esc"]:
            enhanced["intent"] = "cancel_or_close"
        
        return enhanced
    
    def _analyze_scroll(self, event: Dict, previous_events: List[Dict]) -> Dict:
        """Understand scroll intent."""
        enhanced = event.copy()
        
        dy = event.get("dy", 0)
        if dy > 0:
            enhanced["intent"] = "scroll_down"
        elif dy < 0:
            enhanced["intent"] = "scroll_up"
        
        return enhanced
    
    def _llm_analyze_click(self, ocr_text: str, window: Dict) -> Optional[str]:
        """Use LLM to understand what was clicked."""
        if not self.use_llm:
            return None
        
        try:
            prompt = f"""Analyze this UI interaction:
- Visible text near click: "{ocr_text}"
- Application: {window.get('app', 'unknown')}
- Window title: {window.get('title', 'unknown')}

What type of UI element was clicked? Provide a brief description (1-2 words):"""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You analyze UI interactions concisely."},
                    {"role": "user", "content": prompt}
                ],
            )
            
            return response["message"]["content"].strip()
        except Exception:
            return None
    
    def understand_workflow(self, events: List[Dict]) -> Dict[str, object]:
        """
        Understand the overall workflow at a high level.
        
        Returns a structured understanding of what the workflow does.
        """
        if not events:
            return {"summary": "Empty workflow", "steps": []}
        
        # Analyze all actions
        analyzed_events = []
        for i, event in enumerate(events):
            previous = analyzed_events[-10:] if analyzed_events else []
            analyzed = self.analyze_action(event, previous)
            analyzed_events.append(analyzed)
        
        # Extract high-level steps
        steps = []
        current_step = None
        
        for event in analyzed_events:
            intent = event.get("intent", "")
            event_type = event.get("type", "")
            
            # Group related actions into steps
            if intent and intent != current_step:
                if current_step:
                    steps.append(current_step)
                current_step = {
                    "action": intent,
                    "target": event.get("semantic_target", ""),
                    "window": event.get("window", {}),
                }
            elif current_step and event_type == "key_press" and len(str(event.get("key", ""))) == 1:
                # Typing continues the current step
                current_step["action"] = "fill_field"
        
        if current_step:
            steps.append(current_step)
        
        # Generate summary
        summary = self._generate_summary(steps, analyzed_events)
        
        return {
            "summary": summary,
            "steps": steps,
            "total_actions": len(events),
            "applications_used": list(set(
                e.get("window", {}).get("app", "unknown") 
                for e in analyzed_events 
                if e.get("window")
            )),
        }
    
    def _generate_summary(self, steps: List[Dict], events: List[Dict]) -> str:
        """Generate a natural language summary of the workflow."""
        if not steps:
            return "Workflow with no identifiable steps"
        
        # Simple summary generation
        step_descriptions = []
        for step in steps[:5]:  # First 5 steps
            action = step.get("action", "")
            target = step.get("target", "")
            if target:
                step_descriptions.append(f"{action} on {target[:30]}")
            else:
                step_descriptions.append(action)
        
        summary = " → ".join(step_descriptions)
        if len(steps) > 5:
            summary += f" ... ({len(steps) - 5} more steps)"
        
        # Use LLM for better summary if available
        if self.use_llm and len(step_descriptions) > 0:
            try:
                llm_summary = self._llm_generate_summary(step_descriptions, events)
                if llm_summary:
                    return llm_summary
            except Exception:
                pass
        
        return summary
    
    def _llm_generate_summary(self, step_descriptions: List[str], events: List[Dict]) -> Optional[str]:
        """Use LLM to generate a natural language summary."""
        if not self.use_llm:
            return None
        
        try:
            apps = list(set(
                e.get("window", {}).get("app", "") 
                for e in events 
                if e.get("window", {}).get("app")
            ))
            
            prompt = f"""Summarize this workflow automation in 1-2 sentences:

Steps performed:
{chr(10).join(f"- {step}" for step in step_descriptions[:10])}

Applications used: {', '.join(apps) if apps else 'unknown'}

Provide a clear, concise description of what this workflow accomplishes:"""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You summarize automation workflows clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
            )
            
            return response["message"]["content"].strip()
        except Exception:
            return None

