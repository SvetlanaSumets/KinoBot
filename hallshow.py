from PIL import Image, ImageDraw, ImageFont
from schedule import HALL, SIZE, get_is_busy, is_site_busy, out_of_range, is_session_exist
from database import users
import datetime
import os

free_color = '#0082ff'
busy_color = '#dec8ff' 
image_color = '#ffffff'
color_choose = '#ff9370' 

text_free_color = '#595959'
text_color_choose = 'white'

place_height = 40
place_width = 40
padding_horizontal = 7
padding_vertical = 18

row_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', int(place_height * 0.66))
borders = {'top' : 80, 'right' : 90, 'left' : 110, 'bottom' : 40}


# Вернуть загруженность зала
def return_hallshow(Date, Time, Film: str, username: str, row: int = None, col: int = None):
	session = is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	hall = session[0][-1] 
	draw(Date, Time, hall, username, row, col)
	return users + username + os.sep + 'current' + os.sep + 'hallshow.png'


# Отрисовка зала на сеанс + актуальной брони 
def draw(session_day, session_time, hall_title: str, username: str, row: int = None, col: int = None) -> None:
	if not hall_title in HALL:
		raise Exception('Зала не существует')
	
	height, width = SIZE[hall_title]

	im_height = borders['top'] + height * place_height + height * (padding_vertical - 1) + borders['bottom']
	im_width = borders['left'] + width * place_width + width * (padding_horizontal - 1) + borders['right']
	
	image = Image.new('RGB', (im_width, im_height), image_color)
	drawer = ImageDraw.Draw(image)

	BUSY = get_is_busy(session_day, session_time, hall_title)

	color =[]
	text =[]
	drawer.line([(borders['left'] // 2, borders['top'] - place_height), (im_width - borders['right'] // 2, borders['top'] - place_height)], fill='grey', width=10)
	for i in range(height):
		for j in range(width):
			x = borders['left'] + j * (place_width + padding_horizontal) + ((-1) ** (i + 1)) * place_width // 5
			y = borders['top'] + i * (place_height + padding_vertical)

			if BUSY[i][j]:
				drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=busy_color)

			elif row != None and col != None:
				for ii in range(len(row)):
					if row[ii]-1 == i and col[ii]-1 == j:
						drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=color_choose)
						drawer.text((x + 5, y), str(j + 1), font=row_font, fill=text_color_choose)
						color.append([i, j])
				if not [i, j] in color:
					drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=free_color)
					drawer.text((x + 5, y), str(j + 1), font=row_font, fill=text_free_color)
					
			elif row != None and col == None:
				if row[0]-1 == i and not BUSY[i][j]:
					drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=color_choose)
					drawer.text((x + 5, y), str(j + 1), font=row_font, fill=text_color_choose)
				else:
					drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=free_color)
					drawer.text((x + 5, y), str(j + 1), font=row_font, fill=text_free_color)
			
			else:
				drawer.rectangle([(x, y), (x + place_width, y + place_height)], fill=free_color)
				drawer.text((x + 5, y), str(j + 1), font=row_font, fill=text_free_color)
			
			if row != None:
				for ii in range(len(row)):
					if i == row[ii]-1:
						drawer.text((5, y), str(i + 1), font=row_font, fill=color_choose)
						text.append(i)
				if not i in text:
					drawer.text((5, y), str(i + 1), font=row_font, fill='grey')

			else:
				drawer.text((5, y), str(i + 1), font=row_font, fill='grey')

	image.save(users + username + os.sep + 'current' + os.sep + 'hallshow.png')
	# image.show()

# draw(datetime.date(2020, 4, 23), datetime.time(14, 0), 'Синий', 'Света', [2,5,6], [4,6,7])
#python C:\\Users\\Света\\Desktop\\Bot\\hallshow.py
