from WildPromptorAI import WildPromptorAI
import google.generativeai as genai

class WildPromptorGemini(WildPromptorAI):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "🧪 AILab/🤖 AI Generator"
    
    @classmethod
    def INPUT_TYPES(cls):
        default_api_key = cls.load_default_api_key()
        return {
            "required": {
                "keywords": ("STRING", {"multiline": True}),
                "max_length": ("INT", {"default": 256, "min": 1, "max": 1024}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.1}),
                "api_key": ("STRING", {"default": default_api_key, "multiline": False}),
            },
        }
    
    @classmethod
    def load_default_api_key(cls):
        try:
            return cls().config['gemini']['api_key']
        except:
            return "Enter your API key here"

    def __init__(self):
        super().__init__()

    def setup_genai(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config['gemini']['model_id'])

    def generate_prompt(self, keywords, max_length=256, temperature=0.7, api_key=""):
        if not api_key:
            api_key = self.config['gemini']['api_key']
        self.setup_genai(api_key)
        ai_prompt = self.format_prompt(keywords)
        
        try:
            response = self.model.generate_content(
                ai_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_length,
                    temperature=temperature
                )
            )
            generated_prompt = response.text
            generated_prompt = self.clean_prompt(generated_prompt)
            
            if len(generated_prompt) > max_length:
                generated_prompt = generated_prompt[:max_length]
            
            print(f"🤖 Gemini prompt:\n{generated_prompt}")
            return (generated_prompt,)
        except genai.types.generation_types.GenerationException as e:
            print(f"Generation error: {str(e)}")
            return ("Error: Unable to generate prompt",)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return ("Error: Unexpected issue occurred",)

NODE_CLASS_MAPPINGS = {"WildPromptorGemini": WildPromptorGemini}
NODE_DISPLAY_NAME_MAPPINGS = {"WildPromptorGemini": "Gemini 🤖"}