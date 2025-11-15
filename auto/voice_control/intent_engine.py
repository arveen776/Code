from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


@dataclass
class IntentResult:
    """Normalized representation of a parsed command."""

    name: str
    confidence: float
    source: str
    slots: Dict[str, str]

    @property
    def is_confident(self) -> bool:
        return self.confidence >= 0.55


class IntentEngine:
    """Maps natural-language commands to browser intents."""

    def __init__(self, enable_llm: bool = True) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self._llm_enabled = (
            enable_llm and api_key and OpenAI is not None  # type: ignore[truthy-functional]
        )
        self._client = OpenAI(api_key=api_key) if self._llm_enabled else None

    def detect(self, utterance: str) -> Optional[IntentResult]:
        utterance = utterance.strip().lower()
        if not utterance:
            return None

        result = self._match_rules(utterance)
        if result and result.is_confident:
            return result

        if self._llm_enabled:
            llm_result = self._llm_intent(utterance)
            if llm_result:
                return llm_result

        return result

    # ------------------------------------------------------------------
    # Rule-based intents
    # ------------------------------------------------------------------

    def _match_rules(self, utterance: str) -> Optional[IntentResult]:
        patterns = {
            "scroll_down": r"(scroll|move)\s+(down|lower)",
            "scroll_up": r"(scroll|move)\s+(up|higher)",
            "go_back": r"\b(back|previous)\b",
            "go_forward": r"\bforward\b",
            "refresh": r"\b(refresh|reload)\b",
            "new_tab_site": r"(open|start).*(new\s+tab|another tab)\s+(?:for\s+)?(?P<url>[\w\.\- ]+)$",
            "new_tab": r"(open|start).*(new\s+tab|another tab)",
            "close_tab": r"(close|kill)\s+(this|the)\s+tab",
            "goto_url": r"(go|navigate).*(?:to|into)\s+(?P<url>[\w\.\-:/]+)",
            "stop": r"\b(stop listening|exit|quit)\b",
        }

        for name, pattern in patterns.items():
            match = re.search(pattern, utterance)
            if not match:
                continue

            slots = match.groupdict()
            confidence = 0.75 if slots else 0.65
            return IntentResult(
                name=name,
                confidence=confidence,
                source="rules",
                slots=slots,
            )

        return None

    # ------------------------------------------------------------------
    # LLM intent fallback
    # ------------------------------------------------------------------

    def _llm_intent(self, utterance: str) -> Optional[IntentResult]:
        if not self._client:
            return None

        prompt = (
            "You are an intent classifier for browser voice commands. "
            "Supported intents: scroll_down, scroll_up, go_back, go_forward, "
            "refresh, new_tab, close_tab, goto_url, stop, noop. "
            "Return JSON with fields intent, confidence (0-1), slots dict."
        )

        response = self._client.responses.create(  # type: ignore[union-attr]
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": utterance,
                },
            ],
            response_format={"type": "json_schema", "json_schema": self._schema()},
            temperature=0.0,
        )

        message = None
        try:
            message = response.output[0].content[0].text  # type: ignore[index]
        except (AttributeError, IndexError):
            # Try fallbacks that exist in older SDK builds
            message = getattr(response, "output_text", None)

        if not message:
            return None

        try:
            payload = json.loads(message)
        except (json.JSONDecodeError, TypeError):
            return None

        intent = payload.get("intent")
        if not intent or intent == "noop":
            return None

        return IntentResult(
            name=intent,
            confidence=float(payload.get("confidence", 0.5)),
            source="llm",
            slots=payload.get("slots", {}),
        )

    @staticmethod
    def _schema() -> Dict[str, object]:
        return {
            "name": "IntentResponse",
            "schema": {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "confidence": {"type": "number"},
                    "slots": {"type": "object", "additionalProperties": {"type": "string"}},
                },
                "required": ["intent", "confidence", "slots"],
            },
        }


