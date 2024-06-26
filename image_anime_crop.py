import cv2
from PIL import Image

import sys
import os.path
import shutil
import numpy as np

SEARCH_PATH = u"H:\Downloads\organized_wallpaper\\"
NEW_PATH = u"H:\Downloads\cropped_wallpaper\\"
ERROR_PATH = u"H:\Downloads\error_wallpaper\\"

def detect(filename, cascade_file = "./lbpcascade_animeface.xml"):
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)

    cascade = cv2.CascadeClassifier(cascade_file)
    
    with Image.open(filename) as input_image:
        print("Working on "+ filename)
        new_path = NEW_PATH


        input_detection = cv2.imread(filename, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(input_detection, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = cascade.detectMultiScale(gray,
                                        # detector options
                                        scaleFactor = 1.1,
                                        minNeighbors = 5,
                                        minSize = (24, 24))
        for (x, y, w, h) in faces:
            cv2.rectangle(input_detection, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if len(faces) > 0:
            x_arr = []
            y_arr = []
            for face in faces:
                x,y,w,h = face
                x_arr.append((x + w) // 2)
                y_arr.append((y + h) // 2)
            x_center = np.average(x_arr)
            y_center = np.average(y_arr)
        else:
            raise Exception("Found no face")

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
        cropped_image.save(filename)
        shutil.move(filename, new_path)

# if len(sys.argv) != 2:
#     sys.stderr.write("usage: detect.py <filename>\n")
#     sys.exit(-1)

# detect(sys.argv[1])
        
images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]

for image in images:
    splitName = image.split('\\')
    stream = open(image, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    im = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    stream.close()
    os.rename(image, '\\'.join(splitName))
    image = '\\'.join(splitName)
    try:
        detect(image)
    except Exception as e:
        shutil.move(image, ERROR_PATH)
        print(image + " failed ", e)