from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return "Quote Overlay API is running."

@app.route("/overlay", methods=["POST"])
def overlay_text():
    data = request.json
    bg_url = data.get("background_url")
    quote = data.get("quote", "No quote provided")

    # Load background image
    response = requests.get(bg_url)
    bg = Image.open(BytesIO(response.content)).convert("RGBA")

    # Setup font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=48)
    draw = ImageDraw.Draw(bg)

    # Centered text
    text_width, text_height = draw.textsize(quote, font)
    x = (bg.width - text_width) / 2
    y = (bg.height - text_height) / 2
    draw.text((x, y), quote, font=font, fill="black")

    # Return image
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)

    return send_file(output, mimetype="image/png")
