import os
import json
import re

class WildPromptorAI:
    @staticmethod
    def INPUT_TYPES():
        return {
            "required": {"keywords": ("STRING", {"multiline": True})},
            "optional": {"max_length": ("INT", {"default": 512, "min": 50, "max": 1000})}
        }
    def __init__(self):
        self.load_config()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            print("Config file not found. Please create a config.json file.")
            self.config = {}

    def clean_prompt(self, text):
        text = re.sub(r'^.*?:\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = ' '.join(text.split())
        unwanted_phrases = ['style', 'additional detail', 'artistic style', 'optional details', 'generate an image of','Image Description:', 'The image displayed is', 'The image shows', 'In this image', 'The scene depicts', 'This image portrays', 'Visualize a scene where']
        for phrase in unwanted_phrases:
            text = re.sub(rf'\b{phrase}\b', '', text, flags=re.IGNORECASE)
        return text.strip()

    def format_prompt(self, keywords):
        return f"Based on these keywords: {keywords}\nCreate a single, concise paragraph describing an image. Focus only on the visual elements without mentioning prompt creation or image generation. Avoid sections, bullet points, or style suggestions."

    def generate_prompt(self, keywords, max_length=512):
        raise NotImplementedError("Subclasses must implement generate_prompt method")