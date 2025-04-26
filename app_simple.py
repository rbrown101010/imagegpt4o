import http.server
import socketserver
import urllib.parse
import json
import random
import base64
import io
from PIL import Image, ImageDraw
import openai
from openai import OpenAI
from openai_config import OPENAI_API_KEY

PORT = 8090  # Changed to avoid conflict with running server

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
    """Fallback to generate a simple image based on the prompt."""
    # Create a blank white image
    width, height = 400, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Use the prompt to seed random generator
    seed = sum(ord(c) for c in prompt)
    random.seed(seed)
    
    # Draw some random shapes
    for _ in range(5):
        shape_type = random.choice(['rectangle', 'circle'])
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        
        x = random.randint(0, width-100)
        y = random.randint(0, height-100)
        
        if shape_type == 'rectangle':
            size = random.randint(20, 100)
            draw.rectangle([x, y, x + size, y + size], fill=color)
        else:
            radius = random.randint(20, 100)
            draw.ellipse([x, y, x + radius, y + radius], fill=color)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    return img_base64

class ImageGeneratorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Serve the HTML page
            html = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI Image Generator</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    h1 {{
                        text-align: center;
                    }}
                    .form-container {{
                        margin-top: 20px;
                        text-align: center;
                    }}
                    input[type="text"] {{
                        width: 70%;
                        padding: 10px;
                        margin-right: 10px;
                    }}
                    button {{
                        padding: 10px 15px;
                        background-color: #FF69B4;
                        color: white;
                        border: none;
                        cursor: pointer;
                    }}
                    .image-container {{
                        margin-top: 30px;
                        text-align: center;
                    }}
                    img {{
                        max-width: 100%;
                        border: 1px solid #ddd;
                    }}
                    .loading {{
                        display: none;
                        text-align: center;
                        margin-top: 20px;
                    }}
                    .api-badge {{
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        background-color: #FF69B4;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="api-badge">OpenAI API</div>
                <h1>AI Image Generator</h1>
                
                <div class="form-container">
                    <form id="generate-form">
                        <input type="text" id="prompt" name="prompt" placeholder="Describe the image you want to generate..." required>
                        <button type="submit">Generate</button>
                    </form>
                </div>
                
                <div class="loading" id="loading">
                    <p>Generating your image with AI...</p>
                </div>
                
                <div class="image-container" id="image-display">
                </div>
                
                <script>
                    document.getElementById('generate-form').addEventListener('submit', async function(e) {{
                        e.preventDefault();
                        const prompt = document.getElementById('prompt').value;
                        
                        // Show loading indicator
                        document.getElementById('loading').style.display = 'block';
                        
                        // Send request to generate image
                        const response = await fetch('/generate?prompt=' + encodeURIComponent(prompt));
                        const data = await response.json();
                        
                        // Hide loading indicator
                        document.getElementById('loading').style.display = 'none';
                        
                        // Display the image
                        const imageContainer = document.getElementById('image-display');
                        imageContainer.innerHTML = `<img src="data:image/png;base64,${{data.image}}" alt="Generated image">
                                                   <p><em>Generated from: "${{prompt}}"</em></p>`;
                    }});
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        elif self.path.startswith('/generate'):
            # Parse the query parameters
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            prompt = query_components.get('prompt', [''])[0]
            
            # Generate the image
            try:
                img_base64 = generate_image_with_openai(prompt)
            except Exception as e:
                print(f"Error generating image: {e}")
                img_base64 = generate_fallback_image(prompt)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'image': img_base64
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404)

def run_server():
    with socketserver.TCPServer(("", PORT), ImageGeneratorHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    print(f"Starting AI Image Generator server on port {PORT}...")
    print("Using OpenAI gpt-image-1 model for image generation")
    run_server() 