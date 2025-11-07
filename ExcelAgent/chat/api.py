import requests
import time
import os


def inference_chat(chat, model, api_url, token, provider="openai", temperature=0.0):
    """
    Unified inference function supporting multiple LLM providers.
    
    Args:
        chat: List of [role, content] tuples
        model: Model name
        api_url: API endpoint URL (None for Gemini SDK)
        token: API key/token
        provider: 'gemini', 'openai', 'deepseek', 'claude'
        temperature: Sampling temperature
    """
    provider = provider.lower()
    
    if provider == "gemini":
        return _inference_gemini(chat, model, token, temperature)
    elif provider in ["openai", "deepseek"]:
        return _inference_openai_compatible(chat, model, api_url, token, temperature)
    elif provider == "claude":
        return _inference_claude(chat, model, token, temperature)
    else:
        # Fallback to OpenAI-compatible
        return _inference_openai_compatible(chat, model, api_url, token, temperature)


def _inference_gemini(chat, model, token, temperature):
    """Inference using Google Gemini API via google-generativeai SDK."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai package required for Gemini. Install: pip install google-generativeai")
    
    genai.configure(api_key=token)
    
    # Convert chat format to Gemini format
    # chat is list of [role, content] where content is list of dicts with 'type' and 'text'
    system_instruction = None
    messages = []
    
    for role, content in chat:
        # Extract text from content
        if isinstance(content, list):
            text = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])
        else:
            text = content
            
        if role == "system":
            system_instruction = text
        else:
            # Gemini uses 'user' and 'model' roles
            gemini_role = "model" if role == "assistant" else "user"
            messages.append({"role": gemini_role, "parts": [text]})
    
    # Create model with system instruction
    model_instance = genai.GenerativeModel(
        model, 
        system_instruction=system_instruction
    )
    
    # Start chat with history
    chat_session = model_instance.start_chat(history=messages[:-1] if len(messages) > 1 else [])
    
    # Send the last message
    last_message = messages[-1]["parts"][0] if messages else ""
    
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=2048,
    )
    
    try:
        response = chat_session.send_message(last_message, generation_config=generation_config)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise


def _inference_openai_compatible(chat, model, api_url, token, temperature):
    """Inference using OpenAI-compatible API (OpenAI, DeepSeek, etc.)."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Convert chat format to OpenAI messages format
    messages = []
    for role, content in chat:
        # Extract text from content
        if isinstance(content, list):
            text = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])
        else:
            text = content
        messages.append({"role": role, "content": text})

    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": temperature,
        "seed": 1234
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.post(api_url, headers=headers, json=data, timeout=60)
            res_json = res.json()
            res_content = res_json['choices'][0]['message']['content']
            return res_content
        except Exception as e:
            print(f"Network Error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                try:
                    print(f"Response: {res.json()}")
                except:
                    print("Request Failed - no response available")
                raise


def _inference_claude(chat, model, token, temperature):
    """Inference using Anthropic Claude API."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": token,
        "anthropic-version": "2023-06-01"
    }
    
    # Convert chat format to Claude format
    system_message = None
    messages = []
    
    for role, content in chat:
        # Extract text from content
        if isinstance(content, list):
            text = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])
        else:
            text = content
            
        if role == "system":
            system_message = text
        else:
            messages.append({"role": role, "content": text})
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": temperature
    }
    
    if system_message:
        data["system"] = system_message
    
    try:
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60
        )
        res_json = res.json()
        return res_json['content'][0]['text']
    except Exception as e:
        print(f"Claude API Error: {e}")
        raise
