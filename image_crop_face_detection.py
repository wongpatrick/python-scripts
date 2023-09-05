import os
import shutil
from PIL import Image
import dlib
import numpy as np
import cv2

SEARCH_PATH = u"H:\Downloads\organized_wallpaper\\"
NEW_PATH = u"H:\Downloads\cropped_wallpaper\\"

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]


face_detector = dlib.get_frontal_face_detector()

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
        # input_image = Image.open("pic_4.jpg")
            print("Working on "+ image)

            image_array = np.array(input_image)

            faces = face_detector(image_array)
            new_path = NEW_PATH

            # need to focus on all faces when multiple are present maybe find the middle point of all the faces
            if len(faces) > 0:
                face = faces[0]  # Assuming you want to focus on the first detected face
                x_center = (face.left() + face.right()) // 2
                y_center = (face.top() + face.bottom()) // 2
            else:
                x_center = input_image.width // 2
                y_center = input_image.height // 2



            if input_image.height > input_image.width:
                crop_height = input_image.height 
                crop_width = int(crop_height * 9 / 16)
                x1 = max(0, x_center - crop_width // 2)
                if x1 == 0:
                    x2 = crop_width
                else:
                    x2 = min(input_image.width, x_center + crop_width // 2)
                    if x2 == input_image.width:
                        x1 = input_image.width - crop_width
                y1 = 0
                y2 = input_image.height
                new_path += '9x16'
            else:
                crop_width = input_image.width
                crop_height = int(crop_width * 9 / 16)
                x1 = 0
                x2 = crop_width
                y1 = max(0, y_center - crop_height // 2)
                if y1 == 0:
                    y2 = crop_height
                else:
                    y2 = min(input_image.height, y_center + crop_height // 2)
                    if y2 == input_image.height:
                        y1 = input_image.height - crop_height
                new_path += '16x9'

            crop_box = (x1, y1, x2, y2)
            cropped_image = input_image.crop(crop_box)

            cropped_image.save(image)
            shutil.move(image, new_path)
    except:
        print(image + " failed")