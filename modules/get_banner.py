import os
import PIL
from PIL import Image

try:
    from urllib2 import Request as urllib_request
    from urllib2 import urlopen as urllib_urlopen
    from urllib2 import URLError as urllib_urlerror
    from urllib2 import HTTPError as urllib_httperror
except:
    from urllib import request as urllib_request
    urllib_urlopen = urllib_request.urlopen
    urllib_urlerror = urllib_request.URLError
    urllib_httperror = urllib_request.HTTPError

def get_banner(game_name, url, banner_path, lib):

    banner_req = urllib_request(url)

    try:

        if not os.path.exists(banner_path):
            os.makedirs(banner_path)

        banner_data = urllib_urlopen(banner_req).read()
        banner_file = open(banner_path + '/' + game_name + '.jpg', 'wb')
        banner_file.write(banner_data)
        banner_file.close()

        pic_src = Image.open(banner_path + '/' + game_name + '.jpg')
        pic = pic_src.resize((518, 240), PIL.Image.ANTIALIAS)
        pic.save(banner_path + '/' + game_name + '.jpg')

        if lib == 'goglib':

            if not os.path.exists(banner_path + '/unavailable/'):
                os.makedirs(banner_path + '/unavailable/')

            new_pic = Image.open(banner_path + '/' + game_name + '.jpg')
            pic_grey = new_pic.convert('L')
            pic_grey.save(banner_path + '/unavailable/' + game_name + '.jpg')

    except urllib_urlerror as e:
        print(e.reason)
    except urllib_httperror as e:
        print(e.code)
        print(e.read())

if __name__ == "__main__":
    import sys
    get_banner(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
