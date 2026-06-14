from typing import Optional

from anthropic import Anthropic
from openai import AsyncOpenAI

from app.config import settings


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"
    
    async def summarize_call(
        self,
        call_transcript: str,
        call_metadata: Optional[dict] = None,
    ) -> dict:
        prompt = f"""You are a professional call summarizer. Analyze the following call transcript and provide:
        1. A concise summary (2-3 sentences)
        2. Key points (bullet list)
        3. Action items (if any)
        4. Sentiment (positive, neutral, or negative)
        
        Transcript:
        {call_transcript}
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional call summarizer."},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "call_summary",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "key_points": {"type": "array", "items": {"type": "string"}},
                            "action_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string"},
                                        "assignee": {"type": "string"},
                                        "due_date": {"type": "string"},
                                    },
                                },
                            },
                            "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                        },
                    },
                },
            },
        )
        
        return response.choices[0].message.content


class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    async def summarize_call(
        self,
        call_transcript: str,
        call_metadata: Optional[dict] = None,
    ) -> dict:
        prompt = f"""You are a professional call summarizer. Analyze the following call transcript and provide:
        1. A concise summary (2-3 sentences)
        2. Key points (bullet list)
        3. Action items (if any)
        4. Sentiment (positive, neutral, or negative)
        
        Transcript:
        {call_transcript}
        """
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        
        return response.content[0].text
