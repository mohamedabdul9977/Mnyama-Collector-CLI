import os
import requests
import urllib.parse
import base64
import time
import random
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()


class ImageGenerator:
    """Handle image generation using multiple free APIs with fallback support"""
    
    def __init__(self):
        # Create images directory if it doesn't exist
        self.image_dir = "creature_images"
        os.makedirs(self.image_dir, exist_ok=True)
        
        # ✅ Load API keys from .env
        self.deepai_api_key = os.getenv("DEEPAI_API_KEY")  
        self.hf_api_key = os.getenv("HUGGING_FACE_API_KEY")
        
        # API endpoints metadata (not strictly required but nice to keep track)
        self.apis = {
            "pollinations": {"url": "https://image.pollinations.ai/prompt/", "free": True, "requires_key": False},
            "deepai": {"url": "https://api.deepai.org/api/text2img", "free": True, "requires_key": True},
            "huggingface": {"url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1", "free": True, "requires_key": True}
        }
    
    def generate_creature_image(self, creature_name, species_name):
        """
        Generate an image for a creature using multiple free APIs with fallback support
        """
        prompt = f"A realistic photo of a {species_name} named {creature_name}, wildlife photography, detailed, high quality"
        
        # Try different APIs in order of preference
        api_attempts = [
            ("pollinations", self._generate_with_pollinations),
            ("deepai", self._generate_with_deepai),
            ("huggingface", self._generate_with_huggingface)
        ]
        
        for api_name, api_function in api_attempts:
            try:
                print(f"🎨 Trying {api_name.title()} API...")
                image_path, success = api_function(prompt, creature_name, species_name)
                
                if success and image_path:
                    return image_path, f"✅ Image generated using {api_name.title()}"
                    
            except Exception as e:
                print(f"   ❌ {api_name.title()} failed: {str(e)}")
                continue
        
        # If all APIs fail, create a placeholder
        print("🔄 All APIs failed, creating placeholder...")
        image_path = self._create_placeholder_image(creature_name, species_name)
        return image_path, "Created placeholder image (APIs unavailable)"

    # --- POLLINATIONS ---
    def _generate_with_pollinations(self, prompt, creature_name, species_name):
        encoded_prompt = urllib.parse.quote(prompt)
        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        params = {
            "width": 512,
            "height": 512,
            "seed": random.randint(1, 1000000),
            "nologo": "true",
            "enhance": "true"
        }
        
        full_url = f"{api_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        response = requests.get(full_url, timeout=30)
        
        if response.status_code == 200:
            filename = f"{creature_name}_{species_name}_pollinations.jpg".lower().replace(" ", "_")
            image_path = os.path.join(self.image_dir, filename)
            with open(image_path, "wb") as f:
                f.write(response.content)
            return image_path, True
        return None, False

    # --- DEEPAI ---
    def _generate_with_deepai(self, prompt, creature_name, species_name):
        if not self.deepai_api_key:
            raise Exception("DeepAI API key missing in .env file")
        
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={"text": prompt},
            headers={"api-key": self.deepai_api_key},
            timeout=30
        )
        
        if response.status_code == 200 and "output_url" in response.json():
            img_url = response.json()["output_url"]
            img_response = requests.get(img_url, timeout=30)
            if img_response.status_code == 200:
                filename = f"{creature_name}_{species_name}_deepai.jpg".lower().replace(" ", "_")
                image_path = os.path.join(self.image_dir, filename)
                with open(image_path, "wb") as f:
                    f.write(img_response.content)
                return image_path, True
        return None, False

    # --- HUGGING FACE ---
    def _generate_with_huggingface(self, prompt, creature_name, species_name):
        if not self.hf_api_key:
            raise Exception("Hugging Face API key missing in .env file")
        
        headers = {"Authorization": f"Bearer {self.hf_api_key}", "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {"guidance_scale": 7.5, "num_inference_steps": 20, "width": 512, "height": 512}
        }
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            filename = f"{creature_name}_{species_name}_hf.jpg".lower().replace(" ", "_")
            image_path = os.path.join(self.image_dir, filename)
            with open(image_path, "wb") as f:
                f.write(response.content)
            return image_path, True
        
        return None, False

    # --- PLACEHOLDER FALLBACK ---
    def _create_placeholder_image(self, creature_name, species_name):
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (400, 300), color="lightblue")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((50, 100), f"Creature: {creature_name}", fill="black", font=font)
        draw.text((50, 130), f"Species: {species_name}", fill="black", font=font)
        draw.text((50, 200), "[Generated Image]", fill="gray", font=font)
        filename = f"{creature_name}_{species_name}_placeholder.png".lower().replace(" ", "_")
        image_path = os.path.join(self.image_dir, filename)
        img.save(image_path)
        return image_path


# --- CLI Helper Functions ---
def print_header(title):
    print("\n" + "="*60)
    print(f" {title.center(58)} ")
    print("="*60)

def print_menu(title, options):
    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print(f"{len(options)+1}. Go Back")

def get_user_choice(max_choice):
    while True:
        try:
            choice = int(input("> "))
            if 1 <= choice <= max_choice:
                return choice
            else:
                print(f"Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("Please enter a valid number")

def format_capacity_bar(current, maximum, width=30):
    if maximum == 0:
        percentage = 100
    else:
        percentage = min(100, (current / maximum) * 100)
    filled = int((percentage / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{maximum} ({percentage:.1f}%)"

def print_creature_details(creature):
    print(f"\n--- Creature Details ---")
    print(f"Name: {creature.name}")
    print(f"Age: {creature.age} years")
    print(f"Species: {creature.species.name}")
    print(f"Diet: {creature.species.diet_type}")
    print(f"Size: {creature.size} sq ft")
    print(f"Threat Status: {creature.species.threat_status}")
    if creature.habitats:
        print(f"Habitats: {', '.join([h.name for h in creature.habitats])}")
    else:
        print("Habitats: Not assigned to any habitat")
    if creature.image_path:
        print(f"Image: {creature.image_path}")

def print_habitat_report(habitat):
    """Print a summary report of a single habitat and its creatures."""
    print(f"\n🏞️ Habitat Report: {habitat.name}")
    print(f"Biome Type: {habitat.biome_type}")
    print(f"Square Footage: {habitat.square_footage}")
    print(f"Current Capacity: {habitat.current_capacity}/{habitat.square_footage}")
    print(f"Creatures: {len(habitat.creatures)}")

    if habitat.creatures:
        for creature in habitat.creatures:
            print(f"  • {creature.name} ({creature.species.name})")
    else:
        print("  (No creatures assigned)")

