from database import *
import datetime
import shutil
import codecs
import time
import os

HALL = ['Синий', 'Зеленый', 'Желтый', 'Красный', 'Оранжевый'] # if hall in HALL
SIZE = {'Синий' : (10, 10), 'Оранжевый': (12, 15), 'Красный': (10, 15), 'Зеленый': (15, 20), 'Желтый': (8,8)} # SIZE['Синий'][1] 
TIME = {'Синий':     ('11.00', '14.00', '17.00', '20.00', '23.00'),
		'Зеленый':   ('10.05', '13.05', '16.05', '19.05', '22.05'),
		'Желтый':    ('11.35', '14.35', '17.35', '20.35', '23.35'),
		'Красный':   ('10.20', '13.20', '16.20', '19.20', '22.20'),
		'Оранжевый': ('09.00', '12.00', '15.00', '18.00', '21.00')} #TIME['Синий'][0]


# Цена сеанса
def price_list(date1, time1) -> str:
	date_m_f = date1.isoweekday() >= 1 and date1.isoweekday() <= 5 
	date_s_s = date1.isoweekday() >= 6 and date1.isoweekday() <= 7
	time_9_18 = time1 >= datetime.time(9, 0) and time1 <= datetime.time(18, 0)
	time_18_ = time1 >= datetime.time(18, 0) 
	if date_m_f and time_9_18:
		return '60'
	elif date_m_f and time_18_:
		return '70'
	elif date_s_s and time_9_18:
		return '70'
	elif date_s_s and time_18_:
		return '80'


# Перезапись матриц брони
def rewriting_files(is_busy: list, who_booked: list, date1, time1, hall_title: str) -> None:
	if not hall_title in HALL:
		raise Exception('Зала не существует')

	with open(halls + hall_title + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format) + os.sep + 'is_busy.txt', 'w') as file: 
		for row in range(SIZE[hall_title][0]):
			for col in range(SIZE[hall_title][1]):
				if col + 1 != SIZE[hall_title][1]:
					file.write(str(int(is_busy[row][col])) + ' ')
				elif row + 1 != SIZE[hall_title][0]:
					file.write(str(int(is_busy[row][col])) + '\n')
				else:
					file.write(str(int(is_busy[row][col])))

	with open(halls + hall_title + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format) + os.sep + 'who_booked.txt', 'w') as file: 
		for row in range(SIZE[hall_title][0]):
			for col in range(SIZE[hall_title][1]):
				if col + 1 != SIZE[hall_title][1]:
					file.write(str(who_booked[row][col]) + ' ')
				elif row + 1 != SIZE[hall_title][0]:
					file.write(str(who_booked[row][col]) + '\n')
				else:
					file.write(str(who_booked[row][col]))


# Заполнение реляционного расписания и создание соответствующих папок
def push_session(film: str, date1, time1, hall: str):
	# if datetime.datetime.combine(date1, time1) < datetime.datetime.now():
	# 	raise Exception(f'Сори, дата {date1.strftime(date_format)} время {time1.strftime(time_format)} прошли') 

	if not is_film_exist(film):
		raise Exception(f'Сори, фильма "{film}" в БД нет')

	if not time1.strftime(time_format) in TIME[hall]:
		raise Exception(f'В {hall} зал нельзя назначить время {time1.strftime(time_format)}')

	if is_session_exist(lambda x: x == film, lambda x: x == date1, lambda x: x == time1, lambda x: x == hall) != []:
		raise Exception('Такой сеанс уже вписан в расписание')

	if not hall in HALL:
		raise Exception('Зала не существует')

	temp = is_session_exist(lambda x: x == film, lambda x: x == date1, lambda x: x == time1)
	if temp != []:
		raise Exception(f'Фильм {film} на {date1.strftime(date_format)} в {time1.strftime(time_format)} уже показывается в зале {temp[0][-1]}, Вы не можете в это же время вписать его в зал {hall}')

	with open(path + 'SCHEDULE.txt', 'a') as file:
		file.write(f'{film};{date1.strftime(date_format)};{time1.strftime(time_format)};{hall}\n')

	if not os.path.exists(halls + os.sep + hall + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format)):
		os.makedirs(halls + os.sep + hall + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format))
		rewriting_files([[0] * SIZE[hall][1]] * SIZE[hall][0], [['str'] * SIZE[hall][1]] * SIZE[hall][0], date1, time1, hall)


