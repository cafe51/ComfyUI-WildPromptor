import random
import re

class WildPromptor_DataToPromptList:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "file path"}),  # Changed default value
                "separator": ("STRING", {"default": "default"}),  # Changed default value
                "batch_size": ("INT", {"default": 1, "min": 0, "max": 1000}),
                "count_start_from": ("INT", {"default": 1, "min": 1}),
                "allow_duplicates": ("BOOLEAN", {"default": True}),
                "mode": (["⬇️Sequential", "⬆️Reverse", "🎲Random"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "text": ("STRING", {"forceInput": True}),  # Changed name from multiline_text to text
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("prompt", "prompt_list",)
    OUTPUT_IS_LIST = (True, False,)
    FUNCTION = "generate_prompts"
    CATEGORY = "🧪AILab/🧿WildPromptor/🔀Promptor"

    def generate_prompts(self, path, batch_size=1, count_start_from=1, seed=0, allow_duplicates=True, mode="⬇️Sequential", separator="default", text=None):
        random.seed(seed)
        
        data = []

        def split_and_clean(text, separator=None):
            if separator == "default" or separator == "":
                segments = [segment.strip() for segment in text.splitlines() if segment.strip()]
            else:
                segments = [segment.strip() for segment in text.split(separator) if segment.strip()]

            return segments

        # Read from text if provided
        if text:
            data.extend(split_and_clean(text, separator))

        # Read from path if provided
        if path and path != "file path":
            paths = re.split(r'\s*[,|\n]\s*', path.strip())
            cleaned_paths = []
            buffer = ""
            
            for part in paths:
                if part:
                    buffer += part
                    if buffer.count('.') > 1 or buffer.endswith(('.txt', '.csv')):
                        cleaned_paths.append(buffer.strip())
                        buffer = ""
            
            if buffer:
                cleaned_paths.append(buffer.strip())

            for p in cleaned_paths:
                if p:
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            data.extend(split_and_clean(f.read(), separator))
                    except (FileNotFoundError, IOError) as e:
                        print(f"Error reading file {p}: {e}")

        # Handle the case where batch_size is 0 (representing "All")
        if batch_size == 0:
            batch_size = len(data)
        
        if not data:
            return (["No data available"],)
        
        data_len = len(data)
        count_start_from = min(count_start_from - 1, data_len - 1)  # Adjust for 0-based index

        if mode == "⬆️Reverse":
            data = data[::-1]
        elif mode == "🎲Random":
            random.shuffle(data)

        prompts = []
        used_indices = set()
        
        for i in range(batch_size):
            if allow_duplicates:
                index = (count_start_from + i) % data_len
            else:
                if len(used_indices) >= data_len:
                    break
                while True:
                    index = (count_start_from + i) % data_len
                    if index not in used_indices:
                        used_indices.add(index)
                        break
            prompts.append(data[index])

        prompt_list = "\n\n".join(prompts)

        return (prompts, prompt_list,)

NODE_CLASS_MAPPINGS = {
    "WildPromptor_DataToPromptList": WildPromptor_DataToPromptList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WildPromptor_DataToPromptList": "WildPromptor Data To Prompt List 📋+🔀"
}
