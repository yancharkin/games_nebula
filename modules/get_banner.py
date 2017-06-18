import os
import urllib2
import PIL
from PIL import Image

def get_banner(game_name, url, banner_path, lib):

    banner_req = urllib2.Request(url)

    try:

        if not os.path.exists(banner_path):
            os.makedirs(banner_path)

        banner_data = urllib2.urlopen(banner_req).read()
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

    except urllib2.URLError as e:
        print e.reason
    except urllib2.HTTPError as e:
        print e.code
        print e.read()

if __name__ == "__main__":
    import sys
    get_banner(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
