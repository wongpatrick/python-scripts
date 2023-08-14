"""
This script is essentially for sorting out images 
I would need to crop for either 16:9 or 9:16
"""

import os
import shutil
import numpy as np
import cv2

search_path = u"H:\Downloads\\wallpaper"
NEW_PATH = u"H:\Downloads\organized_wallpaper\\"

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(search_path)) for f in fn if '.jpg' or '.png' in f.lower()]

# os.mkdir('downloaded_images')

for image in images:
    splitName = image.split('\\')
    newName = splitName[-2] + ' - ' + splitName[-1]
    splitName[-1] = newName
    
    stream = open(image, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    im = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    stream.close()

    os.rename(image, '\\'.join(splitName))
    image = '\\'.join(splitName)
    
    new_path = ""
    height, width, channel = im.shape
    if width > height:
        new_path = NEW_PATH + '16x9'
    else:
        new_path = NEW_PATH + '9x16'
    
    shutil.move(image, new_path)