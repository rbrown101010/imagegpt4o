from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw
import numpy as np
import io
import os
import base64
import openai
from openai import OpenAI
from openai_config import OPENAI_API_KEY

app = Flask(__name__)

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Initialize OpenAI client if API key is available
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_image_with_openai(prompt):
    """Generate an image using OpenAI's gpt-image-1 model API"""
    # If no API key or client is available, use fallback
    if not client or not OPENAI_API_KEY:
        print("No OpenAI API key available. Using fallback image generation.")
        return generate_fallback_image(prompt)
        
    try:
        # Call OpenAI API
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512",  # Lower resolution for faster response
            quality="medium",  # Medium quality for balance
            response_format="b64_json"
        )
        
        # Get base64 encoded image
        img_b64 = response.data[0].b64_json
        return img_b64
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to the local image generation if API call fails
        return generate_fallback_image(prompt)

def generate_fallback_image(prompt):
    """
    Fallback to generate a simple image if API call fails.
    This is a very basic implementation that creates colored shapes.
    """
    # Create a blank white image
    width, height = 400, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Simple "algorithm" to create different images based on the prompt
    # Using the sum of character codes to seed the random generator
    seed = sum(ord(c) for c in prompt)
    np.random.seed(seed)
    
    # Draw some random shapes based on the prompt
    for _ in range(5):
        shape_type = np.random.choice(['rectangle', 'circle'])
        color = (
            np.random.randint(0, 256),
            np.random.randint(0, 256),
            np.random.randint(0, 256)
        )
        
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        
        if shape_type == 'rectangle':
            size = np.random.randint(20, 100)
            draw.rectangle([x, y, x + size, y + size], fill=color)
        else:
            radius = np.random.randint(20, 100)
            draw.ellipse([x, y, x + radius, y + radius], fill=color)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    return img_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    image_data = None
    error_message = None
    prompt = ""
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        if prompt:
            try:
                # Use OpenAI API for image generation
                image_data = generate_image_with_openai(prompt)
            except Exception as e:
                # Fallback to local generation if API fails
                print(f"Error with OpenAI API: {e}")
                image_data = generate_fallback_image(prompt)
                error_message = "API request failed. Using fallback image generation."
    
    return render_template('index.html', image_data=image_data, prompt=prompt, error_message=error_message)

if __name__ == '__main__':
    print("Starting AI Image Generator using Flask...")
    print("Using OpenAI gpt-image-1 model for image generation")
    app.run(debug=True, port=5050)  # Use a different port to avoid conflicts 