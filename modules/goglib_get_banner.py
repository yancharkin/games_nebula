import os
from bs4 import BeautifulSoup
import lxml
import PIL
from PIL import Image
import json

try:
    from fuzzywuzzy import fuzz
    use_fuzzy = True
except:
    print('you may want to use <pip install fuzzywuzzy> for more accurate images')
    use_fuzzy = False

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

SEARCH_API = 'https://embed.gog.com/games/ajax/filtered?mediaType=game&search='

def find_image(query):
    global use_fuzzy
    product_json = json.loads(urllib_urlopen(SEARCH_API + query.replace('_', ' ')).read().decode('utf-8'))
    if use_fuzzy:
        best_match = None
        closest_ratio = 0
        for product in product_json['products']:
            ratio = fuzz.token_set_ratio(query, product['slug'])
            if ratio > closest_ratio:
                closest_ratio = ratio
                best_match = product
        return 'https:' + best_match['image'] + '.jpg'
    else:
        for product in product_json['products']:
            if product['slug'] == query:
                return 'https:' + product['image'] + '.jpg'

def goglib_get_banner(banner_path, *args):

    banner_height = 240
    game_name = os.path.basename(banner_path).split('.jpg')[0]

    try:
        banner_url = find_image(game_name)

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
