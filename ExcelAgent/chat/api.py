import requests
import time
import os


def inference_chat(chat, model, api_url, token, provider="openai", temperature=0.0):
    """
    Unified inference function supporting multiple LLM providers.
    
    Args:
        chat: List of [role, content] tuples
        model: Model name
        api_url: API endpoint URL (None for Gemini SDK, or base URL for OpenAI-compatible APIs)
        token: API key/token (can be env var name or actual key)
        provider: 'gemini', 'openai', 'deepseek', 'claude', 'nvidia', or auto-detected
        temperature: Sampling temperature
    """
    # Resolve API key if it's an environment variable name
    token = _resolve_api_key(token)
    
    # Auto-detect provider from API URL if not explicitly set
    if provider == "gemini" and api_url:
        provider = _detect_provider_from_url(api_url)
    elif not provider or provider == "auto":
        provider = _detect_provider_from_url(api_url) if api_url else "gemini"
    
    provider = provider.lower()
    
    if provider == "gemini" and not api_url:
        return _inference_gemini(chat, model, token, temperature)
    elif provider in ["openai", "deepseek", "nvidia"] or (api_url and provider != "claude"):
        # Use OpenAI SDK for OpenAI-compatible APIs
        return _inference_openai_sdk(chat, model, api_url, token, temperature)
    elif provider == "claude":
        return _inference_claude(chat, model, token, temperature)
    else:
        # Fallback to OpenAI-compatible
        return _inference_openai_sdk(chat, model, api_url, token, temperature)


def _resolve_api_key(api_key):
    """
    Resolve API key from environment variable if it looks like an env var name,
    otherwise return as-is.
    
    Args:
        api_key: API key string or environment variable name
        
    Returns:
        Resolved API key value
    """
    if not api_key:
        return None
    
    # If it looks like an environment variable name (all caps, underscores, no special chars)
    # and exists in environment, use it
    if api_key.isupper() and '_' in api_key:
        env_value = os.environ.get(api_key)
        if env_value:
            return env_value
    
    # Otherwise, treat as direct API key
    return api_key


def _detect_provider_from_url(api_url):
    """
    Auto-detect provider from API URL.
    
    Args:
        api_url: API endpoint URL
        
    Returns:
        Detected provider name
    """
    if not api_url:
        return "gemini"
    
    api_url_lower = api_url.lower()
    
    if "anthropic.com" in api_url_lower or "claude" in api_url_lower:
        return "claude"
    elif "openai.com" in api_url_lower:
        return "openai"
    elif "deepseek.com" in api_url_lower:
        return "deepseek"
    elif "nvidia.com" in api_url_lower or "integrate.api.nvidia.com" in api_url_lower:
        return "nvidia"
    elif "gemini" in api_url_lower or "google" in api_url_lower:
        return "gemini"
    else:
        # Default to OpenAI-compatible for unknown URLs
        return "openai"


def _normalize_api_url(api_url):
    """
    Normalize API URL to ensure it's in the correct format for OpenAI SDK.
    OpenAI SDK expects base_url like 'https://api.example.com/v1'
    (without /chat/completions suffix).
    
    Args:
        api_url: Raw API URL
        
    Returns:
        Normalized base URL
    """
    if not api_url:
        return None
    
    # Remove trailing slashes
    api_url = api_url.rstrip('/')
    
    # If URL ends with /chat/completions, remove it
    if api_url.endswith('/chat/completions'):
        api_url = api_url[:-len('/chat/completions')]
    
    # If URL ends with /v1/chat/completions, remove /chat/completions
    if api_url.endswith('/v1/chat/completions'):
        api_url = api_url[:-len('/chat/completions')]
    
    # Ensure /v1 is present if not already
    if not api_url.endswith('/v1'):
        # Check if there's already a version path
        if '/v1' not in api_url:
            api_url = api_url.rstrip('/') + '/v1'
    
    return api_url


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


def _inference_openai_sdk(chat, model, api_url, token, temperature):
    """
    Inference using OpenAI SDK for OpenAI-compatible APIs (OpenAI, DeepSeek, NVIDIA, etc.).
    Falls back to requests if OpenAI SDK is not available.
    """
    try:
        from openai import OpenAI
    except ImportError:
        # Fallback to requests-based implementation if OpenAI SDK not available
        return _inference_openai_requests(chat, model, api_url, token, temperature)
    
    # Normalize API URL for OpenAI SDK
    base_url = _normalize_api_url(api_url) if api_url else None
    
    # Initialize OpenAI client
    client_kwargs = {
        "api_key": token,
    }
    if base_url:
        client_kwargs["base_url"] = base_url
    
    client = OpenAI(**client_kwargs)
    
    # Convert chat format to OpenAI messages format
    messages = []
    for role, content in chat:
        # Extract text from content
        if isinstance(content, list):
            text = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])
        else:
            text = content
        messages.append({"role": role, "content": text})
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2048,
                temperature=temperature,
                seed=1234
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI SDK Error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise


def _inference_openai_requests(chat, model, api_url, token, temperature):
    """
    Fallback inference using requests for OpenAI-compatible APIs.
    Used when OpenAI SDK is not available.
    """
    # Normalize API URL - ensure it has /chat/completions endpoint
    if api_url:
        api_url_normalized = _normalize_api_url(api_url)
        if not api_url_normalized.endswith('/chat/completions'):
            api_url_normalized = api_url_normalized.rstrip('/') + '/chat/completions'
    else:
        api_url_normalized = "https://api.openai.com/v1/chat/completions"
    
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
            res = requests.post(api_url_normalized, headers=headers, json=data, timeout=60)
            res.raise_for_status()
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
