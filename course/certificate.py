from io import BytesIO
from onlinecourse import settings
from PIL import ImageFont, Image, ImageDraw
import os
    
def make_certificates(name, course, date):
    font_path = 'font/legendaria.ttf'
    font_path2 = 'font/productsans.ttf'
    img_path = 'images/template.png'
    font = ImageFont.truetype(font_path, 120, encoding="unic")
    font2 = ImageFont.truetype(font_path2, 60, encoding="unic")
    color = "#FFFFFF"
    template = Image.open(img_path)
    WIDTH, HEIGHT = template.size

    image_source = template
    draw = ImageDraw.Draw(image_source)

    name_width = draw.textlength(name, font=font)
    name_height = 300

    course_width = draw.textlength(course, font=font2)
    course_height = 420

    draw.text(((WIDTH - name_width) / 2, (HEIGHT - name_height) / 2 - 30), name, fill=color, font=font)
    draw.text(((WIDTH - course_width) - 150, (HEIGHT - course_height) / 2 - 30), course, fill=color, font=font2)

    source = f'images/{name}.png'
    image_source.save(source)
    img = Image.open(source)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=60) 
    img_io.seek(0)

    storage = settings.firebase.storage()
    storage_path = f"certificate/" + f"{name}_{course}"
    storage.child(storage_path).put(img_io)
    print('Saving Certificate of:', name)
    os.remove(source)

    return storage.child(storage_path).get_url(None)
