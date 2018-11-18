import PIL
from PIL import Image

def image_to_grayscale(input_path, output_path):
    """Convert image to grayscale"""
    img = Image.open(input_path)
    img = img.convert('L')
    img.save(output_path)

if __name__ == '__main__':
    import sys
    image_to_grayscale(sys.argv[1], sys.argv[2])
