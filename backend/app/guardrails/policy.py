import re
from typing import Tuple, Optional

class PolicyEnforcer:
    def sanitize_output(self, text: str, has_refund_tool_result: bool = False) -> str:
        """
        Ensures the model doesn't leak internal tool calls or promise refunds if tool wasn't run.
        """
        cleaned = text

        # Strip internal action JSON artifacts if leaked
        cleaned = re.sub(r'```json\s*\{\s*"action":.*?\}\s*```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'\{\s*"action":\s*"[^"]+".*?\}', '', cleaned, flags=re.DOTALL)

        # Strip unverified refund promises
        if not has_refund_tool_result:
            if re.search(r'(?:I\s+have|I\'ve)\s+processed\s+(?:your\s+)?refund', cleaned, re.IGNORECASE):
                cleaned = re.sub(
                    r'(?:I\s+have|I\'ve)\s+processed\s+(?:your\s+)?refund',
                    'I have reviewed your refund request',
                    cleaned,
                    flags=re.IGNORECASE
                )

        return cleaned.strip()

policy_enforcer = PolicyEnforcer()
