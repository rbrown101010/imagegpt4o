import http.server
import socketserver
import urllib.parse
import json
import random
import base64
import io
from PIL import Image, ImageDraw

PORT = 8080

def generate_image(prompt):
    """Generate a simple image based on the prompt."""
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
                <title>Image Generator App</title>
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
                </style>
            </head>
            <body>
                <h1>Image Generator</h1>
                
                <div class="form-container">
                    <form id="generate-form">
                        <input type="text" id="prompt" name="prompt" placeholder="Enter your image description here" required>
                        <button type="submit">Generate</button>
                    </form>
                </div>
                
                <div class="image-container" id="image-display">
                </div>
                
                <script>
                    document.getElementById('generate-form').addEventListener('submit', async function(e) {{
                        e.preventDefault();
                        const prompt = document.getElementById('prompt').value;
                        
                        // Send request to generate image
                        const response = await fetch('/generate?prompt=' + encodeURIComponent(prompt));
                        const data = await response.json();
                        
                        // Display the image
                        const imageContainer = document.getElementById('image-display');
                        imageContainer.innerHTML = `<img src="data:image/png;base64,${{data.image}}" alt="Generated image">`;
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
            img_base64 = generate_image(prompt)
            
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
    run_server() 