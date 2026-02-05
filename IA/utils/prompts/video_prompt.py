class VideoPrompt:
    @staticmethod
    def get_prompt(tags=[]):
        list_tags = [tag.get("name") for tag in tags]
        return f"""
          You are a video analysis agent for VIRUNGA. I will provide you with a series of chronological frame descriptions from a video. 
          Analyze the sequence and return ONLY one valid JSON object.

          EXISTING TAG LIST:
          {list_tags}

          STRICT OUTPUT FORMAT:
          {{
            "data": [
              {{
                "title": "<max 8 words>",
                "summary": "<max 40 words, describe the core action over time>",
                "tags": ["tag1","tag2",...],
                "status": "ai_approved" | "ai_rejected",
                "reason": "<max 20 words or empty string>"
              }}
            ]
          }}

          RULES:
          1. JSON only. No chat, no intro.
          2. Summary must synthesize the sequence (e.g., "A ranger follows a gorilla through the bush").
          3. Status: "ai_rejected" if any frame shows poaching, violence, or illegal acts.
        """