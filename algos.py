from PIL import Image
from threading import Thread
import os

uploads_path = "static/uploads"
nns_path = "NNs"
max_image_size = 1500

is_uploading = False


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
    global is_uploading
    is_uploading = True

    image = Image.open(file)
    new_filename = file.filename
    if is_image_too_heavy(image):
        print("HEAVY")

        new_image = resize_to_display(image)
        new_filename = "resized_" + file.filename
        new_image.save(os.path.join(uploads_path, new_filename))

        save_heavy_file(image, file.filename)
    else:
        print("NOT HEAVY LEL")
        image.save(os.path.join(uploads_path, file.filename))
        is_uploading = False
    return new_filename


def task(image, filename):
    image.save(os.path.join(uploads_path, filename))


def save_heavy_file(image, filename):
    Thread(target=_save_heavy_file, args=(os.path.join(uploads_path, filename),)).start()


def _save_heavy_file(image, filename):
    global is_uploading
    image.save(os.path.join(uploads_path, filename))
    is_uploading = False


def get_nns_directories_name():
    return [name for name in os.listdir(nns_path)]
