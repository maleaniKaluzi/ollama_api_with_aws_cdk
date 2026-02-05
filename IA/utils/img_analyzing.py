import requests
import json
import re
from prompts.image_prompt import ImagePrompt
# from prompts.video_prompt import VideoPrompt

OLLAMA_URL = "http://localhost:11434" 
MODEL = "llava"

def describe_image(image_bytes, type_media: str):
    if type_media == 'image':
        full_prompt = ImagePrompt.get_prompt()
    # elif type_media == 'video':
    #     full_prompt = VideoPrompt.get_prompt()
    else:
        full_prompt = ImagePrompt.get_prompt()

    try:
        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "images": [image_bytes],
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0
                }
            },
        )

        if res.status_code != 200:
            return {"description": f"Ollama Error: {res.text}"}

        content_str = res.json().get("response", "")
        match = re.search(r"\{.*\}", content_str, re.S)
        if not match:
            return {"description": f"No JSON found in response: {content_str}"}

        json_str = match.group()
        parsed = json.loads(json_str)
        return {"description": parsed}
        # return parsed

    except Exception as e:
        return {"description": f"API Error: {str(e)}"}
