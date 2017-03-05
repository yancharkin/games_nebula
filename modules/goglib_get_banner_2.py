import urllib2
import PIL
from PIL import Image

import goglib_recreate_banner

def goglib_get_banner_2(game_name, url, banner_path):

    banner_req = urllib2.Request(url)

    try:

        banner_data = urllib2.urlopen(banner_req).read()
        banner_file = open(banner_path + '/' + game_name + '.jpg', 'wb')
        banner_file.write(banner_data)
        banner_file.close()

        pic_src = Image.open(banner_path + '/' + game_name + '.jpg')
        scale_lvl = 240/float(pic_src.size[1])
        scaled_width = int(float(pic_src.size[0])*scale_lvl)
        pic = pic_src.resize((scaled_width, 240), PIL.Image.ANTIALIAS)
        pic.save(banner_path + '/' + game_name + '.jpg')

        new_pic = Image.open(banner_path + '/' + game_name + '.jpg')
        pic_grey = new_pic.convert('L')
        pic_grey.save(banner_path + '/unavailable/' + game_name + '.jpg')

    except urllib2.URLError as e:
        print e.reason
    except urllib2.HTTPError as e:
        print e.code
        print e.read()

if __name__ == "__main__":
    import sys
    goglib_get_banner_2(sys.argv[1], sys.argv[2], sys.argv[3])
