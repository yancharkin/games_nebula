import os
import PIL
from PIL import Image

try:
    from modules import goglib_recreate_banner
except:
    pass

def image_to_grayscale(input_path, output_path):
    """Convert image to grayscale"""
    def convert():
        img = Image.open(input_path)
        img = img.convert('L')
        img.save(output_path)
    if os.path.exists(input_path):
        convert()
    else:
        game_name = os.path.basename(input_path).split('.jpg')[0]
        goglib_recreate_banner.goglib_recreate_banner(game_name, input_path)
        convert()

if __name__ == '__main__':
    import sys
    image_to_grayscale(sys.argv[1], sys.argv[2])
