import json
from core.config import settings
from openai import OpenAI



class AI:
    @classmethod
    def prompt_to_ai(cls, prompt: str) -> str | None:
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

        try:
            return result
        except json.JSONDecodeError:
            print("=======================")
            print(result)
            print("=======================")
            return

            # if max_tries > 0:
            #     return cls.prompt_to_ai(prompt, max_tries - 1)
            # else:
            #     raise json.JSONDecodeError("Failed to parse JSON", result, 0)

    