# Очистить неактуальные сеансы
def clean_schedule() -> None:
	data_today = is_session_exist(date1=lambda x: x == datetime.datetime.now().date(), time1=lambda x: x >= datetime.datetime.now().time())
	data_next = is_session_exist(date1=lambda x: x > datetime.datetime.now().date())
	with open(path + 'SCHEDULE.txt', 'w') as file:
		for session in data_today:
			push_session(session[0], session[1], session[2], session[3])
		for session in data_next:
			push_session(session[0], session[1], session[2], session[3])


# Очистить папки неактуального расписания после месяца хранения
def clean_halls() -> None:
	# with open(path + 'SCHEDULE.txt', 'w') as file:
	# 	pass

	for hall in HALL:
		for day_directory in os.listdir(halls + hall):
			if datetime.datetime.strptime(day_directory, date_format).date() < datetime.datetime.now().date() - datetime.timedelta(days=140): 
				shutil.rmtree(halls + hall + os.sep + day_directory)


# Очистить неактуальное расписание и папки неактуального расписания после месяца хранения
def full_clean_schedule():
	clean_schedule()
	clean_halls()


# Очистить реляционное расписание
def delete_schedule() -> None:
	with open(path + 'SCHEDULE.txt', 'w') as file:
		pass

	for hall in HALL:
		for directory in os.listdir(halls + hall):
			shutil.rmtree(halls + hall + os.sep + directory)


# Быстрое заполнение расписаниея
def write_schedule(date1, films: str) -> None: 
	for i in range(len(HALL)):
		for j in range(len(TIME['Синий'])):
			push_session(films[i], date1, datetime.datetime.strptime(TIME[HALL[i]][j], time_format).time(), HALL[i])



# SQL-функция местного разлива, работа с реляционным расписанием
def is_session_exist(film=lambda x: True, date1=lambda x: True, time1=lambda x: True, hall=lambda x: True) -> list:
	with open(path + 'SCHEDULE.txt', 'rt') as file:
		schedule = file.read().split('\n')
		condition = [film, date1, time1, hall]
		sample = []

		for line in schedule:
			if line != '':
				line = line.split(';')
				line[1] = datetime.datetime.strptime(line[1], date_format).date()
				line[2] = datetime.datetime.strptime(line[2], time_format).time()

				if all(condition[i](line[i]) for i in range(len(condition))):
					sample.append(line)
		return sample


# Фильтр кортежей расписания с учетом установленного(ых) параметра(ов)
def filter(Film, Date, Time, order_by=None, rev=False):
	if Film == '':
		lam_film = lambda x: True
	else:
		lam_film = lambda x: x == Film
	if Date == '':
		lam_date = lambda x: True
	else:
		lam_date = lambda x: x == datetime.datetime.strptime(Date, date_format).date() 
	if Time == '':
		lam_time = lambda x: True
	else:
		lam_time = lambda x: x == datetime.datetime.strptime(Time, time_format).time()

	result = is_session_exist(film=lam_film, date1=lam_date, time1=lam_time)
	res=[]
	for row in result:
		if datetime.datetime.combine(row[1], row[2]) >= datetime.datetime.now():
			res.append(row)
	if order_by:
		res.sort(key=order_by, reverse=rev)
	return res
	

#Фильмы в ближайшеев ремя
def novelty() -> list:
	DateTime = []
	data_today = is_session_exist(date1=lambda x: x == datetime.datetime.now().date(), time1=lambda x: x >= datetime.datetime.now().time())
	data_next = is_session_exist(date1=lambda x: x > datetime.datetime.now().date())
	for session in data_today:
		DateTime.append(session[0])
	for session in data_next:
		DateTime.append(session[0])

	return list(set(DateTime))
# print(novelty())#FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


