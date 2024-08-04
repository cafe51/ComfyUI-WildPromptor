from WildPromptorAI import WildPromptorAI
import requests
import json
import os
import base64
import time
import random
from io import BytesIO
from PIL import Image
import numpy as np
from pprint import pprint
from server import PromptServer
from aiohttp import web
from requests.exceptions import Timeout, RequestException

class WildPromptorOllamaVision(WildPromptorAI):
    ollama_status = "Not connected"
    cached_models = ["Waiting for connection..."]
    last_refresh_time = 0

    @classmethod
    def INPUT_TYPES(cls):
        default_url = cls.get_default_settings()
        return {
            "required": {
                "images": ("IMAGE",),
                "Prompt": ("STRING", {"multiline": True}),
                "Server_url": ("STRING", {"default": default_url}),
                "Model": (cls.get_ollama_models(),),
                "Temperature": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 2.0, "step": 0.1}),
                "Max_length": ("INT", {"default": 256, "min": 1, "max": 1024, "step": 1}),
            },
            "optional": {
                "Keep_alive": ("INT", {"default": 5, "min": 0, "max": 60, "step": 5}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "generate_vision_prompt"
    CATEGORY = "🧪 AILab/🤖 AI Generator"

    @classmethod
    def get_default_settings(cls):
        config = cls.load_config()
        return config.get('ollama', {}).get('url', 'http://localhost:11434')

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

        server_url = cls.get_default_settings()
        
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
            return cls.cached_models if cls.cached_models else ["No available models"]
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            cls.ollama_status = "Connection failed"
            cls.cached_models = ["Unable to fetch models"]
            return cls.cached_models

    @classmethod
    def load_config(cls):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}

    @classmethod
    def handle_error(cls, error, context=""):
        cls.ollama_status = "Connection failed"
        error_message = f"Error: {context} - {str(error)}"
        print(error_message)
        return (error_message,)

    def generate_vision_prompt(self, images, Prompt, Model, Temperature=0.7, Max_length=256, Server_url="", Keep_alive=5):
        if not Server_url:
            Server_url = self.get_default_settings()

        if not self.check_ollama_server(Server_url):
            return ("Ollama server is not running. Please start the server and try again.",)

        if Model in ["Waiting for connection...", "Ollama server not running", "Unable to fetch models"]:
            return ("Ollama server not connected or models not available. Please ensure Ollama is running and refresh the model list.",)

        images_b64 = []
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = base64.b64encode(buffered.getvalue())
            images_b64.append(str(img_bytes, 'utf-8'))

        prompt = self.format_prompt(Prompt)
        
        payload = {
            "model": Model,
            "prompt": prompt,
            "images": images_b64,
            "stream": False,
            "temperature": Temperature,
            "keep_alive": f"{Keep_alive}m"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{Server_url}/api/generate", json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                generated_description = self.clean_prompt(result['response'])
                
                if len(generated_description) > Max_length:
                    generated_description = generated_description[:Max_length]
                
                print(f"🤖 Ollama Vision description:\n{generated_description}")
                return (generated_description,)
            except Timeout:
                if attempt < max_retries - 1:
                    print(f"Request timed out. Retrying... (Attempt {attempt + 2} of {max_retries})")
                    time.sleep(2)
                else:
                    return self.handle_error("Max retries reached. Unable to generate description.", "Timeout")
            except RequestException as e:
                return self.handle_error(e, "Network issue")
            except Exception as e:
                return self.handle_error(e, "Unknown issue")

@PromptServer.instance.routes.post("/ollama/get_models")
async def get_models_endpoint(request):
    data = await request.json()
    url = data.get("url", "http://localhost:11434")
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        response.raise_for_status()
        models = [model['name'] for model in response.json()['models']]
        return web.json_response(models)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

NODE_CLASS_MAPPINGS = {"WildPromptorOllamaVision": WildPromptorOllamaVision}
NODE_DISPLAY_NAME_MAPPINGS = {"WildPromptorOllamaVision": "Ollama Vision 🤖👁️"}