import os
from bs4 import BeautifulSoup
import lxml
import PIL
from PIL import Image

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

def goglib_get_banner(banner_path, *args):

    banner_height = 240
    game_name = os.path.basename(banner_path).split('.jpg')[0]
    print("Getting picture for: '" + game_name + "'")

    req = urllib_request('https://www.gog.com/game/' + game_name)

    try:
        game_page = urllib_urlopen(req)
        game_page_content = game_page.read()
        soup = BeautifulSoup(game_page_content, 'lxml')
        raw_data = soup.find('picture').find_all('source')

        banner_url = raw_data[0]['srcset'].split('_')[0] + '.jpg'

        if banner_url.startswith('http'):
            banner_req = urllib_request(banner_url)
        else:
            banner_req = urllib_request('https:' + banner_url)

        banner_data = urllib_urlopen(banner_req).read()
        banner_file = open(banner_path, 'wb')
        banner_file.write(banner_data)
        banner_file.close()

        pic_src = Image.open(banner_path)
        scale_lvl = banner_height/float(pic_src.size[1])
        scaled_width = int(float(pic_src.size[0])*scale_lvl)
        pic = pic_src.resize((scaled_width, banner_height), PIL.Image.ANTIALIAS)
        if len(args) > 0:
            pic = pic.convert('L')
        pic.save(banner_path)

    except urllib_urlerror as e:
        print(e.reason)
    except urllib_httperror as e:
        print(e.code)
        print(e.read())
    except:
        goglib_recreate_banner.goglib_recreate_banner(game_name, banner_path)
