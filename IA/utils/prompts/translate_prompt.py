class Translate:
    @staticmethod
    def get_translate_prompt(text=""):
        """Returns the system prompt for Ollama(translategemma:4b) translation."""
        return f"""You are a professional English (en) to french (fr) translator. Your goal is to accurately convey the meaning and nuances of the original English text while adhering to French grammar, vocabulary, and cultural sensitivities.
    Produce only the French translation, without any additional explanations or commentary. Please translate the following English text into French:

    
    {text}
    """

