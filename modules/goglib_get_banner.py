import os
import PIL
from PIL import Image

from gogapi import GogApi, Token
from modules import goglib_recreate_banner

try:
    from urllib2 import Request as urllib_request
    from urllib2 import urlopen as urllib_urlopen
    from urllib2 import URLError as urllib_urlerror
    from urllib2 import HTTPError as urllib_httperror
except:
    from urllib.request import Request as urllib_request
    from urllib.request import urlopen as urllib_urlopen
    from urllib.request import URLError as urllib_urlerror
    from urllib.request import HTTPError as urllib_httperror

def goglib_get_banner(banner_path, unavailable_path, game_id, *args):

    banner_height = 240
    game_name = os.path.basename(banner_path).split('.jpg')[0]
    print("Getting picture for: '" + game_name + "'")

    try:
        token_path = os.getenv('HOME') + '/.config/lgogdownloader/galaxy_tokens.json'
        token = Token.from_file(token_path)
        if token.expired():
            token.refresh()
            token.save(token_path)
        api = GogApi(token)

        prod = api.product(game_id)
        prod.update_galaxy(expand=True)
        banner_url = 'https:' + ''.join(prod.image_logo.split('_glx_logo'))

        banner_req = urllib_request(banner_url)
        banner_data = urllib_urlopen(banner_req).read()
        banner_file = open(banner_path, 'wb')
        banner_file.write(banner_data)
        banner_file.close()

        pic_src = Image.open(banner_path)
        scale_lvl = banner_height/float(pic_src.size[1])
        scaled_width = int(float(pic_src.size[0])*scale_lvl)
        pic = pic_src.resize((scaled_width, banner_height), PIL.Image.ANTIALIAS)
        pic.save(banner_path)
        pic = pic.convert('L')
        pic.save(unavailable_path)

    except urllib_urlerror as e:
        print(e.reason)
    except urllib_httperror as e:
        print(e.code)
        print(e.read())
    except:
        goglib_recreate_banner.goglib_recreate_banner(game_name, banner_path)
