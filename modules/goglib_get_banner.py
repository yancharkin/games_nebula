from bs4 import BeautifulSoup
import lxml
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

#~ import goglib_recreate_banner

def goglib_get_banner(game_name, icon_path, banner_path):

    req = urllib_request('https://www.gog.com/game/' + game_name)

    try:
        game_page = urllib_urlopen(req)
        game_page_content = game_page.read()
        soup = BeautifulSoup(game_page_content, 'lxml')
        raw_data = soup.findAll(attrs={'name':'og:image'})
        banner_url = raw_data[0]['content'].encode('utf-8')

        if banner_url.startswith('http'):
            banner_req = urllib_request(banner_url)
        else:
            banner_req = urllib_request('https:' + banner_url)

        banner_data = urllib_urlopen(banner_req).read()
        banner_file = open(banner_path + '/' + game_name + '.jpg', 'wb')
        banner_file.write(banner_data)
        banner_file.close()

        pic_src = Image.open(banner_path + '/' + game_name + '.jpg')
        scale_lvl = 240/float(pic_src.size[1])
        scaled_width = int(float(pic_src.size[0])*scale_lvl)
        pic = pic_src.resize((scaled_width, 240), PIL.Image.ANTIALIAS)
        pic.save(banner_path + '/' + game_name + '.jpg')

        #~ if banner_url.startswith('http'):
            #~ goglib_recreate_banner.goglib_recreate_banner(game_name, icon_path, banner_path)

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
    goglib_get_banner(sys.argv[1], sys.argv[2], sys.argv[3])
