from ..myqrcode import create_qrcode_from_text_with_logo

if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'qrcode.png'     # 生成带有图标的二维码
    logo_path = 'logo.jpeg'      # 用于填充的图标
    create_qrcode_from_text_with_logo(text, save_path, logo_path)
