import requests
import json
import os
import time
import random
from WildPromptorAI import WildPromptorAI
from requests.exceptions import Timeout, RequestException

class WildPromptorOllama(WildPromptorAI):
    ollama_status = "Not connected"
    cached_models = ["Waiting for connection..."]
    last_refresh_time = 0
    default_model = ""

    @classmethod
    def INPUT_TYPES(cls):
        default_url, default_model = cls.get_default_settings()
        cls.default_model = default_model
        return {
            "required": {
                "keywords": ("STRING", {"multiline": True}),
                "server_url": ("STRING", {"default": default_url}),
                "model": (cls.get_ollama_models(),),
                "max_length": ("INT", {"default": 512, "min": 1, "max": 1024, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "🧪 AILab/🤖 AI Generator"

    @classmethod
    def get_default_settings(cls):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            ollama_config = config.get('ollama', {})
            return ollama_config.get('url', 'http://localhost:11434'), ollama_config.get('model', '')
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return 'http://localhost:11434', ''

    @classmethod
    def check_ollama_server(cls, server_url):
        try:
            response = requests.get(f"{server_url}/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False

    @classmethod
    def get_ollama_models(cls):
        current_time = time.time()
        if current_time - cls.last_refresh_time < 1:
            return cls.cached_models

        server_url, _ = cls.get_default_settings()
        
        if not cls.check_ollama_server(server_url):
            cls.ollama_status = "Server not running"
            cls.cached_models = ["Ollama server not running"]
            return cls.cached_models

        try:
            response = requests.get(f"{server_url}/api/tags?nocache={random.random()}", timeout=5)
            response.raise_for_status()
            cls.cached_models = [model['name'] for model in response.json()['models']]
            cls.last_refresh_time = current_time
            cls.ollama_status = "Connected"
            if cls.default_model and cls.default_model in cls.cached_models:
                cls.cached_models.remove(cls.default_model)
                cls.cached_models.insert(0, cls.default_model)
            return cls.cached_models if cls.cached_models else ["No available models"]
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            cls.ollama_status = "Connection failed"
            cls.cached_models = ["Unable to fetch models"]
            return cls.cached_models

    @classmethod
    def handle_error(cls, error, context=""):
        cls.ollama_status = "Connection failed"
        error_message = f"Error: {context} - {str(error)}"
        print(error_message)
        return (error_message,)

    def generate_prompt(self, keywords, model, temperature=0.7, max_length=512, server_url=None):
        if server_url is None:
            server_url, _ = self.get_default_settings()

        if not self.check_ollama_server(server_url):
            return ("Ollama server is not running. Please start the server and try again.",)

        if model in ["Waiting for connection...", "Ollama server not running", "Unable to fetch models"]:
            return ("Ollama server not connected or models not available. Please ensure Ollama is running and refresh the model list.",)
        
        prompt = self.format_prompt(keywords)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{server_url}/api/generate", json=payload, timeout=30)
                response.raise_for_status()
                
                json_response = response.json()
                generated_prompt = self.clean_prompt(json_response.get('response', ''))
                
                if len(generated_prompt) > max_length:
                    generated_prompt = generated_prompt[:max_length]
                
                print(f"🤖 Ollama prompt:\n{generated_prompt}")
                return (generated_prompt,)
            except Timeout:
                if attempt < max_retries - 1:
                    print(f"Request timed out. Retrying... (Attempt {attempt + 2} of {max_retries})")
                    time.sleep(2)
                else:
                    return self.handle_error("Max retries reached. Unable to generate prompt.", "Timeout")
            except RequestException as e:
                return self.handle_error(e, "Network issue")
            except Exception as e:
                return self.handle_error(e, "Unknown issue")

NODE_CLASS_MAPPINGS = {"WildPromptorOllama": WildPromptorOllama}
NODE_DISPLAY_NAME_MAPPINGS = {"WildPromptorOllama": "Ollama 🤖"}