import datetime
from statistics import mean
import random
import shutil
import codecs
import time
import os

location = 'C:\\Users\\Света\\Desktop\\Bot' + os.sep


# Путь к базе данных
path = location + 'DATABASE' + os.sep
films = path + 'Films' + os.sep
users = path + 'Users' + os.sep
halls = path + 'Halls' + os.sep

time_format = '%H.%M'
date_format = '%Y.%m.%d'
full_format = date_format + ' ' + time_format


# Проверка на существование фильма
def is_film_exist(film_title: str) -> bool:
	return os.path.exists(films + film_title)


# Добавление фильма в базу данных
def add_film(film_title: str, country: str, producer: list, genre: list, time: str, actor: list, site: str) -> None:
	if is_film_exist(film_title):
		raise Exception('Фильм уже зарегестрирован')
		
	os.mkdir(films + film_title)
	with open(films + film_title + os.sep + 'country.txt', 'w') as file:
		file.write(country)
	with open(films + film_title + os.sep + 'producers.txt', 'w') as file:
		file.write('\n'.join(producer))
	with open(films + film_title + os.sep + 'genres.txt', 'w') as file:
		file.write('\n'.join(genre))
	with open(films + film_title + os.sep + 'time.txt', 'w') as file:
		file.write(time)
	with open(films + film_title + os.sep + 'actors.txt', 'w') as file:
		file.write('\n'.join(actor))
	with open(films + film_title + os.sep + 'site.txt', 'w') as file:
		file.write(site)
	with open(films + film_title + os.sep + 'rating.txt', 'w') as file:
		file.write('0')

# Считывание года фильма
def year(film_title: str) -> str:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	return film_title[-5:-1]


# Считывание страны фильма
def country(film_title: str) -> str:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'country.txt', 'rt') as file:
		return file.read()


# Считывание режисера(ов) фильма
def producers(film_title: str) -> list:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'producers.txt', 'rt') as file:
		return file.read().split('\n')


# Считывание жанра(ов) фильма
def genge(film_title: str) -> list:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'genres.txt', 'rt') as file:
		return file.read().split('\n')


# Считывание длительности фильма
def time(film_title: str) -> str:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'time.txt', 'rt') as file:
		return file.read()


# Считывание актера(ов) фильма
def actors(film_title: str) -> list:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'actors.txt', 'rt') as file:
		return file.read().split('\n')


# Считывание года фильма
def site(film_title: str) -> str:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	
	with open(films + film_title + os.sep + 'site.txt', 'rt') as file:
		return file.read()


# Считывание обложки фильма
def photo(film_title: str) -> None:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')

	return films + film_title + os.sep + f'{film_title}.jpg'
	#os.startfile(films + film_title + os.sep + f'{film_title}.jpg')


# Запись рейтинга фильма
def update_rating(mark: str, film_title: str) -> None:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')

	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')
	if int(mark) < 0 or int(mark) > 10:
		raise Exception('Невозможно установить такую оценку фильма')

	with open(films + film_title + os.sep + 'rating.txt', 'a') as file:
		file.write(f';{mark}')


# Считывание рейтинга фильма
def get_rating(film_title: str) -> list:
	if not is_film_exist(film_title):
		raise Exception(f'{film_title} - Фильм не зарегестрирован')

	with open(films + film_title + os.sep + 'rating.txt', 'rt') as file:
		return list(map(int, file.read().split(';')))


# Подсчет рейтинга фильма
def AVG_rating(film_title: str) -> float:
	return round(mean(get_rating(film_title)), 2)


# Полная информация о фильме
def information_about_film(film_title: str)-> list:
	if AVG_rating(film_title) != 0.0:
		AVG = AVG_rating(film_title)
	else:
		AVG = '—'
	if producers(film_title) != '':
		producer = ', '.join(producers(film_title))
	else:
		producer = '—'
	if genge(film_title) != '':
		genges = ', '.join(genge(film_title))
	else:
		genges = '—'
	if actors(film_title) != '':
		actor = ', '.join(actors(film_title))
	else:
		actor = '—'
	if site(film_title) != '':
		www = site(film_title)
	else:
		www = '—'

	return [year(film_title), country(film_title), producer, genges, time(film_title), actor, AVG, www]




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Проверка на существование пользователя
def is_user_exist(username: str) -> bool:
	return os.path.exists(users + username)


