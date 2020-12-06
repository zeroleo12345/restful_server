from utils.myqrcode import Qrcode


if __name__ == '__main__':
    text = 'http://www.baidu.com'
    save_path = 'out.png'
    icon_path = 'icon.jpeg'
    icon_img = Qrcode.convert_local_icon_to_img(icon_path=icon_path)
    Qrcode.add_icon_on_qrcode(qrcode_text=text, icon_img=icon_img, save_path=save_path)
