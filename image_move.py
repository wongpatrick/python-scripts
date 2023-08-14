import os
import shutil
import numpy as np
import cv2

search_path = u"H:\Downloads\\wallpaper"

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(search_path)) for f in fn if '.jpg' in f.lower()]

# os.mkdir('downloaded_images')

for image in images:
    print(image)

    stream = open(image, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    im = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    stream.close()

    new_path = ""
    height, width, channel = im.shape
    if width > height:
        print("Potentially 16:9")
        new_path = 'downloaded_images/16x9'
    else:
        print("Potentially 9:16")
        new_path = 'downloaded_images/9x16'
    
    shutil.move(image, new_path)