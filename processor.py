
# Upgraded processor: supports PNG, SVG, and animated outputs (GIF/WebP/APNG where available).
from PIL import Image, ImageFilter, ImageOps, ImageDraw
import numpy as np
from io import BytesIO
import math

def _average_color(image, box=None):
    if box:
        region = image.crop(box)
    else:
        region = image
    arr = np.array(region.resize((10,10))).astype(int)
    avg = tuple(arr.mean(axis=(0,1)).astype(int)[:3])
    return avg

def _posterize_flat(image, bits=3):
    img = image.convert('RGB')
    img = ImageOps.posterize(img, bits)
    img = img.filter(ImageFilter.SMOOTH)
    return img

def _compose_base_circle(size, base_color):
    canvas = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(canvas)
    r = size//2 - 2
    bbox = [(size//2 - r, size//2 - r), (size//2 + r, size//2 + r)]
    draw.ellipse(bbox, fill=tuple(list(base_color) + [255]))
    # highlight
    hl_bbox = [int(size*0.58), int(size*0.18), int(size*0.9), int(size*0.45)]
    hl = Image.new('RGBA', (size, size), (0,0,0,0))
    hl_draw = ImageDraw.Draw(hl)
    hl_draw.ellipse(hl_bbox, fill=(255,255,255,60))
    canvas = Image.alpha_composite(canvas, hl)
    return canvas

def _draw_face(canvas, expression='smile'):
    size = canvas.size[0]
    draw = ImageDraw.Draw(canvas)
    eye_y = int(size*0.38)
    eye_x_offset = int(size*0.18)
    eye_r = int(size*0.06)
    # eyes
    if expression == 'winky':
        draw.line([(size//2 - eye_x_offset - eye_r, eye_y), (size//2 - eye_x_offset + eye_r, eye_y)], fill=(0,0,0,255), width=4)
        draw.ellipse((size//2 + eye_x_offset - eye_r, eye_y - eye_r, size//2 + eye_x_offset + eye_r, eye_y + eye_r), fill=(0,0,0,255))
    else:
        draw.ellipse((size//2 - eye_x_offset - eye_r, eye_y - eye_r, size//2 - eye_x_offset + eye_r, eye_y + eye_r), fill=(0,0,0,255))
        draw.ellipse((size//2 + eye_x_offset - eye_r, eye_y - eye_r, size//2 + eye_x_offset + eye_r, eye_y + eye_r), fill=(0,0,0,255))
    # mouth
    mouth_top = int(size*0.55)
    mouth_left = int(size*0.32)
    mouth_right = int(size*0.68)
    mouth_bottom = int(size*0.75)
    if expression == 'smile':
        draw.pieslice([mouth_left, mouth_top, mouth_right, mouth_bottom], start=0, end=180, fill=(0,0,0,255))
    elif expression == 'sad':
        draw.pieslice([mouth_left, mouth_top, mouth_right, mouth_bottom], start=180, end=360, fill=(0,0,0,255))
    elif expression == 'tongue':
        draw.pieslice([mouth_left, mouth_top, mouth_right, mouth_bottom], start=0, end=180, fill=(0,0,0,255))
        tbox = [int(size*0.47), int(size*0.62), int(size*0.53), int(size*0.72)]
        draw.ellipse(tbox, fill=(255,105,180,255))
    else:
        draw.line([(int(size*0.35), int(size*0.65)), (int(size*0.65), int(size*0.65))], fill=(0,0,0,255), width=6)
    return canvas

def process_photo_to_emoji(img_bytes, tone='auto', size=256, as_svg=False):
    \"\"\"Process a photo and return either PNG bytes or SVG string when as_svg=True\"\"\"
    img = Image.open(BytesIO(img_bytes)).convert('RGB')
    # Crop centered square
    w,h = img.size
    side = min(w,h)
    left = (w-side)//2
    top = (h-side)//2
    img = img.crop((left, top, left+side, top+side))
    img = img.resize((size, size), Image.LANCZOS)
    flat = _posterize_flat(img, bits=3)
    center_box = (size*3//8, size*3//8, size*5//8, size*5//8)
    base = _average_color(flat, box=center_box)
    if as_svg:
        return _render_svg_base_face(size, base, expression='smile')
    canvas = _compose_base_circle(size, base)
    canvas = _draw_face(canvas, expression='smile')
    out = BytesIO()
    canvas.save(out, format='PNG')
    out.seek(0)
    return out

def generate_prompt_emoji(prompt, tone='auto', size=256, as_svg=False):
    p = prompt.lower()
    if 'pink' in p:
        base = (255,182,193)
    elif 'green' in p:
        base = (144,238,144)
    elif 'blue' in p:
        base = (135,206,235)
    elif 'brown' in p:
        base = (210,180,140)
    else:
        base = (255,205,0)
    expression = 'neutral'
    if 'smile' in p or 'happy' in p or ':' in p:
        expression = 'smile'
    if 'sad' in p or 'frown' in p:
        expression = 'sad'
    if 'wink' in p or ';)' in p:
        expression = 'winky'
    if 'tongue' in p or ':p' in p:
        expression = 'tongue'
    if as_svg:
        return _render_svg_base_face(size, base, expression=expression)
    canvas = _compose_base_circle(size, base)
    canvas = _draw_face(canvas, expression=expression)
    out = BytesIO()
    canvas.save(out, format='PNG')
    out.seek(0)
    return out

def _render_svg_base_face(size, base_color, expression='smile'):
    # Returns an SVG string representing the emoji (circle base + simple eyes/mouth)
    # base_color: (r,g,b)
    r,g,b = base_color
    eye_y = size*0.38
    eye_x_offset = size*0.18
    eye_r = size*0.06
    mouth_top = size*0.55
    mouth_left = size*0.32
    mouth_right = size*0.68
    mouth_bottom = size*0.75
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
    <defs>
      <filter id="f"><feGaussianBlur stdDeviation="2" /></filter>
    </defs>
    <circle cx="{size/2}" cy="{size/2}" r="{size/2 - 2}" fill="rgb({r},{g},{b})" />
    <ellipse cx="{size*0.5 - eye_x_offset}" cy="{eye_y}" rx="{eye_r}" ry="{eye_r}" fill="black" />
    <ellipse cx="{size*0.5 + eye_x_offset}" cy="{eye_y}" rx="{eye_r}" ry="{eye_r}" fill="black" />'''
    if expression == 'winky':
        svg += f'<line x1="{size*0.5 - eye_x_offset - eye_r}" y1="{eye_y}" x2="{size*0.5 - eye_x_offset + eye_r}" y2="{eye_y}" stroke="black" stroke-width="4" />'
    if expression == 'smile':
        mx = (mouth_left + mouth_right)/2
        svg += f'<path d="M {mouth_left} {mouth_bottom} A {(mouth_right-mouth_left)/2} {(mouth_bottom-mouth_top)/2} 0 0 1 {mouth_right} {mouth_bottom} L {mouth_right- (mouth_right-mouth_left)/4} {mouth_bottom- (mouth_bottom-mouth_top)/4} A {(mouth_right-mouth_left)/4} {(mouth_bottom-mouth_top)/4} 0 0 0 {mouth_left + (mouth_right-mouth_left)/4} {mouth_bottom- (mouth_bottom-mouth_top)/4} Z" fill="black" />'
    elif expression == 'sad':
        svg += f'<path d="M {mouth_left} {mouth_top} A {(mouth_right-mouth_left)/2} {(mouth_bottom-mouth_top)/2} 0 0 0 {mouth_right} {mouth_top} L {mouth_right- (mouth_right-mouth_left)/4} {mouth_top+ (mouth_bottom-mouth_top)/4} A {(mouth_right-mouth_left)/4} {(mouth_bottom-mouth_top)/4} 0 0 1 {mouth_left + (mouth_right-mouth_left)/4} {mouth_top+ (mouth_bottom-mouth_top)/4} Z" fill="black" />'
    else:
        # neutral line
        svg += f'<rect x="{size*0.35}" y="{size*0.64}" width="{size*0.3}" height="{size*0.03}" rx="2" fill="black" />'
    svg += '</svg>'
    return svg

def generate_animated_variants(prompt_or_image_bytes, mode='prompt', frames=6, size=256, out_format='gif'):
    \"\"\"Generate a simple animated emoji (blink/bounce) and return BytesIO of chosen format.
       mode: 'prompt' or 'photo'
       out_format: 'gif'|'webp'|'apng' (apng requires external library)\"\"\"
    # Generate base PNG first
    if mode == 'prompt':
        base_png = generate_prompt_emoji(prompt_or_image_bytes, size=size)
        base_img = Image.open(base_png).convert('RGBA')
    else:
        base_png = process_photo_to_emoji(prompt_or_image_bytes, size=size)
        base_img = Image.open(base_png).convert('RGBA')
    # Create frames: simple blink animation by scaling eyes/mouth or by overlay fade
    frames_list = []
    for i in range(frames):
        f = base_img.copy()
        draw = ImageDraw.Draw(f)
        # simulate blink: every (frames-1)th frame eyes closed
        if i % frames == frames-1:
            # draw closed eyes as lines
            eye_y = int(size*0.38)
            eye_x_offset = int(size*0.18)
            eye_r = int(size*0.06)
            draw.line([(size//2 - eye_x_offset - eye_r, eye_y), (size//2 - eye_x_offset + eye_r, eye_y)], fill=(0,0,0,255), width=4)
            draw.line([(size//2 + eye_x_offset - eye_r, eye_y), (size//2 + eye_x_offset + eye_r, eye_y)], fill=(0,0,0,255), width=4)
        # simple bounce by moving whole image slightly up/down via canvas
        offset = int(math.sin(2*math.pi*i/frames) * 6)
        canvas = Image.new('RGBA', (size, size + 12), (0,0,0,0))
        canvas.paste(f, (0, offset + 6), f)
        # crop back to size centered
        crop = canvas.crop((0,6,size,size+6))
        frames_list.append(crop)
    out = BytesIO()
    if out_format == 'gif':
        frames_list[0].save(out, format='GIF', save_all=True, append_images=frames_list[1:], duration=80, loop=0, disposal=2)
    elif out_format == 'webp':
        frames_list[0].save(out, format='WEBP', save_all=True, append_images=frames_list[1:], duration=80, loop=0, lossless=True)
    elif out_format == 'apng':
        # Pillow does not reliably write APNGs in all environments; fallback to GIF if not available.
        try:
            frames_list[0].save(out, format='PNG', save_all=True, append_images=frames_list[1:], duration=80, loop=0, disposal=2)
        except Exception as e:
            # fallback to GIF
            frames_list[0].save(out, format='GIF', save_all=True, append_images=frames_list[1:], duration=80, loop=0, disposal=2)
    else:
        frames_list[0].save(out, format='GIF', save_all=True, append_images=frames_list[1:], duration=80, loop=0, disposal=2)
    out.seek(0)
    return out
