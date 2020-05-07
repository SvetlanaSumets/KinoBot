from PIL import Image, ImageDraw, ImageFont
from database import users, date_format, time_format, full_format, photo
import datetime
import os

image_color = '#fff9e8'
text_color = '#595959'
place_height = 40
place_width = 40

row_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', int(place_height * 0.66))
col_font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', int(place_height * 0.90))
borders = {'top' : 80, 'right' : 90, 'left' : 110, 'bottom' : 40}

# Вернуть билет
def return_ticket(Date, Time, Film: str, Hall:str, Price: str, username: str, row: int, col: int):
	draw(Date, Time, Film, Hall, Price, username, row, col)
	return users + username + os.sep + 'current' + os.sep + 'ticket.png'


# Нарисовать билет
def draw(Date, Time, Film: str, Hall:str, Price: str, username: str, row: int, col: int) -> None:

	im_height = 670 + 170 * len(row)
	im_width = 1000
	
	image = Image.new('RGB', (im_width, im_height), image_color)
	drawer = ImageDraw.Draw(image)

	photoo = Image.open(photo(Film))
	width, height = photoo.size
	new_width  = 250
	new_height = int(new_width * height / width)
	photoo = photoo.resize((new_width, new_height), Image.ANTIALIAS)

	drawer.line([(borders['left']//2, borders['top'] - place_height), (im_width - borders['right']//2, borders['top'] - place_height)], fill='#980000', width=60)
	drawer.line([(borders['left']//2, borders['top'] - place_height + 20), (im_width - borders['right']//2, borders['top'] - place_height + 20)], fill='#fff9e8', width=10)
	
	image.paste(photoo, (55, 80))
	drawer.text((borders['left']//2 + 270, 110), f'Фильм: {Film}', font=col_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 160), f'Дата: {Date.strftime(date_format)}', font=row_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 200), f'Время: {Time.strftime(time_format)}', font=row_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 240), f'Зал: {Hall}', font=row_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 300), f'Билет продан: {datetime.datetime.now().strftime(full_format)}', font=row_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 340), f'Телеграм-ботом @nure_kino_bot', font=row_font, fill=text_color)
	drawer.text((borders['left']//2 + 270, 380), f'Пользователю {username} ', font=row_font, fill=text_color)
	
	tab = 0
	for i in range(len(row)):
		drawer.text((borders['left']//2 + 10, 475 + i* 170), f'Билет {i+1} из {len(row)}', font=row_font, fill=text_color)
		drawer.text((borders['left']//2 + 650, 475 + i* 170), f'Электронный билет', font=row_font, fill=text_color)
		drawer.line([(borders['left']//2, borders['top'] - place_height + 480+ i* 170), (im_width - borders['right']//2, borders['top'] - place_height + 480+ i* 170)], fill='#595959', width= 5)
		
		drawer.text((borders['left']//2 + 30, 550 + i* 170), f'Ряд: {row[i]}', font=row_font, fill=text_color)
		drawer.text((borders['left']//2 + 30, 590 + i* 170), f'Место: {col[i]}', font=row_font, fill=text_color)

		drawer.rectangle([(borders['left']//2 + 195, 550 + i* 170 - 5), (borders['left']//2 + 200 + 305, 550 + i* 170 + 80)], fill='#d0c8ff')
		drawer.rectangle([(borders['left']//2 + 200, 550 + i* 170), (borders['left']//2 + 200 + 300, 550 + i* 170 + 75)], fill='#e3e0ff')
		drawer.text((borders['left']//2 + 200 + 30, 550 + i* 170 + 25), 'Требуется к оплате', font=row_font, fill=text_color)
		drawer.text((borders['left']//2 + 200 + 360, 570 + i* 170), f'Цена: {Price} грн', font=row_font, fill=text_color)
		tab = 590 + i* 170

	drawer.line([(borders['left']//2, tab + 120), (im_width - borders['right']//2, tab + 120)], fill='#595959', width= 5)
	drawer.text((borders['left']//2 + 550, tab + 130), f'Сумма к оплате: {str(len(row) * int(Price))} грн', font=row_font, fill=text_color)

	drawer.line([(borders['left']//2, borders['top'] - place_height + tab + 170), (im_width - borders['right']//2, borders['top'] - place_height + tab + 170)], fill='#980000', width=60)
	drawer.line([(borders['left']//2, borders['top'] - place_height + tab + 150), (im_width - borders['right']//2, borders['top'] - place_height + tab + 150)], fill='#fff9e8', width=10)
	

	image.save(users + username + os.sep + 'current' + os.sep + 'ticket.png')
	# image.show()

# draw(datetime.date(2020, 4, 23), datetime.time(11, 0), '1917 (2019)', 'Синий', '70', '@Svetlana_Sumets', [5,5], [6,7])
#python C:\\Users\\Света\\Desktop\\Bot\\ticket.py
