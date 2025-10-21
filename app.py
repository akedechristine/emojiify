from flask import Flask, render_template, request, send_file, redirect, url_for, make_response
from io import BytesIO
from processor import process_photo_to_emoji, generate_prompt_emoji, _render_svg_base_face, generate_animated_variants
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024  # 12MB upload limit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt','').strip()
    tone = request.form.get('tone','auto')
    out_type = request.form.get('out_type','png')
    uploaded = request.files.get('photo')
    if uploaded and uploaded.filename != '':
        img_bytes = uploaded.read()
        if out_type == 'svg':
            svg = process_photo_to_emoji(img_bytes, tone=tone, as_svg=True)
            resp = make_response(svg)
            resp.headers.set('Content-Type', 'image/svg+xml')
            resp.headers.set('Content-Disposition', 'attachment; filename=emoji.svg')
            return resp
        elif out_type in ('gif','webp','apng'):
            anim = generate_animated_variants(img_bytes, mode='photo', out_format=out_type)
            mime = 'image/gif' if out_type=='gif' else 'image/webp' if out_type=='webp' else 'image/png'
            return send_file(anim, mimetype=mime, as_attachment=True, download_name=f'emoji.{out_type}')
        else:
            out_png = process_photo_to_emoji(img_bytes, tone=tone)
            return send_file(out_png, mimetype='image/png', as_attachment=True, download_name='emoji.png')
    elif prompt:
        if out_type == 'svg':
            svg = generate_prompt_emoji(prompt, tone=tone, as_svg=True)
            resp = make_response(svg)
            resp.headers.set('Content-Type', 'image/svg+xml')
            resp.headers.set('Content-Disposition', 'attachment; filename=emoji.svg')
            return resp
        elif out_type in ('gif','webp','apng'):
            anim = generate_animated_variants(prompt, mode='prompt', out_format=out_type)
            mime = 'image/gif' if out_type=='gif' else 'image/webp' if out_type=='webp' else 'image/png'
            return send_file(anim, mimetype=mime, as_attachment=True, download_name=f'emoji.{out_type}')
        else:
            out_png = generate_prompt_emoji(prompt, tone=tone)
            return send_file(out_png, mimetype='image/png', as_attachment=True, download_name='emoji.png')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
