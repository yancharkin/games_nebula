## ! Module not used ! ##

import PIL
from PIL import Image

def goglib_recreate_banner(game_name, icon_path, banner_path):

    icon = Image.open(icon_path + game_name + '.jpg')
    icon = icon.resize((150, 150), PIL.Image.ANTIALIAS)

    banner = Image.open(banner_path + '/' + game_name + '.jpg')
    offset = ((banner.size[0] - 150)/2, (banner.size[1] - 150)/2)
    banner.paste(icon, offset)
    banner.save(banner_path + '/' + game_name + '.jpg')

if __name__ == "__main__":
    import sys
    goglib_recreate_banner(sys.argv[1], sys.argv[2], sys.argv[3])
