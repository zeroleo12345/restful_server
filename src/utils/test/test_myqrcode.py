from utils.myqrcode import add_logo_on_qrcode_from_text


if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'out.png'
    logo_path = 'logo.jpeg'
    add_logo_on_qrcode_from_text(qrcode_text=text, save_path=save_path, logo_path=logo_path)
