"""
API Setup Guide for CreatureCollectorCLI
Run this script to test and configure your image generation APIs
"""

import os
from helpers import ImageGenerator

def setup_guide():
    """Interactive setup guide for image generation APIs"""
    
    print("🎨 CreatureCollectorCLI - Image Generation API Setup")
    print("=" * 60)
    print()
    
    print("This guide will help you set up FREE image generation APIs:")
    print()
    print("1. 🌸 POLLINATIONS.AI (Completely Free)")
    print("   • No API key required")
    print("   • No sign-up needed")
    print("   • Already configured!")
    print()
    
    print("2. 🤖 DEEPAI (Free Tier)")
    print("   • Visit: https://deepai.org/")
    print("   • Sign up for free account")
    print("   • Get API key from account dashboard")
    print("   • Set environment variable: export DEEPAI_API_KEY='your-key'")
    print()
    
    print("3. 🤗 HUGGING FACE (Free Tier)")
    print("   • Visit: https://huggingface.co/")
    print("   • Create free account")
    print("   • Go to Settings > Access Tokens")
    print("   • Create new token with 'Inference API' permission")
    print("   • Set environment variable: export HUGGING_FACE_API_KEY='your-key'")
    print()
    
    print("4. 🏠 LOCAL STABLE DIFFUSION (Advanced)")
    print("   • Install AUTOMATIC1111 or similar")
    print("   • Enable API mode")
    print("   • Run on localhost:7860")
    print()
    
    # Check current environment variables
    print("📋 Current Environment Variables:")
    print("-" * 40)
    deepai_key = os.getenv('DEEPAI_API_KEY')
    hf_key = os.getenv('HUGGING_FACE_API_KEY')
    
    print(f"DEEPAI_API_KEY:       {'✅ Set' if deepai_key else '❌ Not set'}")
    print(f"HUGGING_FACE_API_KEY: {'✅ Set' if hf_key else '❌ Not set'}")
    print()
    
    # Test APIs
    choice = input("Would you like to test the APIs now? (y/N): ").lower()
    if choice == 'y':
        print("\n🧪 Testing APIs...")
        image_gen = ImageGenerator()
        image_gen.test_apis()
    
    print("\n✅ Setup complete!")
    print("You can now run the CreatureCollectorCLI with image generation enabled.")
    print("\nTo start the application:")
    print("  cd lib")
    print("  python cli.py")

if __name__ == "__main__":
    setup_guide()