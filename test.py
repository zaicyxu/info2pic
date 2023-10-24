import os
import numpy as np
from PIL import Image

def is_grayscale(image):
    img_arr = np.array(image)
    diff = np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 1].astype(np.int16)) + \
           np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 2].astype(np.int16)) + \
           np.abs(img_arr[:, :, 1].astype(np.int16) - img_arr[:, :, 2].astype(np.int16))
    grayscale = np.max(diff) < 25
    return grayscale

def find_grayscale_images(folder_path):
    grayscale_images = []
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for file in image_files:
        image_path = os.path.join(folder_path, file)
        try:
            image = Image.open(image_path)
            if is_grayscale(image):
                grayscale_images.append(file)
        except Exception as e:
            print("Error opening image:", file)
            print(e)
    return grayscale_images

# 示例用法
folder_path = r"D:\work\add_info2pic\抗体图\一抗图库\2023\06\06"
grayscale_images = find_grayscale_images(folder_path)
print("Grayscale images found:", grayscale_images)