# SQL-функция местного разлива, работа с реляционной историей
def is_history_exist(username: str, date1=lambda x: True, time1=lambda x: True, row=lambda x: True, col=lambda x: True, film=lambda x: True) -> list:
	with open(users + username + os.sep + 'history.txt', 'rt') as file:
		history = file.read().split('\n')
		condition = [date1, time1, row, col, film]
		sample = []

		for line in history:
			if line != '':
				line = line.split(';')
				line[0] = datetime.datetime.strptime(line[0], date_format).date()
				line[1] = datetime.datetime.strptime(line[1], time_format).time()

				if all(condition[i](line[i]) for i in range(len(condition))):
					sample.append(line)
		return sample


# Актуальная история
def history_actually(username: str) -> list:
	DateTime =[]
	data_today = is_history_exist(username, date1=lambda x: x == datetime.datetime.now().date(), time1=lambda x: x >= datetime.datetime.now().time())
	data_next = is_history_exist(username, date1=lambda x: x > datetime.datetime.now().date())

	for session in data_today:
		DateTime.append([session[0].strftime(date_format), session[1].strftime(time_format), str(session[2]), str(session[3]), session[4]])
	for session in data_next:
		DateTime.append([session[0].strftime(date_format), session[1].strftime(time_format), str(session[2]), str(session[3]), session[4]])

	return DateTime


# Проверка на существование фильма
def is_hall_exist(hall_title: str) -> bool:
	return os.path.exists(halls + hall_title)


# Проверка на пустоту зала
def is_hall_empty(date1, time1, hall_title:str) -> bool:
	return all(not item for row in get_is_busy(date1, time1, hall_title) for item in row)


# Проверка на существование даты
def is_date_exist(date1, hall_title:str) -> bool:
	return os.path.exists(halls + hall_title + os.sep + date1.strftime(date_format))


# Проверка на существование времени
def is_time_exist(date1, time1, hall_title:str) -> bool:
	return os.path.exists(halls + hall_title + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format))


# Проверка, занято ли место
def is_site_busy(is_busy: bool, row: int, col: int) -> bool:
	return is_busy[row][col] #def out_of_range


# Проверка, кем занято место
def is_site_busy_whom(who_booked: str, row: int, col: int) -> str:
	return who_booked[row][col] #def out_of_range


# Проверка, кем занято место
def is_site_busy_whom2(date1, time1, hall_title: str, row: int, col: int) -> str:
	List = get_who_booked(date1, time1, hall_title)
	return List[row][col]


# Проверка, занят ли ряд
def is_row_busy(is_busy: bool, row: int) -> bool:
	row_busy =[]
	for col in range(len(is_busy[0])):
		row_busy.append(is_busy[row][col])

	return row_busy.count(True) == len(is_busy[0])


# Занят полностью зал
def is_hall_filled(is_busy: bool) -> bool:
	return sum(row.count(True) for row in is_busy) == len(is_busy)*len(is_busy[0])


# Exception - существует ли зал, дата, время
def Exception_is_hall_date_time_exist(date1, time1, hall_title: str)-> None:
	if not is_hall_exist(hall_title):
		raise Exception(f'{hall_title} - Зала не существует')
	if not is_date_exist(date1, hall_title):
		raise Exception(f'{date1.strftime(date_format)} - Даты не существует')
	if not is_time_exist(date1, time1, hall_title):
		raise Exception(f'{time1.strftime(time_format)} - Времени не существует')


# Опустошить зал во время какого-то сеанса
def delete_filling_hall(date1, time1, hall_title: str) -> None:
	Exception_is_hall_date_time_exist(date1, time1, hall_title)
	is_busy, who_booked = get_is_busy(date1, time1, hall_title), get_who_booked(date1, time1, hall_title)

	for row in range(sizes[hall_title][0]):
		for col in range(sizes[hall_title][1]):
			is_busy[row][col] = True
			who_booked[row][col] = 'str'

	rewriting_files(is_busy, who_booked, date1, time1, hall_title)


#Бронь несуществующего места
def out_of_range(row: int, col: int, hall: str) -> bool:
	return row < 0 or row >= SIZE[hall][0] or col < 0 or col >= SIZE[hall][1]


