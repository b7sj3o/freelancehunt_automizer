import json
from core.config import settings
from openai import OpenAI
from core.loggers import ai_logger as logger

class AI:
    @classmethod
    def prompt_to_ai(cls, prompt: str, max_tries: int = 3) -> str | None:
        completion = settings.client.chat.completions.create(
            model=settings.OPENROUTER_AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": settings.AI_SYSTEM_CONTENT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=settings.AI_TEMPERATURE,
            top_p=settings.AI_TOP_P,
            max_tokens=settings.AI_MAX_TOKENS,

        )
        result = completion.choices[0].message.content

        if not result:
            if max_tries > 0:
                return cls.prompt_to_ai(prompt, max_tries - 1)
            else:
                logger.error(f"AI returned an empty response")
                return None

            return result


    