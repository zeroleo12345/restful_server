import os
import sys
import qrcode
from PIL import Image


def add_logo_on_qrcode_from_web(url, path, logo=''):
    pass


def add_logo_on_qrcode_from_text(text, save_path, logo_path=''):
    """
    生成中间带logo的二维码
    :param text: 二维码字符串
    :param save_path: 生成的二维码保存路径
    :param logo_path: logo文件路径
    :return:
    """
    # 初步生成二维码图像
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    # 互动二Image实例并把颜色模式转换成RGBA
    img = img.convert('RGBA')
    if logo_path and os.path.exists(logo_path):
        try:
            icon = Image.open(logo_path)    # 打开logo文件
            img_w, img_h = img.size
        except Exception as e:
            print(e)
            sys.exit(1)
        factor = 4
        #  计算logo尺寸
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)
        #  比较并重新设置logo文件（图片pdsu.png）的尺寸
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        #  计算logo的位置，并且复制到二维码中
        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        icon = icon.convert('RGBA')
        img.paste(icon, (w, h), icon)
    img.save(save_path)           # 保存二维码
