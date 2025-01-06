# from numba import jit, cuda 

import os
import shutil
from PIL import Image
# import dlib
import numpy as np
import cv2
from retinaface import RetinaFace

SEARCH_PATH = u"H:\\Downloads\\organized_wallpaper\\"
NEW_PATH = u"H:\\Downloads\\cropped_wallpaper\\"
ERROR_PATH = u"H:\\Downloads\\error_wallpaper\\"

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]
Image.MAX_IMAGE_PIXELS = 933120000

def calculate_aspect_ratio(width, height):
    return round(width / height, 2)

TARGET_RATIO_9x16 = round(9 / 16, 2)
TARGET_RATIO_16x9 = round(16 / 9, 2)
TARGET_RATIO_16x10 = round(16 / 10, 2)

# face_detector = dlib.get_frontal_face_detector()
for image in images:
    try:
        splitName = image.split('\\')
        stream = open(image, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        im = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        stream.close()
        os.rename(image, '\\'.join(splitName))
        image = '\\'.join(splitName)
        

        with Image.open(image) as input_image:
            print(f"Processing: {image}")
            
            width, height = input_image.width, input_image.height
            current_ratio = calculate_aspect_ratio(width, height)
            
            # Move images that already match target aspect ratio
            if current_ratio == TARGET_RATIO_9x16:
                print("Image matches 9x16 aspect ratio. Moving without cropping.")
                new_image_path = os.path.join(NEW_PATH, "9x16")
                os.makedirs(new_image_path, exist_ok=True)
                input_image.save(os.path.join(new_image_path, os.path.basename(image)))
                os.remove(image)
                continue
            elif current_ratio == TARGET_RATIO_16x9:
                print("Image matches 16x9 aspect ratio. Moving without cropping.")
                new_image_path = os.path.join(NEW_PATH, "16x9")
                os.makedirs(new_image_path, exist_ok=True)
                input_image.save(os.path.join(new_image_path, os.path.basename(image)))
                os.remove(image)
                continue

            # Detect faces and calculate center
            image_array = np.array(input_image)
            faces = RetinaFace.detect_faces(image_array)
            if not faces:
                raise Exception("No face detected. Skipping image.")

            # Calculate center of detected faces
            x_coords = [(face["facial_area"][0] + face["facial_area"][2]) // 2 for face in faces.values()]
            y_coords = [(face["facial_area"][1] + face["facial_area"][3]) // 2 for face in faces.values()]
            x_center = int(np.mean(x_coords))
            y_center = int(np.mean(y_coords))

            # Calculate target crop dimensions
            if height > width:  # Portrait
                target_width = min(width, int(height * 9 / 16))
                target_height = int(target_width * 16 / 9)
            else:  # Landscape
                target_height = min(height, int(width * 9 / 16))
                target_width = int(target_height * 16 / 9)

            # Adjust crop box to stay within bounds
            x1 = x_center - target_width // 2
            y1 = y_center - target_height // 2
            x2 = x1 + target_width
            y2 = y1 + target_height

            if x1 < 0:  # Push right if left edge is out of bounds
                x1 = 0
                x2 = target_width
            if x2 > width:  # Push left if right edge is out of bounds
                x2 = width
                x1 = width - target_width
            if y1 < 0:  # Push down if top edge is out of bounds
                y1 = 0
                y2 = target_height
            if y2 > height:  # Push up if bottom edge is out of bounds
                y2 = height
                y1 = height - target_height

            # Crop and save
            crop_box = (x1, y1, x2, y2)
            cropped_image = input_image.crop(crop_box)
            new_image_path = os.path.join(NEW_PATH, f"{'9x16' if height > width else '16x9'}")
            os.makedirs(new_image_path, exist_ok=True)
            cropped_image.save(os.path.join(new_image_path, os.path.basename(image)))

            # Delete the original image after cropping
            os.remove(image)

    except Exception as e:
        error_image_path = os.path.join(ERROR_PATH, os.path.basename(image))
        shutil.move(image, error_image_path)
        print(f"Failed to process {image}: {e}")