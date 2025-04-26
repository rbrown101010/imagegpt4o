import os

# Get OpenAI API key from environment variable
# You can set this by running: 
# export OPENAI_API_KEY="your-api-key-here"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# If no API key is set, print a warning
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set.")
    print("Please set it by running: export OPENAI_API_KEY='your-api-key'")
    print("Using fallback image generation for now.") 