# Забронировать место на сеанс в зале
def book(date1, time1, row: int, col: int, username: str, hall_title: str) -> None:
	Exception_is_hall_date_time_exist(date1, time1, hall_title)
	row -= 1
	col -= 1
	
	is_busy, who_booked = get_is_busy(date1, time1, hall_title), get_who_booked(date1, time1, hall_title)

	if out_of_range(row, col, hall_title):
		raise Exception(f'В зале {hall_title} не существует такого места') 

	if is_busy[row][col]: 
		raise Exception(f'Ряд {row + 1} место {col + 1} в {hall_title} зале на сеанс на {date1.strftime(date_format)} в {time1.strftime(time_format)} - заняты')
	else:
		is_busy[row][col] = True 
		who_booked[row][col] = username

	rewriting_files(is_busy, who_booked, date1, time1, hall_title)


# Отмена брони места на сеанс в зале
def unbook(date1, time1, row: int, col: int, username: str, hall_title: str) -> None:
	Exception_is_hall_date_time_exist(date1, time1, hall_title)
	row -= 1
	col -= 1
	
	is_busy, who_booked = get_is_busy(date1, time1, hall_title), get_who_booked(date1, time1, hall_title)

	if out_of_range(row, col, hall_title):
		raise Exception(f'В зале {hall_title} не существует такого места')

	if not is_busy[row][col]: 
		raise Exception(f'Ряд {row} место {col} в {hall_title} зале на сеанс на {date1.strftime(date_format)} в {time1.strftime(time_format)} - не заняты') 
		raise Exception(f'Ряд {row} место {col} в {hall_title} зале на сеанс на {date1.strftime(date_format)} в {time1.strftime(time_format)} - заняты не вами') 
	else:
		is_busy[row][col] = False 
		who_booked[row][col] = 'str'

	rewriting_files(is_busy, who_booked, date1, time1, hall_title)


# Вернуть заполненность зала на сеанс
def get_is_busy(date1, time1, hall_title: str) -> None:
	Exception_is_hall_date_time_exist(date1, time1, hall_title)

	with open(halls + hall_title + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format) + os.sep + 'is_busy.txt', 'rt') as file:
		return [list(map(bool, map(int, row.split()))) for row in file.readlines()]


# Вернуть заполненность зала на сеанс пользователями
def get_who_booked(date1, time1, hall_title: str) -> None:
	Exception_is_hall_date_time_exist(date1, time1, hall_title)

	with open(halls + hall_title + os.sep + date1.strftime(date_format) + os.sep + time1.strftime(time_format) + os.sep + 'who_booked.txt', 'rt') as file:
		return [list(map(str, row.split())) for row in file.readlines()]


#Основная функция (mood = True - забронировать, mood = False - отменить бронь)
def reservation(film: str, date1, time1, row: int, col: int, username: str, mood: bool) -> None:
	if not is_film_exist(film):
		raise Exception(f'Сори, фильма "{film}" в БД нет')

	if not is_user_exist(username):
		raise Exception(f'Сори, пользователя {username} в БД нет')

	session = is_session_exist(lambda x: x == film, lambda x: x == date1, lambda x: x == time1) #sql

	hall_title = session[0][-1] 
	if mood:
		book(date1, time1, row, col, username, hall_title)
		add_user_history(username, date1, time1, hall_title, row, col, film)
	else:
		unbook(date1, time1, row, col, username, hall_title)
		delete_user_history(username, date1, time1, hall_title, row, col, film)


# Вернуть отсортированное по параметру расписание
def get():
	table = is_session_exist()
	table.sort(key=lambda x: x[1])
	for session in table:
		print(session)


# search = is_session_exist(time1=lambda x: x > datetime.time(15) and x < datetime.time(18))
# search.sort(key=lambda x: x[2])
# for session in search:
# 	print(session)
#clean_schedule()
# push_session('Виноваты звезды (2014)', datetime.date(2020, 4, 27), datetime.time(20, 35), 'Желтый')



