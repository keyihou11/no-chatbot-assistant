#!/usr/bin/env python3
"""Test LLM configuration and connectivity."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI configuration."""
    print("🔍 Testing OpenAI...")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("   ⚠️  OPENAI_API_KEY not configured")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'OK' if you can hear me"}],
            max_tokens=10
        )
        
        print(f"   ✅ OpenAI ({model}) is working!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_claude():
    """Test Anthropic Claude configuration."""
    print("🔍 Testing Anthropic Claude...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("   ⚠️  ANTHROPIC_API_KEY not configured")
        return False
    
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Simple test
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'OK' if you can hear me"}]
        )
        
        print(f"   ✅ Claude ({model}) is working!")
        print(f"   Response: {response.content[0].text}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google():
    """Test Google Gemini configuration."""
    print("🔍 Testing Google Gemini...")
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
    
    if not api_key or api_key == "your_google_api_key_here":
        print("   ⚠️  GOOGLE_API_KEY not configured")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK' if you can hear me")
        
        print(f"   ✅ Google Gemini ({model_name}) is working!")
        print(f"   Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("No-Chatbot LLM Configuration Test")
    print("=" * 60)
    print()
    
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    print(f"📋 Current LLM_PROVIDER: {provider}")
    print()
    
    # Test the configured provider
    if provider == "openai":
        success = test_openai()
    elif provider == "claude":
        success = test_claude()
    elif provider == "google":
        success = test_google()
    else:
        print(f"❌ Unknown provider: {provider}")
        success = False
    
    print()
    print("=" * 60)
    
    # Test all providers (optional)
    print()
    input("Press Enter to test all providers (or Ctrl+C to skip)...")
    print()
    
    results = {
        "OpenAI": test_openai(),
        "Claude": test_claude(),
        "Google": test_google()
    }
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    for provider, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {provider}")
    
    print()
    print("💡 Tip: Configure your preferred provider in .env file")
    print()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
