import os
import random
import json
from typing import Tuple, List, Dict, Any

def get_subfolder_names():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return [f for f in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, f)) and f != '__pycache__']

class BaseNode:
    _config = None

    @classmethod
    def load_config(cls):
        if cls._config is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            with open(config_path, 'r') as f:
                cls._config = json.load(f)
        return cls._config

class PromptListNode(BaseNode):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process_prompt"
    OUTPUT_IS_LIST = (True,)

    def get_txt_file_names(self):
        return [f for f in os.listdir(self.data_path) if f.endswith(".txt")]
    
    def __init__(self):
        self.config = self.load_config()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', self.FOLDER_NAME)
        self.file_names = self.get_txt_file_names()
        self.file_contents = self.load_file_contents()

    def load_file_contents(self):
        file_contents = {}
        for filename in self.file_names:
            file_contents[filename] = self.read_file_lines(filename)
        return file_contents

    def read_file_lines(self, filename):
        file_path = os.path.join(self.data_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]
                titles = []
                contents = []
                for line in lines:
                    if ' - ' in line:
                        title, content = line.split(' - ', 1)
                        titles.append(title)
                        contents.append(content)
                    else:
                        titles.append(line)
                        contents.append(line)
                return titles, contents
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return [], []
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return [], []

    @classmethod
    def INPUT_TYPES(cls):
        self = cls()
        inputs = {"required": {}, "optional": {}}
        for filename in self.file_names:
            original_name = os.path.splitext(filename)[0]
            cleaned_name = original_name.split('.', 1)[-1] if '.' in original_name else original_name
            titles, contents = self.file_contents[filename]
            item_count = len(titles) if titles else len(contents)
            # display_name = f"{self.FOLDER_NAME} - {cleaned_name} [{item_count}]"
            display_name = f"{cleaned_name} [{item_count}]"
            inputs["optional"][display_name] = (["❌disabled", "🎲Random", "🔢ordered"] + titles, {"default": "❌disabled"})

        inputs["optional"]["batch_size"] = ("INT", {"default": 1, "min": 1, "max": 1000})
        inputs["optional"]["seed"] = ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
        return inputs

    def process_prompt(self, batch_size=1, seed=0, **kwargs):
        random.seed(seed)
        all_prompts = []

        for _ in range(batch_size):
            prompt_parts = []
            for key, value in kwargs.items():
                if key in ["batch_size", "seed"]:
                    continue
                if value == "🎲Random":
                    cleaned_name = key.split(' [')[0]
                    original_name = self.get_original_filename(cleaned_name)
                    titles, contents = self.file_contents[original_name + '.txt']
                    if contents:
                        value = random.choice(contents)
                elif value == "🔢ordered":
                    cleaned_name = key.split(' [')[0]
                    original_name = self.get_original_filename(cleaned_name)
                    titles, contents = self.file_contents[original_name + '.txt']
                    if contents:
                        index = _ % len(contents)
                        value = contents[index]
                elif value not in ["❌disabled", "🎲Random", "🔢ordered"]:
                    cleaned_name = key.split(' [')[0]
                    original_name = self.get_original_filename(cleaned_name)
                    titles, contents = self.file_contents[original_name + '.txt']
                    if titles and value in titles:
                        index = titles.index(value)
                        value = contents[index]
                if value not in ["❌disabled", "🎲Random", "🔢ordered"]:
                    prompt_parts.append(str(value))
            if prompt_parts:
                all_prompts.append(", ".join(prompt_parts))

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
    CATEGORY = "🧪AILab/🧿WildPromptor/🔀Promptor"

    @classmethod
    def INPUT_TYPES(cls):
        config = cls.load_config()
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config['data_path'])
        folders = config['folders']

        inputs = {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""})
            }
        }
        for folder in folders:
            if os.path.isdir(os.path.join(data_path, folder)):
                inputs["optional"][folder.lower()] = ("STRING", {"multiline": True, "default": ""})
        inputs["optional"].update({
            "suffix": ("STRING", {"multiline": True, "default": ""}),
            "separator": (["comma", "space", "newline"], {"default": "comma"}),
            "remove_duplicates": ("BOOLEAN", {"default": False}),
            "sort": ("BOOLEAN", {"default": False})
        })
        return inputs

    def process_prompt(self, prefix="", suffix="", separator="comma", remove_duplicates=False, sort=False, **kwargs):
        prompt_parts = [part.strip() for part in [prefix] + list(kwargs.values()) + [suffix] if part and part.strip()]
        
        if not prompt_parts:
            return ("",)
        
        if remove_duplicates:
            prompt_parts = list(dict.fromkeys(prompt_parts))
        
        if sort:
            middle_parts = prompt_parts[1:-1] if suffix else prompt_parts[1:]
            middle_parts.sort()
            prompt_parts = [prefix] + middle_parts + ([suffix] if suffix else [])
        
        final_prompt = {"comma": ", ", "space": " ", "newline": "\n"}[separator].join(prompt_parts)
        
        print(f"🔀 Prompt Concat output:\n{final_prompt}")
        
        return (final_prompt,)

    def process_prompt(self, prefix="", suffix="", separator="comma", remove_duplicates=False, sort=False, **kwargs):
        prompt_parts = [part.strip() for part in [prefix] + list(kwargs.values()) + [suffix] if part and part.strip()]
        
        if not prompt_parts:
            return ("",)
        
        if remove_duplicates:
            prompt_parts = list(dict.fromkeys(prompt_parts))
        
        if sort:
            middle_parts = prompt_parts[1:-1] if suffix else prompt_parts[1:]
            middle_parts.sort()
            prompt_parts = [prefix] + middle_parts + ([suffix] if suffix else [])
        
        final_prompt = {"comma": ", ", "space": " ", "newline": "\n"}[separator].join(prompt_parts)
        
        print(f"🔀 Prompt Concat output:\n{final_prompt}")
        
        return (final_prompt,)

