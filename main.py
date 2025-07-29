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

        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype("DejaVuSans.ttf", size=48)

        # Set max width for text (e.g. 90% of image width)
        max_width = int(bg.width * 0.9)

        # Wrap the quote into multiple lines
        words = quote.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Calculate total text block height
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 10  # 10px spacing
        text_block_height = len(lines) * line_height

        # Vertical start position
        y = (bg.height - text_block_height) // 2

        # Draw each line centered
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (bg.width - line_width) // 2
            draw.text((x, y), line, font=font, fill="black")
            y += line_height

        # Output image
        output = BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        print("💥 ERROR:", e)
        return f"Internal Server Error: {e}", 500