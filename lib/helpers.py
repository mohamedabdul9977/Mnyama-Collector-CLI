import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ===============================
# Image Generator Class
# ===============================
class ImageGenerator:
    def __init__(self):
        self.client = client

    def generate_creature_image(self, description, creature_name):
        """Generate an image for a creature using the OpenAI Image API"""
        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=f"A digital illustration of {description}, highly detailed, fantasy style",
                size="1024x1024"  
            )

            # Extract image URL
            image_url = response.data[0].url

            # Save image URL to a text file
            save_path = f"images/{creature_name.replace(' ', '_')}.txt"
            os.makedirs("images", exist_ok=True)
            with open(save_path, "w") as f:
                f.write(image_url)

            
            return image_url, save_path

        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None


# ===============================
# CLI Helper Functions
# ===============================
def print_header(title):
    """Print a styled header for sections"""
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60 + "\n")


def print_menu(title, options):
    """Print a numbered menu"""
    print_header(title)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print()


def get_user_choice(max_choice):
    """Get validated user input for menu selection"""
    while True:
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= max_choice:
                return choice
            print(f"⚠️ Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("⚠️ Invalid input, please enter a number.")


def print_creature_details(creature):
    """Print details of a creature"""
    habitat_names = [h.name for h in creature.habitats] if creature.habitats else ["Unassigned"]

    print(f"\n🦎 Creature: {creature.name} (Age: {creature.age})")
    print(f"   Species: {creature.species.name} ({creature.species.diet_type})")
    print(f"   Habitats: {', '.join(habitat_names)}")
    if creature.image_path:
        print(f"   Image: {creature.image_path}")
    print()


def print_habitat_report(habitat):
    """Print detailed info about a habitat"""
    print(f"\n🏞️  Habitat: {habitat.name}")
    print(f"   Biome: {habitat.biome_type}")
    print(f"   Size: {habitat.square_footage} sq ft")
    print(f"   Residents: {len(habitat.creatures)} creatures\n")


def format_capacity_bar(current, total, length=20):
    """Generate a simple capacity bar"""
    filled = int(length * current / total) if total > 0 else 0
    return "[" + "#" * filled + "-" * (length - filled) + f"] {current}/{total}"
