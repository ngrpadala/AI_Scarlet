import os
import time
import openai
from llama_cpp import Llama
import scarlet.config as config
import scarlet.memory as memory
import scarlet.logger as logger

# Initialize LLM clients
groq_client = openai.OpenAI(
    api_key=config.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

mistral_client = Llama(
    model_path=os.path.expanduser(
        "~/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    ),
    n_ctx=1024,
    n_threads=4,
    n_gpu_layers=0
)

MISTRAL_MAX_TOKENS = 512  # Safe max for output


def _retry_groq(messages, retries=3):
    last_err = None
    for i in range(1, retries + 1):
        try:
            resp = groq_client.chat.completions.create(
                model="meta-llama/Llama-4-Scout-17B-16E-Instruct",  # Groq 4
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            last_err = e
            print(f"[Groq Error] {i}/{retries}: {e}")
            time.sleep(2 ** i)
    raise last_err


def _trim_for_mistral(messages, max_total_tokens=1024, max_response_tokens=512):
    try:
        from tiktoken import get_encoding
        enc = get_encoding("cl100k_base")
    except ImportError:
        print("[Warning] tiktoken not installed, using fallback length-based trim.")
        enc = None

    total_tokens = 0
    trimmed = []
    max_prompt_tokens = max_total_tokens - max_response_tokens

    for msg in reversed(messages):
        content = msg.get("content", "")
        token_count = len(enc.encode(content)) if enc else len(content) // 4
        if (total_tokens + token_count) > max_prompt_tokens:
            continue
        trimmed.insert(0, msg)
        total_tokens += token_count

    return trimmed


def get_system_prompt(user_role="guest"):
    mood_state = config.mood.get("current", "")
    mood_prompt = config.behavior_rules.get("mood_prompts", {}).get(mood_state, "")
    base_prompt = config.personality.get("sample_prompt", "")
    core_rules = config.behavior_rules.get("core_rules", [])
    behavior_directive = config.personality.get("behavior", {}).get(f"toward_{user_role}", "")
    boundaries = config.personality.get("boundaries", "")

    combined = "\n".join([
        mood_prompt.strip(),
        base_prompt.strip(),
        behavior_directive.strip(),
        "\n".join(core_rules),
        boundaries.strip(),
        f"User: {user_role}"
    ])
    return combined.strip()


def chat_with_model(prompt, user_role="guest", use_groq=None):
    if use_groq is None:
        use_groq = True

    print(f"[LLM] Routing to {'Groq' if use_groq else 'Mistral'}")

    sys_prompt = get_system_prompt(user_role)
    messages = [{"role": "system", "content": sys_prompt}]
    messages += memory.get_conversation_history()
    messages.append({"role": "user", "content": prompt})

    try:
        if use_groq:
            reply = _retry_groq(messages)
        else:
            trimmed = _trim_for_mistral(messages)
            result = mistral_client.create_chat_completion(
                messages=trimmed,
                max_tokens=MISTRAL_MAX_TOKENS,
                temperature=0.7
            )
            reply = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[LLM fallback]:", e)
        try:
            trimmed = _trim_for_mistral(messages)
            result = mistral_client.create_chat_completion(
                messages=trimmed,
                max_tokens=MISTRAL_MAX_TOKENS,
                temperature=0.7
            )
            reply = result["choices"][0]["message"]["content"].strip()
        except Exception as me:
            print("[Mistral Error]:", me)
            reply = "Sorry, I'm having trouble right now."

    logger.log_interaction("user", prompt)
    logger.log_interaction("assistant", reply)
    memory.update_conversation("user", prompt)
    memory.update_conversation("assistant", reply)

    return reply