class PromptBuilder:
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "content_only")  # 修改此处
    # OUTPUT_IS_LIST = (False, False)
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "process_prompt"
    CATEGORY = "🧪AILab/🧿WildPromptor/🔀Promptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "prefix": ("STRING", {"multiline": True, "default": ""}),
                "content": ("STRING", {"multiline": True, "default": ""}),
                "suffix": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    def process_prompt(self, prefix: str = "", content: str = "", suffix: str = "") -> Tuple[List[str], str]:
    # def process_prompt(self, prefix: str = "", content: str = "", suffix: str = "") -> List[str]:
        if isinstance(content, list):
            content = "\n".join(content)

        lines = content.split('\n') if content else []
        prompt_list = [f"{prefix}, {line}, {suffix}".strip(', ') for line in lines if line.strip()]

        return (prompt_list if prompt_list else [""], content)


class KeywordPicker:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("picked_keywords",)
  # OUTPUT_IS_LIST = (True,)
    FUNCTION = "pick_keywords"
    CATEGORY = "🧪AILab/🧿WildPromptor/🔀Promptor"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "input_keywords": ("STRING", {"forceInput": True}),
                "keywords": ("STRING", {"multiline": True, "default": ""}),
                "pick_count": ("INT", {"default": 1, "min": 0, "max": 1000}),
                "pick_mode": (["🎲Random", "🔢ordered"], {"default": "🎲Random"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    def pick_keywords(self, input_keywords="", keywords="", pick_count=1, pick_mode="🎲Random", seed=0):
        combined_keywords = f"{input_keywords},{keywords}"
        
        if not combined_keywords.strip():
            return ("",)
        
        keyword_list = [kw.strip() for kw in combined_keywords.split(', ') if kw.strip()]

        if not keyword_list:
            return ("",)
        
        if pick_count <= 0:
            return ("",)
        
        if pick_mode == "🎲Random":
            random.seed(seed)
            picked = random.sample(keyword_list, min(pick_count, len(keyword_list)))
        else:  # ordered
            picked = keyword_list[:pick_count]
        
        return (", ".join(picked),)

def create_Promptor_node(folder_name):
    return type(f"{folder_name.capitalize()}PromptorNode", (PromptListNode,), {
        "CATEGORY": "🧪AILab/🧿WildPromptor/📋Prompts List",
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