import os
import PIL
from PIL import Image, ImageDraw, ImageFont

def goglib_recreate_banner(game_name, banner_path):

    nebula_dir = os.getenv('NEBULA_DIR')
    banner = Image.new('1', (518, 240), 0)
    draw = ImageDraw.Draw(banner)
    font = ImageFont.truetype(nebula_dir + '/fonts/DejaVuSans.ttf', 24)
    game_name_width = font.getsize(game_name)[0]
    game_name_height = font.getsize(game_name)[1]

    if game_name_width > 518:

        game_name_list = []
        for i in range(0, len(game_name), 28):
            game_name_list.append(game_name[i:i+28])

        all_lines_height = len(game_name_list) * game_name_height
        full_title_y = 120 - all_lines_height/2

        n = 0
        for line in game_name_list:
            line_width = font.getsize(line)[0]
            x = 259 - line_width/2
            y = full_title_y + (game_name_height * n)
            draw.text((x, y), line, fill=1, font=font)
            n += 1

    else:

        x = 259 - game_name_width/2
        y = 120 - game_name_height/2
        draw.text((x, y), game_name, fill=1, font=font)

    banner.save(banner_path, 'JPEG')

## First version, no longer in use:
#def goglib_recreate_banner(game_name, icon_path, banner_path):
#
#    icon = Image.open(icon_path + game_name + '.jpg')
#    icon = icon.resize((150, 150), PIL.Image.ANTIALIAS)
#
#    banner = Image.open(banner_path + '/' + game_name + '.jpg')
#    offset = ((banner.size[0] - 150)/2, (banner.size[1] - 150)/2)
#    banner.paste(icon, offset)
#    banner.save(banner_path + '/' + game_name + '.jpg')
