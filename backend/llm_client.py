"""Multi-LLM client supporting OpenAI, Claude, and Google Gemini."""
import os
import logging
import json
from typing import Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    SYSTEM_PROMPT = """You are a Python code assistant. Analyze the code issue and provide a fix suggestion.

CRITICAL: You must return ONLY a valid JSON object with this EXACT structure:
{
  "title": "Brief fix description (max 50 chars)",
  "description": "Why this matters (1-2 sentences)",
  "patch": "Unified diff format patch (see example below)",
  "risks": "Potential side effects (1 sentence)"
}

PATCH FORMAT EXAMPLE:
For removing an unused variable on line 5:
```
--- a/file.py
+++ b/file.py
@@ -4,5 +4,4 @@
     total = 0
-    unused_var = 42
     for item in items:
```

IMPORTANT RULES:
1. The patch MUST be in unified diff format
2. Use actual line numbers from the code
3. Show context lines (lines before and after the change)
4. For removing a line: prefix with '-'
5. For adding a line: prefix with '+'
6. For context lines: prefix with ' ' (space)
7. Keep the fix minimal - only change what's necessary
8. Do NOT include markdown code fences in the patch field

Be precise and actionable."""
    
    @abstractmethod
    def generate_fix(
        self, 
        code_snippet: str, 
        line: int, 
        message: str, 
        rule_id: str
    ) -> Optional[dict]:
        """Generate a fix suggestion for a code issue."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client."""
    
    def __init__(self):
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        logger.info(f"Initialized OpenAI client with model: {self.model}")
    
    def generate_fix(
        self, 
        code_snippet: str, 
        line: int, 
        message: str, 
        rule_id: str
    ) -> Optional[dict]:
        user_prompt = f"""Code snippet:
```python
{code_snippet}
```

Pylint diagnostic:
- Line {line}: {message} ({rule_id})

Generate a fix."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            fix_data = json.loads(response.choices[0].message.content)
            logger.info(f"Generated fix for {rule_id}: {fix_data.get('title', 'N/A')}")
            return fix_data
            
        except Exception as e:
            logger.error(f"OpenAI API failed: {e}")
            return None


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude client."""
    
    def __init__(self):
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        logger.info(f"Initialized Claude client with model: {self.model}")
    
    def generate_fix(
        self, 
        code_snippet: str, 
        line: int, 
        message: str, 
        rule_id: str
    ) -> Optional[dict]:
        user_prompt = f"""Analyze this Python code issue and provide a fix.

CODE:
```python
{code_snippet}
```

ISSUE:
- Line {line}: {message}
- Rule ID: {rule_id}

TASK:
Generate a minimal fix for this issue. Return a JSON object with:
1. title: Short description of the fix
2. description: Why this fix is needed
3. patch: Unified diff showing the exact change (use actual line numbers)
4. risks: Any potential side effects

Focus on the specific issue. Keep changes minimal."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.1,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Claude returns text content, need to parse JSON
            content = response.content[0].text
            
            # Try to extract JSON (if wrapped in other text)
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            fix_data = json.loads(content)
            logger.info(f"Generated fix for {rule_id}: {fix_data.get('title', 'N/A')}")
            return fix_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Claude API returned invalid JSON: {content[:200]}")
            return None
        except Exception as e:
            logger.error(f"Claude API failed: {e}")
            return None


class GoogleClient(BaseLLMClient):
    """Google Gemini client."""
    
    def __init__(self):
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 500,
            }
        )
        logger.info(f"Initialized Google client with model: {self.model_name}")
    
    def generate_fix(
        self, 
        code_snippet: str, 
        line: int, 
        message: str, 
        rule_id: str
    ) -> Optional[dict]:
        prompt = f"""{self.SYSTEM_PROMPT}

Code snippet:
```python
{code_snippet}
```

Pylint diagnostic:
- Line {line}: {message} ({rule_id})

Generate a fix."""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON from response
            content = response.text
            fix_data = json.loads(content)
            logger.info(f"Generated fix for {rule_id}: {fix_data.get('title', 'N/A')}")
            return fix_data
            
        except Exception as e:
            logger.error(f"Google API failed: {e}")
            return None


class LLMClient:
    """Factory class for creating LLM clients based on configuration."""
    
    def __new__(cls):
        """Create the appropriate LLM client based on LLM_PROVIDER env var."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if provider == "openai":
            return OpenAIClient()
        elif provider == "claude":
            return ClaudeClient()
        elif provider == "google":
            return GoogleClient()
        else:
            logger.warning(f"Unknown LLM provider '{provider}', defaulting to OpenAI")
            return OpenAIClient()
