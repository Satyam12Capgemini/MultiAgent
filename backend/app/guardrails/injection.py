import re
from typing import Tuple, List

INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions', re.IGNORECASE),
    re.compile(r'system\s+override', re.IGNORECASE),
    re.compile(r'you\s+are\s+now\s+(?:in\s+developer\s+mode|dan|unrestricted)', re.IGNORECASE),
    re.compile(r'disregard\s+(?:all\s+)?rules', re.IGNORECASE),
    re.compile(r'bypass\s+safety', re.IGNORECASE),
    re.compile(r'reveal\s+(?:your\s+)?system\s+prompt', re.IGNORECASE),
    re.compile(r'print\s+(?:all\s+)?hidden\s+text', re.IGNORECASE),
]

class PromptInjectionDetector:
    def detect(self, text: str) -> Tuple[bool, List[str]]:
        flagged_patterns = []
        for pattern in INJECTION_PATTERNS:
            if pattern.search(text):
                flagged_patterns.append(pattern.pattern)
        return len(flagged_patterns) > 0, flagged_patterns

injection_detector = PromptInjectionDetector()
