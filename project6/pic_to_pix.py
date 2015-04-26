import PIL.Image as img #pip3 install pillow
from data import *
import sys

RED = 0
GREEN = 1
BLUE = 2

def pic_to_pixel(picture,color):
	pic = img.open(picture)
	matrix = []
	width,height = pic.size
	for i in range(width):
		row = []
		for j in range(height):
			pixel = pic.getpixel((i,j))
			if pixel[color] == 0:
				row.append(0)
			else:
				row.append(pixel[color]/sum(pixel))
		matrix.append(row)

	write_instance_to_file("p_{}.img".format(picture), matrix)

def main():
	color_map = {'RED':RED, 'GREEN':GREEN, 'BLUE':BLUE}

	if len(sys.argv) != 3 or sys.argv[2] not in color_map:
		print('Usage:', sys.argv[0], '<input file> [RED|GREEN|BLUE]')
		return

	pic_to_pixel(sys.argv[1], color_map[sys.argv[2]])

if __name__ == '__main__':
	main()
