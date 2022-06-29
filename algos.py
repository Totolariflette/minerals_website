from PIL import Image
from threading import Thread
import os
from time import sleep
from keras.models import model_from_json

uploads_path = "static/uploads"
nns_path = "NNs"
max_image_size = 1500

is_uploading = False
upload_time_limit = 60  # seconds


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


def _apply_nn_on_image(nn_name, filename):
    Thread(target=_apply_nn_on_image, args=(nn_name, filename,)).start()


def apply_nn_on_image(nn_name, filename):
    # Big images might still be uploaded so we're waiting for them
    # after upload_time_limit seconds it considers that there is a problem
    for i in range(upload_time_limit):
        if is_uploading:
            sleep(1)
        else:
            break
    if is_uploading:
        return

    # Here we get the model and run it
    nn_path = os.path.join(nns_path, nn_name)
    nn_files = [f for f in os.listdir(nn_path)]
    model_file = ""
    weights_file = ""
    if len(nn_files) >= 2:
        for file in nn_files:
            if file.endswith('.json'):
                model_file = os.path.join(nn_path, file)
            if file.endswith('.h5'):
                weights_file = os.path.join(nn_path, file)
    if model_file == "" or weights_file == "":  # Quit if we don't have the 2 correct files
        print("Incorrect files")
        return

    json_file = open(model_file, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(weights_file)
    # TODO Predict the output
