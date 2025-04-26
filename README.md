# AI Image Generator App

A web application that generates images based on user input, with optional OpenAI API integration.

## Features

- Generate images from text descriptions
- OpenAI gpt-image-1 API integration (when API key is provided)
- Fallback to local image generation when API is unavailable
- Simple, user-friendly interface

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. (Optional) Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```
   If no API key is provided, the app will use a local image generation algorithm instead.

3. Run the application (choose one):
   
   - Simple HTTP server version:
     ```
     python app_simple.py
     ```
     Access at http://localhost:8090
   
   - Flask version:
     ```
     python app.py
     ```
     Access at http://localhost:5050

## Usage

1. Enter a description in the input field
2. Click "Generate" to create an image based on your input
3. The generated image will be displayed below the form

## Branches

- `main` - Basic image generator with simple local generation
- `openai-integration` - Enhanced version with OpenAI API integration

## Technical Details

The application offers two implementations:

1. `app_simple.py` - Uses Python's built-in HTTP server
2. `app.py` - Uses Flask framework

When an OpenAI API key is provided, the app will use OpenAI's gpt-image-1 model to generate high-quality images based on text prompts. If no API key is available or if the API call fails, it falls back to a simple local generation algorithm. 