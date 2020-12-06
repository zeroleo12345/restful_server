import os
# 第三方库
import requests
import qrcode
from PIL import Image


class Qrcode(object):
    @staticmethod
    def convert_local_icon_to_img(icon_path: str) -> Image:
        assert os.path.exists(icon_path)
        return Image.open(icon_path)

    @staticmethod
    def convert_web_icon_to_img(icon_url: str) -> Image:
        response = requests.get(icon_url)
        response.content

    @staticmethod
    def add_icon_on_qrcode(qrcode_text: str, icon_img: Image, save_path: str):
        """
        生成中间带logo的二维码
        :param qrcode_text: 二维码字符串
        :param save_path: 生成的二维码保存路径
        :param icon_img: Image对象
        :return:
        """
        # 初步生成二维码图像
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
        qr.add_data(qrcode_text)
        qr.make(fit=True)
        img_background = qr.make_image()
        # 互动二Image实例并把颜色模式转换成RGBA
        img_background = img_background.convert('RGBA')
        bg_w, bg_h = img_background.size
        factor = 4
        # 计算logo尺寸
        size_w = int(bg_w / factor)
        size_h = int(bg_h / factor)
        # 比较并重新设置logo文件（图片pdsu.png）的尺寸
        icon_w, icon_h = icon_img.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon_img = icon_img.resize((icon_w, icon_h), Image.ANTIALIAS)
        # 计算logo的位置，并且复制到二维码中
        w = int((bg_w - icon_w) / 2)
        h = int((bg_h - icon_h) / 2)
        icon_img = icon_img.convert('RGBA')
        img_background.paste(icon_img, (w, h), icon_img)
        # 保存二维码
        img_background.save(save_path)
