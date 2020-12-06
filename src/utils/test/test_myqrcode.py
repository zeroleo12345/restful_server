from utils.myqrcode import Qrcode


if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'out.png'
    logo_path = 'logo.jpeg'
    logo_img = Qrcode.get_logo_img(logo_path=logo_path)
    Qrcode.add_logo_on_qrcode(qrcode_text=text, logo_img=logo_img, save_path=save_path)
