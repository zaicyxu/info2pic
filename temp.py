# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Guo Youwen
@Version        :  
------------------------------------
@File           :  temp.py
@Description    :  
@CreateTime     :  2023/3/9 17:10
"""
from PIL import Image
import numpy as np
import cv2
import os

# WHITE_BACK = False
# im1 = Image.open(r'./图片\老图\2022\01\05\1641344680180622958.jpg')
# # im2 = cv2.cvtColor(np.array(Image.open(r'C:\Users\86177\Desktop\abc.png')), cv2.COLOR_GRAY2BGRA)
# im2 = np.array(Image.open(r'./template.png'))
# if WHITE_BACK:
# 	im2_inv = 255 - im2
# 	im2 = np.dstack((im2_inv, im2_inv, im2_inv, np.array(im2 > 0, np.uint8) * 20))
# else:
# 	im2 = np.dstack((im2, im2, im2, np.array(im2 > 0, np.uint8) * 80))
#
# # im2_im = Image.fromarray(np.array(cv2.resize(im2, (400, 400)), np.uint8))
# im2_ma = Image.fromarray(np.array(cv2.resize(im2, (400, 400)), np.uint8))
# im1.paste(im2_ma, (0, 0), im2_ma)
#
# im1.show()
img_path = r'D:\work\add_info2pic\抗体图\一抗图库\2023\06\06'
img = Image.open(img_path)
extensions = ['.jpg', '.jpeg', '.png']
image_names = [file for root, dirs, files in os.walk(img_path) for file in files if
					os.path.splitext(file)[1].lower() in extensions]
img_arr = np.array(img)
diff = np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 1].astype(np.int16)) + \
	   np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 2].astype(np.int16)) + \
	   np.abs(img_arr[:, :, 1].astype(np.int16) - img_arr[:, :, 2].astype(np.int16))
if np.max(diff) < 25:
	print(image_names)



