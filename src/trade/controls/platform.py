# 项目库
from service.wechat.we_client import WeClient
from trade.models import Account, Platform, User
from settings import log


def create_new_platform(user_id):
    # 成为平台属主
    user = User.get(user_id=user_id)
    assert user
    account = Account.get(user_id=user.user_id, platform_id=user.bind_platform_id)
    assert account
    platform = Platform.get(owner_user_id=user.user_id)
    if not platform:
        # SELECT `AUTO_INCREMENT` FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'trade' AND table_name = 'platform';
        # ALTER TABLE `platform` AUTO_INCREMENT = 3;
        platform = Platform.create(owner_user_id=user.user_id)
    platform.platform_id = platform.id
    qrcode_info = WeClient.create_qrcode(scene_str=str(platform.platform_id), is_permanent=True)
    log.d(f'qrcode_info: {qrcode_info}')
    qrcode_content = qrcode_info['url']
    log.i(f'create qrcode, platform_id: {platform.platform_id}, qrcode_content: {qrcode_content}')
    platform.update(qrcode_content=qrcode_content, platform_id=platform.id, ssid=f'WIFI-{platform.platform_id}')
    user.update(bind_platform_id=platform.platform_id)
    account.update(role=Account.Role.PLATFORM_OWNER.value, platform_id=user.bind_platform_id)
    return platform
