import os
import random
import json
from typing import Tuple, List, Dict, Any

class WildPromptorAllInOne:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "🧪AILab/🧿WildPromptor/🔀Promptor"

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config['data_path'])

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def read_file_options(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {
            "required": {},
            "optional": {
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "allow_duplicates": ("BOOLEAN", {"default": True}),
            }
        }

        for folder in self.config['folders']:
            folder_path = os.path.join(self.data_path, folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('.txt'):
                        original_name = os.path.splitext(file)[0]
                        cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
                        file_path = os.path.join(folder_path, file)
                        options = self.read_file_options(file_path)
                        item_count = len(options)
                        display_name = f"{folder} - {cleaned_name} [{item_count}]"
                        inputs["optional"][display_name] = (["❌disabled", "🎲Random", "🔢ordered"] + options, {"default": "❌disabled"})

        return inputs

    def process_prompt(self, batch_size = 1, seed= 0, allow_duplicates= True, **kwargs):
        random.seed(seed)
        all_prompts = []

        for i in range(batch_size):
            prompt_parts = []
            for key, value in kwargs.items():
                if key in ["batch_size", "seed", "allow_duplicates"]:
                    continue
                if value == "❌disabled":
                    continue
                elif value == "🎲Random":
                    folder, cleaned_name = key.split(' - ', 1)
                    original_name = self.get_original_filename(folder, cleaned_name.split(' [')[0])
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if options:
                        if allow_duplicates:
                            prompt_parts.append(random.choice(options))
                        else:
                            prompt_parts.append(random.sample(options, 1)[0])
        
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