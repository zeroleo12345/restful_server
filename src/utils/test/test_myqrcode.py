from utils.myqrcode import Qrcode


if __name__ == '__main__':

    # icon_path = 'icon.jpeg'
    # icon_img = Qrcode.convert_local_icon_to_img(icon_path=icon_path)

    icon_url = 'http://thirdwx.qlogo.cn/mmopen/vi_32/3IySpcoGTPQu2WbNUGFhq2icLicJpMS1uFdfDWFdE0lv9cjPGeEBors5E6fXqo0ictQlRws1ZwpUTVQS6yDeVsDeQ/132'
    icon_img = Qrcode.convert_web_icon_to_img(icon_url=icon_url)

    text = 'http://www.baidu.com'
    save_path = 'out.png'
    Qrcode.add_icon_on_qrcode(qrcode_text=text, icon_img=icon_img, save_path=save_path)
