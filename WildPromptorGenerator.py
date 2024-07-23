import os
import random
import json
from typing import Tuple, List, Dict, Any

class AllInOneList:
    RETURN_TYPES = ("DPROMPT_DATA",)
    RETURN_NAMES = ("selected_options",)
    FUNCTION = "select_options"
    CATEGORY = "🧪 AILab/🧿 WildPromptor/📋 Prompts"

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(__file__), self.config['data_path'])
        self.file_cache = {}

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {"required": {}, "optional": {}}
        
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
        if file_path in self.file_cache:
            return self.file_cache[file_path]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                options = [line.strip() for line in file if line.strip()]
            self.file_cache[file_path] = options
            return options
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

    def select_options(self, **kwargs):
        selected_options = {k: v for k, v in kwargs.items() if v != "disabled"}
        if not selected_options:
            print("Warning: No options selected.")
        return (selected_options,)

class WildPromptorGenerator:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "🧪 AILab/🧿 WildPromptor/🔀 Promptor"

    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(__file__), self.config['data_path'])
        self.file_cache = {}

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "selected_options": ("DPROMPT_DATA",),
                "prompt_count": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "allow_duplicates": ("BOOLEAN", {"default": True}),
            }
        }

    def process_prompt(self, selected_options: Dict[str, Any], prompt_count: int, seed: int, allow_duplicates: bool = True) -> Tuple[List[str]]:
        if not isinstance(selected_options, dict):
            raise ValueError("selected_options must be a dictionary")

        random.seed(seed)
        all_prompts = []

        for _ in range(prompt_count):
            prompt_parts = []
            for key, value in selected_options.items():
                if value == "🎲 Random":
                    folder, cleaned_name = key.split(' - ')
                    original_name = self.get_original_filename(folder, cleaned_name)
                    file_path = os.path.join(self.data_path, folder, f"{original_name}.txt")
                    options = self.read_file_options(file_path)
                    if options:
                        if allow_duplicates:
                            prompt_parts.append(random.choice(options))
                        else:
                            prompt_parts.append(random.sample(options, 1)[0])
                elif value != "disabled":
                    prompt_parts.append(str(value))
            
            if prompt_parts:
                all_prompts.append(",".join(prompt_parts))

        for prompt in all_prompts:
            print(f"💬 WildPromptor Generator output: {prompt}")

        return (all_prompts,)

    def get_original_filename(self, folder, cleaned_name):
        folder_path = os.path.join(self.data_path, folder)
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt') and cleaned_name in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name

    def read_file_options(self, file_path: str) -> List[str]:
        if file_path in self.file_cache:
            return self.file_cache[file_path]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                options = [line.strip() for line in file if line.strip()]
            self.file_cache[file_path] = options
            return options
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

NODE_CLASS_MAPPINGS = {
    "AllInOneList": AllInOneList,
    "WildPromptorGenerator": WildPromptorGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AllInOneList": "All-In-One List 📋",
    "WildPromptorGenerator": "WildPromptor Generator 🔀"
}