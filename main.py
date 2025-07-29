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

        # Load a better font (adjust path and size)
        font = ImageFont.truetype("DejaVuSans.ttf", size=60)

        # Wrap text manually
        max_width = int(bg.width * 0.85)
        words = quote.split()
        lines = []
        line = ""

        for word in words:
            test_line = line + " " + word if line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        # Calculate text block height
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 10
        text_block_height = len(lines) * line_height

        # Vertical centering
        y = (bg.height - text_block_height) // 2

        # Optional: draw a semi-transparent rectangle behind text
        overlay = Image.new("RGBA", bg.size, (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        margin = 40
        rect_top = y - 20
        rect_bottom = y + text_block_height + 20
        overlay_draw.rectangle(
            [(margin, rect_top), (bg.width - margin, rect_bottom)],
            fill=(255, 255, 255, 180)  # Light white box with transparency
        )
        bg = Image.alpha_composite(bg, overlay)

        # ✅ Properly indented draw loop
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