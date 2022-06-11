from PIL import Image
from threading import Thread
import os

uploads_path = "static/uploads"
max_image_size = 1500


def resize_to_display(image):
    w, h = image.size
    maximum = max(w, h)
    if maximum > max_image_size:
        w *= max_image_size / maximum
        h *= max_image_size / maximum

    return image.resize((int(w), int(h)))


def is_image_too_heavy(image):
    w, h = image.size
    return w > max_image_size or h > max_image_size


def save_file(file):
    image = Image.open(file)
    new_filename = file.filename
    if is_image_too_heavy(image):
        print("HEAVY")

        image = resize_to_display(image)
        new_filename = "resized_" + file.filename
        image.save(os.path.join(uploads_path, new_filename))
    else:
        print("NOT HEAVY LEL")
        image.save(os.path.join(uploads_path, file.filename))
    return new_filename


def task(image, filename):
    image.save(os.path.join(uploads_path, filename))


def save_heavy_file(file):
    image = Image.open(file)
    if is_image_too_heavy(image):
        Thread(target=image.copy().save, args=(os.path.join(uploads_path, file.filename),)).start()


