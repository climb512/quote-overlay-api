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

        # Load a clean font
        font = ImageFont.truetype("DejaVuSans.ttf", size=60)

        # Wrap text manually to fit max width
        max_width = int(bg.width * 0.85)
        words = quote.split()
        lines = []
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        # Calculate total height for vertical centering
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 10
        text_block_height = len(lines) * line_height
        y = (bg.height - text_block_height) // 2

        # Draw each line centered with clean black text
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (bg.width - text_width) // 2
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