'''
'1917 (2019)' 1
'Бегущий в лабиринте (2014)' 2
'Богемская рапсодия (2018)' 3
'Виноваты звезды (2014)' 4
'Голодные игры (2012)' 5
'Джокер (2019)' 6
'До встречи с тобой (2016)' 7
'Доктор Сон (2019)' 8
'Звезда родилась (2018)' 9
'Зеленая книга (2018)' 10
'Книга Генри (2017)' 11
'Красавица и чудовище (2017)' 12
'Маленькие женщины (2019)' 13
'Мег - монстр глубин (2018)' 14
'Мстители (2012)' 15
'Оно (2017)' 16
'Орудия смерти (2013)' 17
'Паразиты (2019)' 18
'Пассажиры (2016)' 19
'Полночное солнце (2018)' 20
'Форма воды (2017)' 21

'Синий'
'Красный'
'Желтый'
'Зеленый'
'Красный'

films1 = ['1917 (2019)', 'Бегущий в лабиринте (2014)', 'Богемская рапсодия (2018)', 'Виноваты звезды (2014)', 'Голодные игры (2012)']
write_schedule(datetime.date(2020, 5, 20), films1)
# write_schedule(datetime.date(2020, 3, 19), films1)

films1 = ['1917 (2019)', 'Бегущий в лабиринте (2014)', 'Богемская рапсодия (2018)', 'Виноваты звезды (2014)', 'Джокер (2019)']
write_schedule(datetime.date(2020, 5, 21), films1)
# write_schedule(datetime.date(2020, 3, 21), films1)

films1 = ['1917 (2019)', 'Бегущий в лабиринте (2014)', 'Богемская рапсодия (2018)', 'До встречи с тобой (2016)', 'Джокер (2019)']
write_schedule(datetime.date(2020, 5, 22), films1)
# write_schedule(datetime.date(2020, 3, 23), films1)

films1 = ['1917 (2019)', 'Бегущий в лабиринте (2014)', 'Доктор Сон (2019)', 'До встречи с тобой (2016)', 'Джокер (2019)']
write_schedule(datetime.date(2020, 5, 23), films1)
# write_schedule(datetime.date(2020, 3, 25), films1)

films1 = ['1917 (2019)', 'Звезда родилась (2018)', 'Доктор Сон (2019)', 'До встречи с тобой (2016)', 'Джокер (2019)']
write_schedule(datetime.date(2020, 5, 24), films1)
# write_schedule(datetime.date(2020, 3, 27), films1)

films1 = ['Зеленая книга (2018)', 'Звезда родилась (2018)', 'Доктор Сон (2019)', 'До встречи с тобой (2016)', 'Джокер (2019)']
write_schedule(datetime.date(2020, 5, 25), films1)
# write_schedule(datetime.date(2020, 3, 29), films1)

films1 = ['Зеленая книга (2018)', 'Звезда родилась (2018)', 'Доктор Сон (2019)', 'До встречи с тобой (2016)', 'Книга Генри (2017)']
write_schedule(datetime.date(2020, 5, 26), films1)
# write_schedule(datetime.date(2020, 3, 31), films1)

films1 = ['Зеленая книга (2018)', 'Звезда родилась (2018)', 'Доктор Сон (2019)', 'Красавица и чудовище (2017)', 'Книга Генри (2017)']
write_schedule(datetime.date(2020, 5, 27), films1)
# write_schedule(datetime.date(2020, 4, 2), films1)

films1 = ['Зеленая книга (2018)', 'Звезда родилась (2018)', 'Маленькие женщины (2019)', 'Красавица и чудовище (2017)', 'Книга Генри (2017)']
write_schedule(datetime.date(2020, 5, 28), films1)
# write_schedule(datetime.date(2020, 4, 4), films1)

films1 = ['Зеленая книга (2018)', 'Мег - монстр глубин (2018)', 'Маленькие женщины (2019)', 'Красавица и чудовище (2017)', 'Книга Генри (2017)']
write_schedule(datetime.date(2020, 5, 29), films1)
# write_schedule(datetime.date(2020, 4, 6), films1)

films1 = ['Мстители (2012)', 'Мег - монстр глубин (2018)', 'Маленькие женщины (2019)', 'Красавица и чудовище (2017)', 'Книга Генри (2017)']
write_schedule(datetime.date(2020, 5, 30), films1)
# write_schedule(datetime.date(2020, 4, 8), films1)

films1 = ['Мстители (2012)', 'Мег - монстр глубин (2018)', 'Маленькие женщины (2019)', 'Красавица и чудовище (2017)', 'Оно (2017)']
write_schedule(datetime.date(2020, 5, 31), films1)
# write_schedule(datetime.date(2020, 4, 10), films1)

films1 = ['Мстители (2012)', 'Мег - монстр глубин (2018)', 'Маленькие женщины (2019)', 'Орудия смерти (2013)', 'Оно (2017)']
write_schedule(datetime.date(2020, 6, 1), films1)
# write_schedule(datetime.date(2020, 4, 12), films1)

films1 = ['Мстители (2012)', 'Мег - монстр глубин (2018)', 'Паразиты (2019)', 'Орудия смерти (2013)', 'Оно (2017)']
write_schedule(datetime.date(2020, 6, 2), films1)
# write_schedule(datetime.date(2020, 4, 14), films1)

films1 = ['Мстители (2012)', 'Пассажиры (2016)', 'Паразиты (2019)', 'Орудия смерти (2013)', 'Оно (2017)']
write_schedule(datetime.date(2020, 6, 3), films1)
# write_schedule(datetime.date(2020, 4, 16), films1)

films1 = ['Полночное солнце (2018)', 'Пассажиры (2016)', 'Паразиты (2019)', 'Орудия смерти (2013)', 'Оно (2017)']
write_schedule(datetime.date(2020, 6, 4), films1)
# write_schedule(datetime.date(2020, 4, 18), films1)

films1 = ['Полночное солнце (2018)', 'Пассажиры (2016)', 'Паразиты (2019)', 'Орудия смерти (2013)', 'Форма воды (2017)']
write_schedule(datetime.date(2020, 6, 5), films1)
# write_schedule(datetime.date(2020, 4, 20), films1)

films1 = ['Полночное солнце (2018)', 'Пассажиры (2016)', 'Паразиты (2019)', 'Голодные игры (2012)', 'Форма воды (2017)']
write_schedule(datetime.date(2020, 6, 6), films1)
# write_schedule(datetime.date(2020, 4, 22), films1)

films1 = ['Полночное солнце (2018)', 'Пассажиры (2016)', 'Виноваты звезды (2014)', 'Голодные игры (2012)', 'Форма воды (2017)']
write_schedule(datetime.date(2020, 6, 7), films1)
# write_schedule(datetime.date(2020, 4, 24), films1)

films1 = ['Полночное солнце (2018)', 'Богемская рапсодия (2018)', 'Виноваты звезды (2014)', 'Голодные игры (2012)', 'Форма воды (2017)']
write_schedule(datetime.date(2020, 6, 8), films1)
# write_schedule(datetime.date(2020, 4, 26), films1)

films1 = ['Бегущий в лабиринте (2014)', 'Богемская рапсодия (2018)', 'Виноваты звезды (2014)', 'Голодные игры (2012)', 'Форма воды (2017)']
write_schedule(datetime.date(2020, 6, 9), films1)
# write_schedule(datetime.date(2020, 4, 28), films1)

'''


