"""
This script is essentially for cropping the image
to the right aspect ratio with cloudinary
"""
import shutil

import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import urllib.request
import json
from PIL import Image
import os
import cv2

SEARCH_PATH = u"H:\\Downloads\\organized_wallpaper\\"
NEW_PATH = u"H:\\Downloads\\cropped_wallpaper\\"
ERROR_PATH = u"H:\\Downloads\\error_wallpaper\\"

f = open('cloudinaryConfig.json')
config = json.load(f)

cloudinary.config( 
  cloud_name = config['cloud_name'], 
  api_key = config['api_key'], 
  api_secret = config['api_secret']
)

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]
Image.MAX_IMAGE_PIXELS = 933120000

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


    with Image.open(image) as im:
      print("Working on "+ image)
      response = cloudinary.uploader.upload(image)
      public_id = response['public_id']

      width = im.width
      height = im.height
      new_path = NEW_PATH

      # Determine if 9x16 or 16x9
      if im.height > im.width:
          new_path += '9x16'
          height = im.height 
          width =  min(int(height * 9 / 16), im.width)
          if width == im.width: # make sure to make it 9x16
              height = int(width * 16 / 9)
      else:
          new_path += '16x9'
          width = im.width
          height = min(int(width * 9 / 16), im.height)
          if height == im.height: # make sure to make it 16x9
              width = int(height * 16 / 9)


      # if width > height:
      #     height = round(im.width * 9 / 16)
      #     new_path += '16x9'
      # else:
      #     width = round(im.height * 9 / 16)
      #     new_path += '9x16'

      imageTag = cloudinary.CloudinaryImage(public_id).image(width=width, height=height, gravity="auto", crop="crop", secure=True)
      url = imageTag.split(" ")[2].split("=")[1].replace('"', '')
      urllib.request.urlretrieve(url, new_path+"\\"+splitName[-1])

      # CLEAN UP
      cloudinary.uploader.destroy(public_id)
    os.remove(image)
  except Exception as e:
      shutil.move(image, ERROR_PATH)
      print(image + " failed ", e)


    