# Добавление пользователя в базу данных
def add_user(id: int, username: str):
	if is_user_exist(username):
		raise Exception('Пользователь уже зарегестрирован')

	os.mkdir(users + username)
	with open(users + username + os.sep + 'id.txt', 'w') as file:
		file.write(str(id))
	with open(users + username + os.sep + 'history.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'activity.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'alert.txt', 'w') as file:
		pass

	os.mkdir(users + username + os.sep + 'current')
	with open(users + username + os.sep + 'current' + os.sep + 'date.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'current' + os.sep + 'time.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'current' + os.sep + 'film.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'current' + os.sep + 'row.txt', 'w') as file:
		pass
	with open(users + username + os.sep + 'current' + os.sep + 'col.txt', 'w') as file:
		pass


# Считать id
def get_user_id(username: str) -> str:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'id.txt', 'rt') as file:
		return int(file.read())


# Считать выбраннй пользователем ряд
def get_current_row(username: str) -> list:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'row.txt', 'rt') as file:
		data = file.read()
		if data == '':
			return []
		else:
			return list(map(int, map(str, data.split(';'))))


# Очистить выбранный пользователем ряд
def clean_current_row(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'row.txt', 'w') as file:
		pass


# Очистить выбранный пользователем ряд
def clean_current_last_row(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	if get_current_row(username) != []:
		List = get_current_row(username)
		del List[-1]
		with open(users + username + os.sep + 'current' + os.sep + 'row.txt', 'w') as file:
			for i in range(len(List)):
				if i + 1 != len(List):
					file.write(str(List[i])+';')
				else:
					file.write(str(List[i]))
	else:
		pass


# Установить выбранный пользователем ряд
def set_current_row(row: int, username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'row.txt', 'a') as file:
		if get_current_row(username) == []:
			file.write(row)
		else:
			file.write(f';{row}')


# Считать выбранного пользователем место
def get_current_col(username: str) -> list:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'col.txt', 'rt') as file:
		data = file.read()
		if data == '':
			return []
		else:
			return list(map(int, map(str, data.split(';'))))


# Очистить выбранное пользователем место
def clean_current_col(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'col.txt', 'w') as file:
		pass


# Очистить выбранное пользователем место
def clean_current_last_col(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	if get_current_col(username) != []:
		List = get_current_col(username)
		del List[-1]
		with open(users + username + os.sep + 'current' + os.sep + 'col.txt', 'w') as file:
			for i in range(len(List)):
				if i + 1 != len(List):
					file.write(str(List[i])+';')
				else:
					file.write(str(List[i]))
	else:
		pass


# Установить выбранное пользователем место
def set_current_col(col: int, username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'col.txt', 'a') as file:
		if get_current_col(username) == []:
			file.write(col)
		else:
			file.write(f';{col}')


# Считать выбранную пользователем дата
def get_current_date(username) -> str:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'date.txt', 'rt') as file:
		return file.read()


# Очистить выбранную пользователем дата
def clean_current_date(username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'date.txt', 'w') as file:
		file.write('')


# Установить выбранную пользователем дату
def set_current_date(Date, username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')
	with open(users + username + os.sep + 'current' + os.sep + 'date.txt', 'w') as file:
		file.write(Date)


# Считать выбранное пользователем время
def get_current_time(username) -> str:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'time.txt', 'rt') as file:
		return file.read()


# Очистить выбранное пользователем время
def clean_current_time(username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'time.txt', 'w') as file:
		file.write('')


# Установить выбранное пользователем время
def set_current_time(Time, username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')
	with open(users + username + os.sep + 'current' + os.sep + 'time.txt', 'w') as file:
		file.write(Time)


# Считать выбранный пользователем фильм
def get_current_film(username) -> str:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'film.txt', 'rt') as file:
		return file.read()