# who_booked = [['str']*8] *8
# #False,False,False,False,False,False,False,False
# #True,True,True,True,True,True,True,True
# is_busy = [[False,False,False,False,False,False,False,False],
# [False,False,False,False,False,False,False,False],
# [False,False,False,False,False,False,False,False],
# [False,False,False,False,False,False,False,False],
# [True,True,True,True,True,True,True,True],
# [True,True,True,True,True,True,True,True],
# [True,True,True,True,True,True,True,True],
# [True,True,True,True,True,True,True,True]]

# time1=datetime.time(23,35)
# hall1='Желтый'

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 30), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 1), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 4), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 5), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 6), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 7), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 8), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 11), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 12), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 13), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 14), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 15), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 18), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 19), time1, hall1)




# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 2), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 3), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 9), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 10), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 16), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 5, 17), time1, hall1)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 15), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 16), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 17), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 20), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 21), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 22), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 23), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 24), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 27), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 28), time1, hall1)



# rewriting_files(is_busy, who_booked, datetime.date(2020, 3, 21), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 3, 22), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 3, 28), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 3, 29), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 4), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 5), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 11), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 12), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 18), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 19), time1, hall1)

# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 25), time1, hall1)
# rewriting_files(is_busy, who_booked, datetime.date(2020, 4, 26), time1, hall1)



#python C:\\Users\\Света\\Desktop\\Bot\\schedule.py