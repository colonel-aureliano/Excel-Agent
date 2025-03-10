from openai import OpenAI

import google.generativeai as genai

from ..utils.utils import logger
from typing import Union, List, Dict

def call_genaiapi(SYSTEM_PROMPT: str, 
                  CHATS: List[Dict],
                  ai_client: Union[genai, OpenAI],  # type: ignore
                  temp: float=0.7, 
                  genai_model: str="openai"):

    genai_model = genai_model.lower()

    if genai_model.startswith("openai"):
        logger.info("Calling OpenAI API")

        messages = [
            {"role": "developer", "content": SYSTEM_PROMPT}
        ]
        messages.extend(CHATS)

        response = ai_client.chat.completions.create(
            model=genai_model,
            messages=messages, 
            temperature=temp
        )

        return response.choices[0].message.content
    
    elif genai_model.startswith("gemini"):
        logger.info("Calling Google GenAI API")
        
        model = ai_client.GenerativeModel(genai_model, 
                                          system_instruction=SYSTEM_PROMPT)
        prev_chat = model.start_chat(
                        history=CHATS[-1], 
                        generation_config=genai.types.GenerationConfig(candidate_count=1, temperature=temp)
                    )
        
        response = prev_chat.send_message(CHATS[-1]["parts"])
        
        return response.text

    elif genai_model.startswith("deepseek"):
        #TODO
        pass
    
    else:
        raise ValueError("Invalid API Spec")
