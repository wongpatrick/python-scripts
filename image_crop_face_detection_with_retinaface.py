# from numba import jit, cuda 

import os
import shutil
from PIL import Image
import dlib
import numpy as np
import cv2
from retinaface import RetinaFace

SEARCH_PATH = u"H:\\Downloads\\organized_wallpaper\\"
NEW_PATH = u"H:\\Downloads\\cropped_wallpaper\\"
ERROR_PATH = u"H:\\Downloads\\error_wallpaper\\"

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]
Image.MAX_IMAGE_PIXELS = 933120000

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
            print("Working on "+ image)

            image_array = np.array(input_image)
            faces = RetinaFace.detect_faces(image_array)
            new_path = NEW_PATH

            # Calculate the center of focus
            if len(faces) > 0:
                x = []
                y = []
                for face in faces:
                    # print(faces[face])
                    (right, top, left, bottom) = faces[face]["facial_area"]
                    x.append((left + right) // 2)
                    y.append((top + bottom) // 2)
                x_center = np.average(x)
                y_center = np.average(y)
            else:
                raise Exception("Can not find face")
                # x_center = input_image.width // 2
                # y_center = input_image.height // 2

            # Determine if 9x16 or 16x9
            if input_image.height > input_image.width:
                new_path += '9x16'
                crop_height = input_image.height 
                crop_width =  min(int(crop_height * 9 / 16), input_image.width)
                if crop_width == input_image.width: # make sure to make it 9x16
                    crop_height = int(crop_width * 16 / 9)

            else:
                new_path += '16x9'
                crop_width = input_image.width
                crop_height = min(int(crop_width * 9 / 16), input_image.height)
                if crop_height == input_image.height: # make sure to make it 16x9
                    crop_width = int(crop_height * 16 / 9)
                
            x1 = max(0, x_center - crop_width // 2)
            if x1 == 0:
                x2 = crop_width
            else:
                x2 = min(input_image.width, x_center + crop_width // 2)
                if x2 == input_image.width:
                    x1 = input_image.width - crop_width
            y1 = max(0, y_center - crop_height // 2)
            if y1 == 0:
                y2 = crop_height
            else:
                y2 = min(input_image.height, y_center + crop_height // 2)
                if y2 == input_image.height:
                    y1 = input_image.height - crop_height

            if y2 > input_image.height:
                raise Exception("Y2 is too far")
            if x2 > input_image.width:
                raise Exception("X2 is too far")

            crop_box = (x1, y1, x2, y2)
            cropped_image = input_image.crop(crop_box)

            cropped_image.save(image)
            shutil.move(image, new_path)
    except Exception as e:
        shutil.move(image, ERROR_PATH)
        print(image + " failed ", e)

# if __name__=="__main__":
#     image_crop()