# Очистить выбранный пользователем фильм
def clean_current_film(username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'current' + os.sep + 'film.txt', 'w') as file:
		file.write('')


# Установить выбранный пользователем фильм
def set_current_film(Film, username) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')
	with open(users + username + os.sep + 'current' + os.sep + 'film.txt', 'w') as file:
		file.write(Film)


# Удаление пользователя из БД
def delete_user(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')
	shutil.rmtree(users + username)


# История пользователя
def add_user_history(username: str, date1, time1, hall:str, row: int, col:int, film:str ) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	max_history = 10
	
	with open(users + username + os.sep + 'history.txt', 'rt') as file:
		history = file.read().split('\n')

	if history == ['']:
		with open(users + username + os.sep + 'history.txt', 'w') as file:
			file.write(date1.strftime(date_format) + ';' + time1.strftime(time_format) + ';' + str(row) + ';' + str(col) + ';' + film)
	elif len(history) < max_history:
		with open(users + username + os.sep + 'history.txt', 'a') as file:
			file.write('\n' + date1.strftime(date_format) + ';' + time1.strftime(time_format) + ';' + str(row) + ';' + str(col) + ';' + film)
	else:
		with open(users + username + os.sep + 'history.txt', 'w') as file:
			file.write('\n'.join(history[1:]))
			file.write('\n' + date1.strftime(date_format) + ';' + time1.strftime(time_format) + ';' + str(row) + ';' + str(col) + ';' + film)


# Удаление строк истории пользователя
def delete_user_history(username: str, date1, time1, hall:str, row: int, col:int, film:str ) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	line = date1.strftime(date_format) + ';' + time1.strftime(time_format) + ';' + str(row) + ';' + str(col) + ';' + film
	index_row = None

	with open(users + username + os.sep + 'history.txt', 'rt') as file:
		history = file.read().split('\n')

		for row in range(len(history)):
			if history[row] == line:
				index_row = row

		if index_row == None:
			raise Exception('Такой строки истории не существует')

		del history[index_row]

	with open(users + username + os.sep + 'history.txt', 'w') as file:
		for row in range(len(history)):
			if row + 1 != len(history):
				file.write(history[row] + '\n')
			else:
				file.write(history[row])


# Вернуть историю пользователя
def history(username:str) -> list:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'history.txt', 'rt') as file:
		return file.read().split('\n')


# Вернуть дата-фильм-время из истории пользователя
def history_date_time_film(username:str) -> list:
	data = history(username)
	date_time_film = []

	for row in data:
		row = row.split(';')
		date_time_film.append([row[0], row[1], row[4]])
	return date_time_film


# Получение последнего оповещения пользователя
def get_alert(username: str):
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'alert.txt', 'tr') as file:
		return datetime.datetime.strptime(file.read(), full_format)


# Установка последнего оповещения пользователя
def set_alert(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'alert.txt', 'w') as file:
		file.write(datetime.datetime.today().strftime(full_format))


# Получение последней активности пользователя
def get_activity(username: str):
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'activity.txt', 'tr') as file:
		return datetime.datetime.strptime(file.read(), full_format)


# Установка последней активности пользователя
def set_activity(username: str) -> None:
	if not is_user_exist(username):
		raise Exception('Пользователь не зарегестрирован')

	with open(users + username + os.sep + 'activity.txt', 'w') as file:
		file.write(datetime.datetime.today().strftime(full_format))


# активност пользователя
def unactive_users(time: int) -> list:
	now_time = datetime.datetime.now()
	unactive_user = []

	for user in os.listdir(users):
		if (now_time - get_activity(user)).days >= time:
			unactive_user.append(user)

	return unactive_user


def Users()->list:
	Users = []

	for user in os.listdir(users):
		Users.append(user)

	return Users


# python C:\\Users\\Света\\Desktop\\Bot\\database.py
