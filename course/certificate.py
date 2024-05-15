from io import BytesIO
from onlinecourse import settings
from PIL import ImageFont, Image, ImageDraw
import os
    
def make_certificates(name_t, course_t, date):
    font_path = 'font/legendaria.ttf'
    font_path2 = 'font/productsans.ttf'
    img_path = 'images/template_new.png'
    font = ImageFont.truetype(font_path, 120, encoding="unic")
    font2 = ImageFont.truetype(font_path2, 60, encoding="unic")
    color = "#000000"
    template = Image.open(img_path)
    WIDTH, HEIGHT = template.size

    image_source = template.convert('RGB')
    draw = ImageDraw.Draw(image_source)

    name = name_t
    course = course_t

    name_width = font.getlength(name)
    name_height = font.size * 1  

    course_width = font2.getlength(course)
    course_height = font2.size * 1  

    name_x = (WIDTH - name_width) / 2
    name_y = (HEIGHT - name_height) / 2 - 110

    course_x = (WIDTH - course_width) / 2
    course_y = (HEIGHT + course_height) / 2 - 255

    draw.text((name_x, name_y), name, fill=color, font=font)
    draw.text((course_x, course_y), course, fill=color, font=font2)

    source = f'images/{name}.png'
    image_source.save(source)
    img = Image.open(source)
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=60) 
    img_io.seek(0)

    storage = settings.firebase.storage()
    storage_path = f"certificate/" + f"{name}_{date}"
    storage.child(storage_path).put(img_io)
    print('Saving Certificate of:', name)
    os.remove(source)

    return storage.child(storage_path).get_url(None)
