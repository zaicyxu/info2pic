# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Zaicy Xu
@Version        :  5.0
------------------------------------
@File           :  main
@Description    :
@CreateTime     :  2023/03/03 10:35
Add text to pic aimed place.
"""

import os
import openpyxl
import numpy as np
import cv2
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
from shutil import move, copy
from tqdm import tqdm
import pickle


def is_grayscale_image(img_path):
    """
    判断一张照片是否为黑白图片
    :param img_path: 图片路径
    :return: True 表示是黑白图片，False 表示不是黑白图片
    """
    img = Image.open(img_path)
    img_arr = np.array(img)
    diff = np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 1].astype(np.int16)) + \
           np.abs(img_arr[:, :, 0].astype(np.int16) - img_arr[:, :, 2].astype(np.int16)) + \
           np.abs(img_arr[:, :, 1].astype(np.int16) - img_arr[:, :, 2].astype(np.int16))
    grayscale = np.max(diff) < 25
    return grayscale


def is_covered_image(im):
    is_grayscale = False
    # 如果通道的插值的最大值小于30，那么说明是黑白图
    im = np.array(im)
    # diff = np.abs(im[:, :, 0] - im[:, :, 1])
    # diff = np.abs(im[:, :, 1] - im[:, :, 2])
    # diff = np.abs(im[:, :, 2] - im[:, :, 3])
    # diff = np.abs(im[:, :, 3] - im[:, :, 0])
    diff = np.abs(im[:, :, 0].astype(np.int16) - im[:, :, 1].astype(np.int16)) + \
           np.abs(im[:, :, 0].astype(np.int16) - im[:, :, 2].astype(np.int16)) + \
           np.abs(im[:, :, 1].astype(np.int16) - im[:, :, 2].astype(np.int16))
    if np.max(diff) < 30:
        is_grayscale = True
        # 如果是黑白图，那么看看左上角的区域有没有小于120的点，并且记录点的个数如果大于280则是表示被覆盖
        if is_grayscale:
            gray_im = np.array(Image.fromarray(np.array(im)).convert('L'))
            region = gray_im[5:206, 5:426]
            black_pix_count = len(region[region < 125])
            if black_pix_count > 260:
                return True
            else:
                return False
    else:
        return False


def get_covered_images(pic_p):
    image_paths = [os.path.join(root, file) for root, dirs, files in os.walk(pic_p) for file in files if
                   file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png')]
    covered_img_list = []
    for img_path in image_paths:
        img = Image.open(img_path)
        img_name = os.path.basename(img_path)
        grayscale = is_grayscale_image(img_path)
        gray_img = img.convert('L')
        if grayscale:
            non_white_pixels = 0
            for x in range(5, 426):
                for y in range(5, 206):
                    pixel = gray_img.getpixel((x, y))
                    if pixel < 125:
                        non_white_pixels += 1
            if non_white_pixels > 260:
                covered_img_list.append(img_name)
            print(covered_img_list)
    return covered_img_list


def add_text(pic_p, file_p):
    # 打开图片文件
    image_folder_path = pic_p
    saved_dir = image_folder_path + '_saved'
    if not os.path.exists(saved_dir):
        os.mkdir(saved_dir)
    covered_dir = os.path.join(image_folder_path + '_saved', 'covered')
    # 定义支持的文件扩展名
    extensions = ['.jpg', '.jpeg', '.png']

    # 获取文件夹及子文件夹内所有符合条件的文件
    image_file_names = [file for root, dirs, files in os.walk(image_folder_path) for file in files if
                        os.path.splitext(file)[1].lower() in extensions]

    wb = openpyxl.load_workbook(file_p)
    ws = wb.active
    data_dict_orig = {row[0]: (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]) for row in
                      ws.iter_rows(min_row=2, values_only=True)}
    data_dict = {}
    for k, v in data_dict_orig.items():
        data_dict[os.path.split(k)[-1]] = v
    im_template = np.array(Image.open(r'./template.png'))
    # im_template = np.array(Image.open(r'D:/work/add_info2pic/template.png'))
    total_count = len(image_file_names)
    im_ps = []
    for root, dirs, files in os.walk(image_folder_path):
        if len(files) > 0:
            for file in files:
                im_ps.append(os.path.join(root, file))

    collect_unsaved = []
    for s, im_p in enumerate(im_ps):
        img = Image.open(im_p)
        im_name = os.path.split(im_p)[-1]
        # 获得图片的保存路径
        saved_p = im_p.replace(image_folder_path, image_folder_path + '_saved')
        # ###################################################
        # 通过转变成灰度图，判断其亮度，然后决定用什么颜色的框和字
        gray_img = ImageOps.grayscale(img)
        stat = ImageStat.Stat(gray_img)
        brightness = stat.mean[0]
        if brightness > 125:
            text_color = (0, 0, 0)
            im2_inv = 255 - im_template
            im2 = np.dstack((im2_inv, im2_inv, im2_inv, np.array(im_template > 0, np.uint8) * 60))
        else:
            text_color = (255, 255, 255)
            im2 = np.dstack((im_template, im_template, im_template, np.array(im_template > 0, np.uint8) * 80))
        # ##################################################
        if im_name in data_dict:
            # img = Image.open(img_path)
            # ##################### 给单张图画框，写字 ####################
            img_org = np.array(img).copy()
            draw = ImageDraw.Draw(img)
            im2_ma = Image.fromarray(np.array(cv2.resize(im2, (420, 200)), np.uint8))
            img.paste(im2_ma, (5, 5), im2_ma)

            # 指定文字内容和颜色
            font = ImageFont.truetype('./AlibabaPuHuiTi-2-65-Medium.ttf', 20)
            font2 = ImageFont.truetype('./AlibabaPuHuiTi-2-45-Light.ttf', 20)
            text_lines = data_dict[im_name]
            text1 = text_lines[0]
            text2_tips = "货号:"
            text3_tips = "应用:"
            text2 = text_lines[1]
            text3_1 = (text_lines[2] or '') + " | " + (text_lines[3] or '')
            text3_2 = (text_lines[4] or '') + " | " + (text_lines[5] or '')
            text3_3 = (text_lines[6] or '') + " | " + (text_lines[7] or '')
            if text3_1 == " | ":
                text3_1 = ""
            if text3_2 == " | ":
                text3_2 = ""
            if text3_3 == " | ":
                text3_3 = ""

            # 左上角显示
            x1 = 25
            x2 = 80
            # 计算每行文本绘制的位置（左上角）
            y1 = 25
            y2 = y1 + (font.getsize(text1)[1] * 2) + 5
            y3 = y2 + font.getsize(text2)[1] + 5
            y3_2 = y3 + font.getsize(text2)[1] + 5
            y3_3 = y3_2 + font.getsize(text2)[1] + 5

            # 绘制每行文本
            lines = textwrap.wrap(text1, width=35)
            for line in lines:
                draw.text((x1, y1), line, font=font, fill=text_color)
                y1 += font.getsize(line)[1]
            # draw.text((x1, y1),  text1, font=font, fill=text_color)
            draw.text((x1, y2), text2_tips, font=font2, fill=text_color)
            draw.text((x2, y2), text2, font=font, fill=text_color)
            draw.text((x1, y3), text3_tips, font=font2, fill=text_color)
            draw.text((x2, y3), text3_1, font=font, fill=text_color)
            draw.text((x2, y3_2), text3_2, font=font, fill=text_color)
            draw.text((x2, y3_3), text3_3, font=font, fill=text_color)
            # ######################################################
            # 判断左上角的框里面是否有图片的文字，前提是图片是WB图
            # 当存在被覆盖的图片的时候，新建一次文件夹，并且将图片放入其中
            if is_covered_image(img_org):
                if not os.path.exists(covered_dir):
                    os.mkdir(covered_dir)
                img.save(os.path.join(covered_dir, im_name))
                print('%d/%d, !!! covered image saved path: %s' % (s, total_count, im_name))
            # 如果没有被覆盖，那么替换原始的图片
            else:
                if not os.path.exists(os.path.split(saved_p)[0]):
                    os.makedirs(os.path.split(saved_p)[0])
                img.save(saved_p, quality=100)
                print('%d/%d, saved path: %s' % (s, total_count, im_name))
            # # if choose == 'yes':
            # if img_name in covered_img_list:
            #     if not os.path.exists(covered_dir):
            #         os.mkdir(covered_dir
            #     img.save(os.path.join(covered_dir, img_name))
            # else:
            #     img.save(os.path.join(img_path))
        else:
            print('%d/%d, ---unsaved path: %s' % (s, total_count, im_name))
            collect_unsaved.append(im_name)
    if len(collect_unsaved) > 0:
        with open('unsaved_path.pkl', 'wb') as f:
            pickle.dump(collect_unsaved, f)

            # if img_name in covered_img_list:
            #     covered_dir = os.path.join(image_folder_path, 'covered')
            #     if not os.path.exists(covered_dir):
            #         os.mkdir(covered_dir)
            #     img.save(os.path.join(covered_dir, img_name))
            # else:
            #     result_dir = os.path.join(image_folder_path, 'result')
            #     if not os.path.exists(result_dir):
            #         os.mkdir(result_dir)
            #     img.save(os.path.join(result_dir, img_name))


if __name__ == '__main__':
    file_p = r'./导入.xlsx'
    pic_p = r'./抗体图'
    # choose = 'yes'
    # get_text(file_p)
    add_text(pic_p, file_p)
