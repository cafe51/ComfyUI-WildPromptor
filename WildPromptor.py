import os
import random
import json
from typing import Tuple, List, Dict, Any

def get_subfolder_names():
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    return [f for f in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, f)) and f != '__pycache__']

class BaseNode:
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)

class PromptListNode(BaseNode):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)
    
    def __init__(self):
        self.load_config()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data', self.FOLDER_NAME)
        self.file_names = self.get_txt_file_names()

    def get_txt_file_names(self):
        return [f for f in os.listdir(self.data_path) if f.endswith(".txt")]

    def read_file_lines(self, filename):
        file_path = os.path.join(self.data_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {"required": {}, "optional": {}}
        for filename in self.file_names:
            original_name = os.path.splitext(filename)[0]
            cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
            display_name = f"{self.FOLDER_NAME} - {cleaned_name}"
            lines = self.read_file_lines(filename)
            inputs["optional"][display_name] = (["disabled", "🎲 Random"] + lines, {"default": "disabled"})

        inputs["optional"]["prompt_count"] = ("INT", {"default": 1, "min": 1, "max": 1000})
        inputs["optional"]["seed"] = ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
        return inputs

    def process_prompt(self, prompt_count=1, seed=0, **kwargs):
        random.seed(seed)
        all_prompts = []

        for _ in range(prompt_count):
            prompt_parts = []
            for key, value in kwargs.items():
                if key in ["prompt_count", "seed"]:
                    continue
                if value == "🎲 Random":
                    folder, cleaned_name = key.split(' - ')
                    original_name = self.get_original_filename(cleaned_name)
                    lines = self.read_file_lines(original_name + '.txt')
                    if lines:
                        value = random.choice(lines)
                    else:
                        continue
                if value != "disabled":
                    prompt_parts.append(value)
            if prompt_parts:
                all_prompts.append(",".join(prompt_parts))

        return (all_prompts,) if all_prompts else ([""],)

    def get_original_filename(self, cleaned_name):
        for filename in self.file_names:
            if cleaned_name in filename:
                return os.path.splitext(filename)[0]
        return cleaned_name

class PromptConcatNode(BaseNode):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    CATEGORY = "🧪 AILab/🧿 WildPromptor/🔀 Promptor"

    def __init__(self):
        self.load_config()
        self.data_path = os.path.join(os.path.dirname(__file__), self.config['data_path'])
        self.folders = self.config['folders']

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""})
            }
        }
        for folder in self.folders:
            if os.path.isdir(os.path.join(self.data_path, folder)):
                inputs["optional"][folder.lower()] = ("STRING", {"multiline": True, "default": ""})
        inputs["optional"].update({
            "suffix": ("STRING", {"multiline": True, "default": ""}),
            "separator": (["comma", "space", "newline"], {"default": "comma"}),
            "remove_duplicates": ("BOOLEAN", {"default": False}),
            "sort": ("BOOLEAN", {"default": False})
        })
        return inputs

    def process_prompt(self, prefix="", suffix="", separator="comma", remove_duplicates=False, sort=False, **kwargs):
        prompt_parts = [part for part in [prefix] + list(kwargs.values()) + [suffix] if part and part != [""] and part != []]
        if not prompt_parts:
            return ("",)
   
        for part in kwargs.values():
            if part:
                prompt_parts.extend(part.split('\n'))
        if suffix:
            prompt_parts.append(suffix)
        
        if remove_duplicates:
            prompt_parts = list(dict.fromkeys(prompt_parts))
        
        if sort:
            middle_parts = prompt_parts[1:-1] if suffix else prompt_parts[1:]
            middle_parts.sort()
            prompt_parts = [prefix] + middle_parts + ([suffix] if suffix else [])
        
        if separator == "comma":
            final_prompt = ", ".join(prompt_parts)
        elif separator == "space":
            final_prompt = " ".join(prompt_parts)
        else:  # newline
            final_prompt = "\n".join(prompt_parts)
        
        print(f"🔀 Prompt Concat output:\n{final_prompt}")
        
        return (final_prompt,)

class PromptBuilder:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "process_prompt"
    CATEGORY = "🧪 AILab/🧿 WildPromptor/🔀 Promptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""}),
                "prompt_body": ("STRING", {"multiline": True, "default": ""}),
                "suffix": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    def process_prompt(self, prefix: str = "", prompt_body: str = "", suffix: str = "") -> List[str]:
        if isinstance(prompt_body, list):
            prompt_body = "\n".join(prompt_body)
        lines = prompt_body.split('\n') if prompt_body else []
        prompt_list = [f"{prefix},{line},{suffix}".strip(',') for line in lines if line.strip()]
        return (prompt_list if prompt_list else [""],)

class KeywordPicker:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("picked_keywords",)
    FUNCTION = "pick_keywords"
    CATEGORY = "🧪 AILab/🧿 WildPromptor/🔀 Promptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "keywords": ("STRING", {"multiline": True, "default": ""}),
                "pick_count": ("INT", {"default": 1, "min": 0, "max": 1000}),
                "pick_mode": (["Random", "Sequential"], {"default": "Random"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    def pick_keywords(self, keywords="", pick_count=1, pick_mode="Random", seed=0):
        if isinstance(keywords, list):
            keywords = ", ".join(keywords)
        if not keywords.strip() or pick_count == 0:
            return ("",)
        
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        if not keyword_list:
            return ("",)
        
        if pick_mode == "Random":
            random.seed(seed)
            picked = random.sample(keyword_list, min(pick_count, len(keyword_list)))
        else:  # Sequential
            picked = keyword_list[:pick_count]
        
        return (", ".join(picked),)

def create_Promptor_node(folder_name):
    return type(f"{folder_name.capitalize()}PromptorNode", (PromptListNode,), {
        "CATEGORY": "🧪 AILab/🧿 WildPromptor/📋 Prompts",
        "FOLDER_NAME": folder_name
    })

NODE_CLASS_MAPPINGS = {
    "PromptConcat": PromptConcatNode,
    "PromptBuilder": PromptBuilder,
    "KeywordPicker": KeywordPicker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptConcat": "Prompt Concat 🔀",
    "PromptBuilder": "Prompt Builder 🔀",
    "KeywordPicker": "Keyword Picker 🔀",
}

for folder in get_subfolder_names():
    node_class = create_Promptor_node(folder)
    NODE_CLASS_MAPPINGS[f"{folder.capitalize()} 📋"] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[f"{folder.capitalize()} 📋"] = f"{folder.capitalize()} 📋"