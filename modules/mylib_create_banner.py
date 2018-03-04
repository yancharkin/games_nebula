import os, sys
from PIL import Image, ImageDraw, ImageFont

def mylib_create_banner(game_name):

    nebula_dir = sys.path[0]
    data_dir = os.getenv('HOME') + '/.games_nebula'

    banners_dir = data_dir + '/images/mylib/'
    banner_path = banners_dir + game_name + '.jpg'

    if not os.path.exists(banners_dir):
        os.makedirs(banners_dir)

    script_path_0 = data_dir + '/scripts/mylib/' + game_name + '/setup'
    script_path_1 = nebula_dir + '/scripts/mylib/' + game_name + '/setup'

    if os.path.exists(script_path_0):
        mylib_setup_script_path = script_path_0
    else:
        mylib_setup_script_path = script_path_1

    script_file = open(mylib_setup_script_path, 'r')
    file_content = script_file.readlines()
    raw_game_title = file_content[-1].replace('#', '').replace('\n', '')

    if sys.version_info[0] == 2:
        game_title = raw_game_title.decode('utf-8')
    elif sys.version_info[0] == 3:
        game_title = raw_game_title

    script_file.close()

    banner = Image.new('1', (518, 240), 0)
    draw = ImageDraw.Draw(banner)
    font = ImageFont.truetype(nebula_dir + '/fonts/DejaVuSans.ttf', 24)

    game_title_width = font.getsize(game_title)[0]
    game_title_height = font.getsize(game_title)[1]

    if game_title_width > 518:

        game_title_list = []
        for i in range(0, len(game_title), 28):
            game_title_list.append(game_title[i:i+28])

        all_lines_height = len(game_title_list) * game_title_height
        full_title_y = 120 - all_lines_height/2

        n = 0
        for line in game_title_list:
            line_width = font.getsize(line)[0]
            x = 259 - line_width/2
            y = full_title_y + (game_title_height * n)
            draw.text((x, y), line, fill=1, font=font)
            n += 1

    else:

        x = 259 - game_title_width/2
        y = 120 - game_title_height/2
        draw.text((x, y), game_title, fill=1, font=font)

    banner.save(banner_path, 'JPEG')
