import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import urllib.request
import json
from PIL import Image
import os
import cv2

def dump_response(response):
    print("Upload response:")
    for key in sorted(response.keys()):
        print("  %s: %s" % (key, response[key]))

SEARCH_PATH = u"H:\Downloads\organized_wallpaper\\"
NEW_PATH = u"H:\Downloads\cropped_wallpaper\\"

f = open('cloudinaryConfig.json')
config = json.load(f)

cloudinary.config( 
  cloud_name = config['cloud_name'], 
  api_key = config['api_key'], 
  api_secret = config['api_secret']
)

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(SEARCH_PATH)) for f in fn if '.jpg' or '.png' in f.lower()]

for image in images:
    if os.stat(image).st_size > 10485760:
        continue
    # Handle different characters in folder/image name
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
      new_path = ""
      if width > height:
          width = im.width 
          height = round(im.width * 9 / 16)
          new_path = NEW_PATH + '16x9'
      else:
          width = round(im.height * 9 / 16)
          height = im.height
          new_path = NEW_PATH + '9x16'

      imageTag = cloudinary.CloudinaryImage(public_id).image(width=width, height=height, gravity="auto", crop="crop", secure=True)
      url = imageTag.split(" ")[2].split("=")[1].replace('"', '')
      urllib.request.urlretrieve(url, new_path+"\\"+splitName[-1])

      # CLEAN UP
      cloudinary.uploader.destroy(public_id)
    os.remove(image)

    

