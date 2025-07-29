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
    try:
        data = request.json
        bg_url = data.get("background_url")
        quote = data.get("quote", "No quote provided")

        # Load background image
        response = requests.get(bg_url)
        response.raise_for_status()
        bg = Image.open(BytesIO(response.content)).convert("RGBA")

        # Use default font
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(bg)

        # Centered text
        #  text_width, text_height = draw.textsize(quote, font)
        bbox = draw.textbbox((0, 0), quote, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (bg.width - text_width) / 2
        y = (bg.height - text_height) / 2
        draw.text((x, y), quote, font=font, fill="black")

        # Output
        output = BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        print("💥 ERROR:", e)
        return f"Internal Server Error: {e}", 500