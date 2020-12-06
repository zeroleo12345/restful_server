import os
# 第三方库
import requests
import qrcode
from PIL import Image


def add_logo_on_qrcode_from_web(qrcode_text, logo_url, save_path):
    response = requests.get(logo_url)
    # response.content
    pass


def add_logo_on_qrcode_from_text(qrcode_text, logo_path, save_path):
    """
    生成中间带logo的二维码
    :param qrcode_text: 二维码字符串
    :param save_path: 生成的二维码保存路径
    :param logo_path: logo文件路径
    :return:
    """
    assert os.path.exists(logo_path)
    img_icon = Image.open(logo_path)
    # 初步生成二维码图像
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
    qr.add_data(qrcode_text)
    qr.make(fit=True)
    img_background = qr.make_image()
    # 互动二Image实例并把颜色模式转换成RGBA
    img_background = img_background.convert('RGBA')
    img_w, img_h = img_background.size
    factor = 4
    # 计算logo尺寸
    size_w = int(img_w / factor)
    size_h = int(img_h / factor)
    # 比较并重新设置logo文件（图片pdsu.png）的尺寸
    icon_w, icon_h = img_icon.size
    if icon_w > size_w:
        icon_w = size_w
    if icon_h > size_h:
        icon_h = size_h
    img_icon = img_icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    # 计算logo的位置，并且复制到二维码中
    w = int((img_w - icon_w) / 2)
    h = int((img_h - icon_h) / 2)
    img_icon = img_icon.convert('RGBA')
    img_background.paste(img_icon, (w, h), img_icon)
    # 保存二维码
    img_background.save(save_path)
