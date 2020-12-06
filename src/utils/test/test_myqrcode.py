from ..myqrcode import add_logo_on_qrcode_from_text

if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'qrcode.png'     # 生成带有图标的二维码
    logo_path = 'logo.jpeg'      # 用于填充的图标
    add_logo_on_qrcode_from_text(text, save_path, logo_path)
