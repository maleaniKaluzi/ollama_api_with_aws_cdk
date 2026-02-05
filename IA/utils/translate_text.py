import requests, json
# from .prompts.translate_prompt import Translate

OLLAMA_URL = "http://localhost:11434"
MODEL = "translategemma:4b"


def translate(text,language="french"):
    # final_prompt = Translate.get_translate_prompt(text)
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"Translate the following text to {language}. Output ONLY the translation: \n\n{text}",
                }
            ],
            "stream":False,
        },
       
        timeout=500,
    )

    try:
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print("Error parsing JSON:", e)
        return {"error": e}
        # json_str = response.text.split('{', 1)[-1].rsplit('}', 1)[0] + '}'
        # return json.loads('{' + json_str)