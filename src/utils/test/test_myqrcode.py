from utils.myqrcode import add_logo_on_qrcode_from_text
from PIL import Image
import matplotlib.pyplot as plt


if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'qrcode.png'     # 生成带有图标的二维码
    logo_path = 'logo.jpeg'      # 用于填充的图标
    add_logo_on_qrcode_from_text(qrcode_text=text, save_path=save_path, logo_path=logo_path)
    # 打开图片
    img = Image.open(save_path)
    plt.imshow(img)
    plt.show()
