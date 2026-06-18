import random
import string
from io import BytesIO


def generate_captcha_text(length=4):
    return ''.join(random.choices(string.digits, k=length))


def generate_captcha_image(text):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    width, height = 120, 40
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    for _ in range(random.randint(3, 6)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(150, 200),) * 3, width=2)

    font = None
    try:
        font = ImageFont.truetype('arial.ttf', 28)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype('DejaVuSans.ttf', 28)
        except (IOError, OSError):
            font = ImageFont.load_default()

    for i, c in enumerate(text):
        x = 10 + i * 28
        y = random.randint(2, 8)
        r, g, b = random.randint(0, 80), random.randint(0, 80), random.randint(0, 80)
        draw.text((x, y), c, fill=(r, g, b), font=font)

    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return buf
