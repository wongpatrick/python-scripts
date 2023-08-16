import numpy as np
import cloudinary
import cloudinary.uploader
import cloudinary.api
import urllib.request
import json
from PIL import Image

 
f = open('cloudinaryConfig.json')
config = json.load(f)

cloudinary.config( 
  cloud_name = config['cloud_name'], 
  api_key = config['api_key'], 
  api_secret = config['api_secret']
)


with Image.open("4.jpg") as im:
    
    print(im.height)
    print(im.height * 9 / 16)
    width = round(im.height * 9 / 16)
    height = im.height

    imageTag = cloudinary.CloudinaryImage("test").image(width=width, height=height, gravity="auto", crop="crop", secure=True)

    url = imageTag.split(" ")[2].split("=")[1].replace('"', '')
    urllib.request.urlretrieve(url, "4transformedCloud.jpg")
