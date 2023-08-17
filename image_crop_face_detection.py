from PIL import Image
import dlib
import numpy as np

face_detector = dlib.get_frontal_face_detector()

input_image = Image.open("pic_4.jpg")

image_array = np.array(input_image)

faces = face_detector(image_array)

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
    x2 = min(input_image.width, x_center + crop_width // 2)
    y1 = 0 # max(0, y_center - crop_height // 2) need to adjust this for 16x9
    y2 = input_image.height #min(input_image.height, y_center + crop_height // 2)
else:
    crop_width = input_image.width
    crop_height = int(crop_width * 9 / 16)
    x1 = 0
    x2 = crop_width
    y1 = max(0, y_center - crop_height // 2)
    y2 = min(input_image.height, y_center + crop_height // 2)

crop_box = (x1, y1, x2, y2)
cropped_image = input_image.crop(crop_box)

cropped_image.save("output_cropped_image.jpg")
cropped_image.show()