import requests

def llm_chat_stream(query, template, model_name, xinference_url, max_tokens=128):
    """
    用户聊天
    :param max_tokens: LLM最大生成长度，字段多时要调大
    """
    prompt = template.format(question=query, context="")
    payload = {
        "model": model_name,
        "prompt": prompt,
        "temperature": 0.8,
        "repetition_penalty": 1.35,
        "max_tokens": max_tokens,   # 支持自定义
        "stream": True,
    }
    try:
        with requests.post(xinference_url, json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()
            partial_reply = ""
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    line_content = line[len("data:"):].strip()
                    if line_content == "[DONE]":
                        break
                    import json
                    data = json.loads(line_content)
                    delta = data.get("choices", [{}])[0].get("text", "")
                    partial_reply += delta
                    yield partial_reply
    except Exception as e:
        yield f"请求出错: {e}"
