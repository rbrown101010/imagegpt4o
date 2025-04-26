from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw
import numpy as np
import io
import os

app = Flask(__name__)

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

def generate_image(prompt):
    """
    Generate a simple image based on the prompt.
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
    
    return image

@app.route('/', methods=['GET', 'POST'])
def index():
    image_data = None
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        if prompt:
            # Generate image
            image = generate_image(prompt)
            
            # Convert PIL image to bytes
            img_io = io.BytesIO()
            image.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Convert to base64 for embedding in HTML
            import base64
            image_data = base64.b64encode(img_io.getvalue()).decode('ascii')
    
    return render_template('index.html', image_data=image_data)

if __name__ == '__main__':
    app.run(debug=True) 