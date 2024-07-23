import os
import random
import json
from typing import Tuple, List, Dict, Any

class WildPromptorAllInOne:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "🧪 AILab/🧿 WildPromptor/🔀 Promptor"

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(__file__), self.config['data_path'])

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {
            "required": {},
            "optional": {
                "prompt_count": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

        for folder in self.config['folders']:
            folder_path = os.path.join(self.data_path, folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('.txt'):
                        original_name = os.path.splitext(file)[0]
                        cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
                        display_name = f"{folder} - {cleaned_name}"
                        options = self.read_file_options(os.path.join(folder_path, file))
                        inputs["optional"][display_name] = (["disabled", "🎲 Random"] + options, {"default": "disabled"})

        return inputs

    def read_file_options(self, file_path: str) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

    def process_prompt(self, prompt_count: int = 1, seed: int = 0, **kwargs):
        random.seed(seed)
        all_prompts = []

        for _ in range(prompt_count):
            prompt_parts = []
            for key, value in kwargs.items():
                if key in ["prompt_count", "seed"]:
                    continue
                if value == "disabled":
                    continue
                elif value == "🎲 Random":
                    folder, cleaned_name = key.split(' - ', 1)
                    original_name = self.get_original_filename(folder, cleaned_name)
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if options:
                        prompt_parts.append(random.choice(options))
                else:
                    prompt_parts.append(value)
        
            if prompt_parts:
                all_prompts.append(",".join(prompt_parts))

        for prompt in all_prompts:
            print(f"🔀 WildPromptor All-in-One prompt: {prompt}")

        return (all_prompts,) if all_prompts else ([""],)

    def get_original_filename(self, folder, cleaned_name):
        folder_path = os.path.join(self.data_path, folder)
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt') and cleaned_name in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name

NODE_CLASS_MAPPINGS = {
    "WildPromptorAllInOne": WildPromptorAllInOne
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptorAllInOne": "WildPromptor All-in-One 📋+🔀"
}