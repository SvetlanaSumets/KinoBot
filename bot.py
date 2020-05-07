from more_itertools import unique_everseen
import telebot
import threading
import database
import schedule
import ticket
import congestion_hall
import hallshow
import telegram
import datetime

TOKEN = '1194717790:AAETJV4ooKmDHhWsv6n1qAJUMUxv7d-kfxw'
bot = telebot.TeleBot(TOKEN)


# Выбор даты пользователем
def choose_date(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup()
	Date = list(unique_everseen([session[1] for session in schedule.filter(Film=database.get_current_film(username), Date='', Time=database.get_current_time(username), order_by = lambda x: x[1])]))

	for i in range(1, len(Date), 2):
		Date_left = Date[i - 1]
		Date_right = Date[i]
		button_left = telebot.types.InlineKeyboardButton(text='📆   '+Date_left.strftime(database.date_format)+'   📆', callback_data='choosen_date_' + Date_left.strftime(database.date_format))
		button_right = telebot.types.InlineKeyboardButton(text='📆   '+Date_right.strftime(database.date_format)+'   📆', callback_data='choosen_date_' + Date_right.strftime(database.date_format))
		keyboard.add(*[button_left, button_right])
	if len(Date) % 2:
		temp = Date[-1]
		keyboard.add(telebot.types.InlineKeyboardButton(text='📆   '+temp.strftime(database.date_format)+'   📆', callback_data='choosen_date_' + temp.strftime(database.date_format)))

	if database.get_current_film(username) != '':
		keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Назад к списку фильмов   🎥', callback_data='choose_film'))
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранного   ✖️', callback_data='main_menu'))
	elif database.get_current_film(username) == '':
		keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Назад в главное меню   📋', callback_data='main_menu'))
	
	if database.get_current_film(username) == '':
		bot.send_message(call.message.chat.id, text="Ниже список дат сеансов, выбери удобный для себя день:", reply_markup=keyboard)
	elif database.get_current_film(username) != '':
		bot.send_message(call.message.chat.id, text=f"Ниже список дат сеансов\n 🔹 на фильм {database.get_current_film(username)}\nВыбери удобный для себя день:", reply_markup=keyboard)


# Выбор фильма пользователем
def choose_film(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup()
	List = [session[0] for session in schedule.filter(Film='', Date=database.get_current_date(username), Time=database.get_current_time(username), order_by = lambda x: x[0])]
	for Film in list(unique_everseen(List)):
		keyboard.add(telebot.types.InlineKeyboardButton(text='🎥   '+Film+'   🎥', callback_data='choosen_film_' + Film))

	if database.get_current_date(username) != '':
		keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Назад к списку дат   📅', callback_data='choose_date'))
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранного   ✖️', callback_data='main_menu'))
	elif database.get_current_date(username) == '':
		keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Назад в главное меню   📋', callback_data='main_menu'))
	
	if database.get_current_date(username) == '':
		bot.send_message(call.message.chat.id, text="Ниже список фильмов, выбери понравившийся и получишь информацию о нем:", reply_markup=keyboard)
	elif database.get_current_date(username) != '':
		bot.send_message(call.message.chat.id, text=f"Ниже список фильмов\n 🔹 на {database.get_current_date(username)} число\nВыбери понравившийся и получишь информацию о нем:", reply_markup=keyboard)


# Выбор времени пользователем
def choose_time(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Film = database.get_current_film(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date) 
	Hall = session[0][-1] 
	
	List = [session[2] for session in schedule.filter(Film=database.get_current_film(username), Date=database.get_current_date(username), Time='', order_by = lambda x: x[2])]

	for Time in list(unique_everseen(List)):
		BUSY = schedule.get_is_busy(Date, Time, Hall)
		if not schedule.is_hall_filled(BUSY):
			keyboard.add(telebot.types.InlineKeyboardButton(text='⏰   '+Time.strftime(database.time_format)+' — '+schedule.price_list(Date, Time)+' грн   💰', callback_data='choosen_time_' + Time.strftime(database.time_format)))
	keyboard.add(telebot.types.InlineKeyboardButton(text='⤴️   Перевыбрать фильм   🎥', callback_data='choose_film'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='⤴️   Перевыбрать дату   📅', callback_data='choose_date'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранного   ✖️', callback_data='main_menu'))

	text = f"Ниже список времени сеансов\n 🔹 на {database.get_current_date(username)} число\n 🔹 на фильм {Film}\nВыбери удобное для себя время\nУчитывай то, что цена в будние и выходные дни разнится, так же как и зависит от времени сеанса:\n 🔺 Пн - Пт 9:00 - 18:00:    60 грн\n 🔺 Пн - Пт позже 18:00:  70 грн\n 🔺 Сб - Вс 9:00 - 18:00:    70 грн\n 🔺 Сб - Вс позже 18:00:   80 грн\nУчитывай среднюю загруженность зала в зависимости от времени сеанса (график выше)."
	photo = open(congestion_hall.return_congestion_hall(Date, Film, username), 'rb')
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)


# Бронирование мест пользователем
def booking(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	Price = schedule.price_list(Date, Time)

	keyboard.add(telebot.types.InlineKeyboardButton(text='🍿   Выбрать ряд и место   🎞', callback_data='choose_row'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='⤴️   Перевыбрать время   ⏰', callback_data='choose_time'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранного   ✖️', callback_data='main_menu'))

	bot.send_message(call.message.chat.id, text = f"Ты уже выбрал сеанс\n 🔹 на {database.get_current_date(username)} число\n 🔹 на фильм {Film}\n 🔹 на время {database.get_current_time(username)}\n 🔹 по цене {Price} грн\nНастало время выбрать места в зале.\n 🔺 Если ты готов продолжить, нажми на кнопку выбора ряда и места.\n 🔺 Eсли хочешь изменить выбранные параметры, нажми кнопку перевыбора времени (там же ты сможешь изменить выбор фильма и даты, если это необходимо).", reply_markup=keyboard)


# Выбор доступного ряда пользователем
def choose_row(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	Hall = session[0][-1] 
	Row = database.get_current_row(username)
	Col = database.get_current_col(username)
	Price = schedule.price_list(Date, Time)
	BUSY = schedule.get_is_busy(Date, Time, Hall)

	free_hall_row = []
	for i in range(schedule.SIZE[Hall][0]):
		if not schedule.is_row_busy(BUSY, i):
			free_hall_row.append(i+1)
		else:
			pass

	for i in range(2, len(free_hall_row), 3):
		row_left = free_hall_row[i-2]
		row_center = free_hall_row[i-1]
		row_right = free_hall_row[i]
		button_left = telebot.types.InlineKeyboardButton(text=f'▪️   {row_left}   ▪️', callback_data=f'choosen_row_{row_left}')
		button_center = telebot.types.InlineKeyboardButton(text=f'▪️   {row_center}   ▪️', callback_data=f'choosen_row_{row_center}')
		button_right = telebot.types.InlineKeyboardButton(text=f'▪️   {row_right}   ▪️', callback_data=f'choosen_row_{row_right}')
		keyboard.add(*[button_left, button_center, button_right])

	if len(free_hall_row) % 3 == 2:
		row_left_1 = free_hall_row[-2]
		row_right_1 = free_hall_row[-1]
		button_left_1 = telebot.types.InlineKeyboardButton(text=f'▪️   {row_left_1}   ▪️', callback_data=f'choosen_row_{row_left_1}')
		button_right_1 = telebot.types.InlineKeyboardButton(text=f'▪️   {row_right_1}   ▪️', callback_data=f'choosen_row_{row_right_1}')
		keyboard.add(*[button_left_1, button_right_1])

	elif len(free_hall_row) % 3 == 1:
		temp = free_hall_row[-1]
		keyboard.add(telebot.types.InlineKeyboardButton(text=f'▪️   {temp}   ▪️', callback_data=f'choosen_row_{temp}'))

	choosen ='\n✅ Уже забронированы:'
	if Row != [] and Col != []:
		for i in range(len(Row)):
			choosen += f'\n 👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n'
	else:
		choosen =''

	if Row == []:
		keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Назад   ⏰', callback_data='booking'))
	elif Row != []:
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Разбронировать места   ✖️', callback_data='booking_unbook'))
	
	text = f"Текущие данные:\n 🔹 Дата: {database.get_current_date(username)}\n 🔹 Фильм: {Film}\n 🔹 Время: {database.get_current_time(username)}\n 🔹 Зал: {Hall}\n 🔹 Цена: {Price} грн\n{choosen}\nПеред тобой зал\n 🔺 занятые места - тусклые клетки;\n 🔺 свободные места - голубые клетки.\nДля начала выбери ряд из списка ниже:"
	photo = open(hallshow.return_hallshow(Date, Time, Film, username), 'rb')
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)


# Выбор доступного места пользователем
def choose_col(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	Row = database.get_current_row(username)
	Col = database.get_current_col(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	Hall = session[0][-1] 
	Price = schedule.price_list(Date, Time)
	BUSY = schedule.get_is_busy(Date, Time, Hall)

	free_hall_col = []
	for col in range(schedule.SIZE[Hall][1]):
		if not schedule.is_site_busy(BUSY, Row[-1] - 1, col):
			free_hall_col.append(col + 1)
		else:
			pass

	for i in range(2, len(free_hall_col), 3):
		col_left = free_hall_col[i-2]
		col_center = free_hall_col[i-1]
		col_right = free_hall_col[i]
		button_left = telebot.types.InlineKeyboardButton(text=f'▪️   {col_left}   ▪️', callback_data=f'choosen_col_{col_left}')
		button_center = telebot.types.InlineKeyboardButton(text=f'▪️   {col_center}   ▪️', callback_data=f'choosen_col_{col_center}')
		button_right = telebot.types.InlineKeyboardButton(text=f'▪️   {col_right}   ▪️', callback_data=f'choosen_col_{col_right}')
		keyboard.add(*[button_left, button_center, button_right])
	
	if len(free_hall_col) % 3 == 2:
		col_left_1 = free_hall_col[-2]
		col_right_1 = free_hall_col[-1]
		button_left_1 = telebot.types.InlineKeyboardButton(text=f'▪️   {col_left_1}   ▪️', callback_data=f'choosen_col_{col_left_1}')
		button_right_1 = telebot.types.InlineKeyboardButton(text=f'▪️   {col_right_1}   ▪️', callback_data=f'choosen_col_{col_right_1}')
		keyboard.add(*[button_left_1, button_right_1])

	elif len(free_hall_col) % 3 == 1:
		temp = free_hall_col[-1]
		keyboard.add(telebot.types.InlineKeyboardButton(text=f'▪️   {temp}   ▪️', callback_data=f'choosen_col_{temp}'))

	choosen ='\n✅ Уже забронированы:'
	if Col != []:
		for i in range(len(Col)):
			choosen += f'\n 👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n'
	else:
		choosen =''

	keyboard.add(telebot.types.InlineKeyboardButton(text='🔙   Перевыбрать ряд   👥', callback_data='choose_row'))
	if Col ==[]:
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранных мест   ✖️', callback_data='booking'))
	
	text = f"Текущие данные:\n 🔹 Дата: {database.get_current_date(username)}\n 🔹 Фильм: {Film}\n 🔹 Время: {database.get_current_time(username)}\n 🔹 Зал: {Hall}\n 🔹 Цена: {Price} грн\n{choosen}\n 👥 Текущий выбранный ряд: {Row[-1]}\n\nПеред тобой зал\n 🔺 занятые места в выбранном ряду - тусклые клетки;\n 🔺 свободные места в выбранном ряду - оранжевые клетки.\nВыбери номер места из списка ниже:"
	photo = open(hallshow.return_hallshow(Date, Time, Film, username, [Row[-1]]), 'rb')
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)


# Главное меню
def to_book_site(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	Row = database.get_current_row(username)
	Col = database.get_current_col(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	print(session)
	Hall = session[0][-1] 
	Price = schedule.price_list(Date, Time)
	BUSY = schedule.get_is_busy(Date, Time, Hall)

	choosen ='\n✅ Уже забронированы:'
	if len(Row) != 1:
		for i in range(len(Row)-1):
			choosen += f'\n 👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n'
	else:
		choosen = ''

	keyboard.add(telebot.types.InlineKeyboardButton(text=f'✅   Забронировать и выбрать еще место   👤', callback_data='book_and_choose_row'))
	keyboard.add(telebot.types.InlineKeyboardButton(text=f'✅   Забронировать и продолжить   🔜', callback_data='book_and_continue'))
	keyboard.add(telebot.types.InlineKeyboardButton(text=f'🔙   Перевыбрать место в {Row[-1]} ряду   👤', callback_data='choose_col'))
	keyboard.add(telebot.types.InlineKeyboardButton(text=f'🔙   Перевыбрать ряд   👥', callback_data='rechoose_row'))
	if len(Row) == 1:
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс выбранных мест   ✖️', callback_data='booking'))
	else:
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сбросить и разбронировать места   ✖️', callback_data='booking_unbook_part'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сброс всего   ✖️', callback_data='main_menu_unbook_part'))
	
	text = f"Текущие данные:\n 🔹 Дата: {database.get_current_date(username)}\n 🔹 Фильм: {Film}\n 🔹 Время: {database.get_current_time(username)}\n 🔹 Зал: {Hall}\n 🔹 Цена: {Price} грн\n {choosen}\n👥 Текущий выбранный ряд: {Row[-1]}\n👤 Текущее выбранное место: {Col[-1]}"
	photo = open(hallshow.return_hallshow(Date, Time, Film, username, [Row[-1]], [Col[-1]]), 'rb')
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)


# Функция проверки данных брони
def data_checking(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	Row = database.get_current_row(username)
	Col = database.get_current_col(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	Hall = session[0][-1] 
	Price = schedule.price_list(Date, Time)
	BUSY = schedule.get_is_busy(Date, Time, Hall)

	choosen ='\n'
	check = 'Проверка забронированных мест:\n'
	for i in range(len(Row)):
		choosen += f'\n 👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n'
		check += f'👥 Ряд: {Row[i]}; 👤 Место: {Col[i]} — забронированы {schedule.is_site_busy_whom2(Date, Time, Hall, Row[i]-1, Col[i]-1)}\n'
	check += '\n Пожалуйста, проверь все данные выше.\n 🔺 Если все ок, нажми кнопку завершения\n 🔺 Если указанный username не твой, или ты хочешь перевыбрать места на выбранный сеанс, нажми на кнопку перевыбора мест.\n 🔺 Если хочешь аннулировать все данные, нажми на кнопку сброса всех данных.'

	keyboard.add(telebot.types.InlineKeyboardButton(text='✅   Все ок, завершить   ✅', callback_data='the_end'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Разбронировать места и выбрать снова   ✖️', callback_data='booking_unbook'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='✖️   Сбросить данные и разбронировать   ✖️', callback_data='main_menu_unbook'))
	
	text = f"Текущие данные:\n 🔹 Дата: {database.get_current_date(username)}\n 🔹 Фильм: {Film}\n 🔹 Время: {database.get_current_time(username)}\n 🔹 Зал: {Hall}\n 🔹 Цена: {Price} грн{choosen}\n{check}"
	photo = open(hallshow.return_hallshow(Date, Time, Film, username, Row, Col), 'rb')
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)


# Установить рейтинг фильма
def pol_rating(call) -> None:
	username = '@' + call.from_user.username
	keyboard = telebot.types.InlineKeyboardMarkup() 

	rating = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
	rat = [1,2,3,4,5,6,7,8,9,'d']

	data = database.history_date_time_film(username)
	row = data[-1]
	Film = row[-1]

	for i in range(2, len(rating), 3):
		left = rating[i-2]
		left_i = rat[i-2]
		center = rating[i-1]
		center_i = rat[i-1]
		right = rating[i]
		right_i = rat[i]
		button_left = telebot.types.InlineKeyboardButton(text=f'▪️   {left}   ▪️', callback_data=f'choosen_rating_{left_i}_{Film}')
		button_center = telebot.types.InlineKeyboardButton(text=f'▪️   {center}   ▪️', callback_data=f'choosen_rating_{center_i}_{Film}')
		button_right = telebot.types.InlineKeyboardButton(text=f'▪️   {right}   ▪️', callback_data=f'choosen_rating_{right_i}_{Film}')
		keyboard.add(*[button_left, button_center, button_right])

	temp = rating[-1]
	temp_i = rat[-1]
	keyboard.add(telebot.types.InlineKeyboardButton(text=f'▪️   {temp}   ▪️', callback_data=f'choosen_rating_{temp_i}_{Film}'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='☹️   Я не хочу голосовать   ☹️', callback_data='not_rating'))
	bot.send_message(call.message.chat.id, text=f"После просмотра фильма {Film}\nОцени, на сколько баллов тебе понравился этот фильм", reply_markup=keyboard)


# Функция завершения брони
def the_end(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup() 
	Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
	Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
	Film = database.get_current_film(username)
	Row = database.get_current_row(username)
	Col = database.get_current_col(username)
	session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
	Hall = session[0][-1] 
	Price = schedule.price_list(Date, Time)

	keyboard.add(telebot.types.InlineKeyboardButton(text=f'✖️   Отмена текущей брони   ✖️', callback_data=f'cancellation'))
	keyboard.add(telebot.types.InlineKeyboardButton(text=f'🔄   Выбрать что-то еще   🔄', callback_data=f'start_call'))
	text = f"Спасибо, жду тебя 😉\n"
	photo = open(ticket.return_ticket(Date, Time, Film, Hall, Price, username, Row, Col), 'rb')
	bot.delete_message(call.message.chat.id, call.message.message_id)
	bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)

	pol_rating(call)


# Функция удаления пользователя
def delete(call) -> None:
	username = '@' + call.from_user.username

	if not username:
		bot.send_message(call.message.chat.id, 'Прости, но твое имя @User не задано. Задай свой username')
		return

	if not database.is_user_exist(username):
		bot.send_message(call.message.chat.id, 'Прости, ты еще не зарегестрирован в базе данных')
	else:
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.add(telebot.types.InlineKeyboardButton(text='🤪   Даааа   🤪', callback_data='bye_yes'))
		keyboard.add(telebot.types.InlineKeyboardButton(text='🤪   Нееет   🤪', callback_data='bye_no'))
		bot.send_message(call.message.chat.id, 'Хочешь удалить свое имя из моей базы данных?', reply_markup=keyboard)


# Функция разбронирования билетa
@bot.message_handler(commands=['unbook'])
def unbook(message) -> None:
	username = '@' + message.from_user.username
	keyboard = telebot.types.InlineKeyboardMarkup()

	List = schedule.history_actually(username) 
	if List != []:
		Text=''
		for i in range(len(List)):
			Text += f'{i+1}). Фильм: {List[i][4]}\n Дата: {List[i][0]}\n Время: {List[i][1]}\n Ряд: {List[i][2]}\n Место: {List[i][3]}\n\n'
			keyboard.add(telebot.types.InlineKeyboardButton(text=f'{i+1}', callback_data=f'unbook_{List[i][0]}_{List[i][1]}_{List[i][2]}_{List[i][3]}'))
		bot.send_message(message.chat.id, Text, reply_markup=keyboard)
	else:
		bot.send_message(message.chat.id, '🙃 У тебя нет текущих/непростроченных броней')


# Функция текущих броней
@bot.message_handler(commands=['reservation'])
def reservation(message) -> None:
	username = '@' + message.from_user.username
	keyboard = telebot.types.InlineKeyboardMarkup()

	List = schedule.history_actually(username) 
	if List != []:
		Text=''
		for i in range(len(List)):
			Text += f'{i+1}). Фильм: {List[i][4]}\n Дата: {List[i][0]}\n Время: {List[i][1]}\n Ряд: {List[i][2]}\n Место: {List[i][3]}\n\n'
		bot.send_message(message.chat.id, Text)
	else:
		bot.send_message(message.chat.id, '🙃 У тебя нет текущих/непростроченных броней')


# Функция разбронирования билетв после завершения
def unbook_end(call) -> None:
	username = '@' + call.from_user.username
	keyboard = telebot.types.InlineKeyboardMarkup()

	List = schedule.history_actually(username) 
	if List != []:
		Text=''
		for i in range(len(List)):
			Text += f'{i+1}). Фильм: {List[i][4]}\n Дата: {List[i][0]}\n Время: {List[i][1]}\n Ряд: {List[i][2]}\n Место: {List[i][3]}\n\n'
			keyboard.add(telebot.types.InlineKeyboardButton(text=f'{i+1}', callback_data=f'unbook_{List[i][0]}_{List[i][1]}_{List[i][2]}_{List[i][3]}'))
		bot.send_message(call.message.chat.id, Text, reply_markup=keyboard)
	else:
		bot.send_message(call.message.chat.id, '🙃 У тебя нет текущих/непростроченных броней')


# Главное меню
def main_menu(call) -> None:
	username = '@' + call.from_user.username

	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(telebot.types.InlineKeyboardButton(text='📅   Даты сеансов   📅', callback_data='choose_date'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='🎬   Сейчас в прокате   🎬', callback_data='choose_film'))
	bot.send_message(call.message.chat.id, text="Для начала у тебя есть выбор:\n 🔺 Посмотреть возможные даты сеансов и фильмы в эти дни;\n 🔺 Посмотреть фильмы, что сейчас в прокате, и даты их показа.", reply_markup=keyboard)
		



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Действия кнопок
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
	username = '@' + call.from_user.username

	if call.data == 'main_menu':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		database.clean_current_date(username)
		database.clean_current_film(username)
		database.clean_current_time(username)
		database.clean_current_row(username)
		database.clean_current_col(username)
		main_menu(call)


	elif call.data == 'main_menu_unbook':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.send_message(call.message.chat.id, text="❌ Ты сбросил все выбранные параметры и разбронировал все места")

		for i in range(len(Row)):
			schedule.unbook(Date, Time, Row[i], Col[i], username, Hall)
			database.delete_user_history(username, Date, Time, Hall, Row[i], Col[i], Film)

		database.clean_current_date(username)
		database.clean_current_film(username)
		database.clean_current_time(username)
		database.clean_current_row(username)
		database.clean_current_col(username)
		main_menu(call)


	elif call.data == 'main_menu_unbook_part':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		bot.delete_message(call.message.chat.id, call.message.message_id)
		if len(Row)!=1:
			bot.send_message(call.message.chat.id, text="❌ Ты сбросил все выбранные параметры и разбронировал все места")
		else:
			bot.send_message(call.message.chat.id, text="❌ Ты сбросил все выбранные параметры")	

		for i in range(len(Row)-1):
			schedule.unbook(Date, Time, Row[i], Col[i], username, Hall)
			database.delete_user_history(username, Date, Time, Hall, Row[i], Col[i], Film)

		database.clean_current_date(username)
		database.clean_current_film(username)
		database.clean_current_time(username)
		database.clean_current_row(username)
		database.clean_current_col(username)
		main_menu(call)


	elif call.data == 'choose_date':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		choose_date(call)


	elif call.data == 'choose_film':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		choose_film(call)


	elif call.data == 'choose_time':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		database.clean_current_time(username)
		choose_time(call)


	elif call.data == 'booking':
		database.clean_current_row(username)
		database.clean_current_col(username)
		bot.delete_message(call.message.chat.id, call.message.message_id)
		booking(call)


	elif call.data == 'booking_unbook':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		Text = f"❌ Ты разбронировал:\n"
		for i in range(len(Row)):
			schedule.unbook(Date, Time, Row[i], Col[i], username, Hall)
			database.delete_user_history(username, Date, Time, Hall, Row[i], Col[i], Film)
			Text += f' 👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n\n'
			
		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.send_message(call.message.chat.id, text=Text)

		database.clean_current_row(username)
		database.clean_current_col(username)
		booking(call)


	elif call.data == 'booking_unbook_part':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		Text = f'❌ Ты сбросил выбранные места:\n 👥 Ряд: {Row[-1]}\n 👤 Место: {Col[-1]}\n\n❌ Ты разбронировал:\n' 
		for i in range(len(Row)-1):
			schedule.unbook(Date, Time, Row[i], Col[i], username, Hall)
			database.delete_user_history(username, Date, Time, Hall, Row[i], Col[i], Film)
			Text += f'👥 Ряд: {Row[i]}\n 👤 Место: {Col[i]}\n\n'

		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.send_message(call.message.chat.id, text=Text)

		database.clean_current_row(username)
		database.clean_current_col(username)
		booking(call)


	elif call.data == 'choose_row':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		database.clean_current_last_row(username)
		choose_row(call)


	elif call.data == 'choose_col':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		database.clean_current_last_col(username)
		choose_col(call)


	elif call.data == 'rechoose_row':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		database.clean_current_last_col(username)
		database.clean_current_last_row(username)
		choose_row(call)


	elif call.data == 'book_and_choose_row':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		bot.send_message(call.message.chat.id, f'✅ Ты забронировал:\n 👥 Ряд: {Row[-1]}\n 👤 Место: {Col[-1]}')
		bot.delete_message(call.message.chat.id, call.message.message_id)

		schedule.book(Date, Time, Row[-1], Col[-1], username, Hall)
		database.add_user_history(username, Date, Time, Hall, Row[-1], Col[-1], Film)
		choose_row(call)


	elif call.data == 'book_and_continue':
		Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
		Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()
		Film = database.get_current_film(username)
		Row = database.get_current_row(username)
		Col = database.get_current_col(username)
		session = schedule.is_session_exist(lambda x: x == Film, lambda x: x == Date, lambda x: x == Time) 
		Hall = session[0][-1] 

		bot.send_message(call.message.chat.id, f'✅ Ты забронировал:\n 👥 Ряд: {Row[-1]}\n 👤 Место: {Col[-1]}')
		bot.delete_message(call.message.chat.id, call.message.message_id)
		schedule.book(Date, Time, Row[-1], Col[-1], username, Hall)
		database.add_user_history(username, Date, Time, Hall, Row[-1], Col[-1], Film)
		data_checking(call)


	elif call.data == 'the_end':
		the_end(call)


	elif call.data == 'cancellation':
		unbook_end(call)


	elif call.data == 'not_rating':
		bot.send_message(call.message.chat.id, f'Ну и ладно, зануда 🤓')
		bot.delete_message(call.message.chat.id, call.message.message_id)


	elif call.data == 'delete':
		bot.delete_message(call.message.chat.id, call.message.message_id)
		delete(call)


	elif call.data == 'bye_yes':
		username = '@' + call.from_user.username
		database.delete_user(username)
		bot.send_message(call.message.chat.id, '😭 Ты удален из базы данных\n🤩 Ну и ладно, если что, заглядывай снова')
		bot.delete_message(call.message.chat.id, call.message.message_id)
	

	elif call.data == 'bye_no':
		bot.send_message(call.message.chat.id, '🥳🥳🥳🥳🥳🥳🥳🥳 Урааааааааааа, ты остаешься со мной')
		bot.delete_message(call.message.chat.id, call.message.message_id)


	elif call.data == 'start_call':
		start_call(call)


	elif call.data[:6] == 'unbook':
		username = '@' + call.from_user.username
		keyboard = telebot.types.InlineKeyboardMarkup()

		Date =datetime.datetime.strptime(call.data[7:17], database.date_format).date()
		Time = datetime.datetime.strptime(call.data[18:23], database.time_format).time()
		
		RowCol = call.data[24:]
		RowCol = RowCol.split('_')
		Row = int(RowCol[0])
		Col = int(RowCol[1])

		session = schedule.is_session_exist(date1 =lambda x: x ==  Date, time1 =lambda x: x == Time) 
		Hall = session[0][-1] 
		Film = session[0][0] 

		schedule.unbook(Date, Time, Row, Col, username, Hall)
		database.delete_user_history(username, Date, Time, Hall, Row, Col, Film)
		bot.delete_message(call.message.chat.id, call.message.message_id)
		keyboard.add(telebot.types.InlineKeyboardButton(text='✖️  Аннулировать еще одну бронь  ✖️', callback_data='cancellation'))
		bot.send_message(call.message.chat.id, f'✅ Билет успешно аннулирован',reply_markup=keyboard)
			

	elif call.data[:7] == 'choosen':
		if call.data[8:12] == 'date':
			database.set_current_date(call.data[13:], '@' + call.from_user.username)
			bot.send_message(call.message.chat.id, f'📅 Ты выбрал дату: {call.data[13:]}')
			bot.delete_message(call.message.chat.id, call.message.message_id)

			if database.get_current_film(username) == '':
				choose_film(call)
			elif database.get_current_date(username) != '' and database.get_current_film(username) != '':
				choose_time(call)


		if call.data[8:12] == 'time':
			database.set_current_time(call.data[13:], '@' + call.from_user.username)
			Date = datetime.datetime.strptime(database.get_current_date(username), database.date_format).date()
			Time = datetime.datetime.strptime(database.get_current_time(username), database.time_format).time()

			bot.send_message(call.message.chat.id, f'⏰ Ты выбрал время: {call.data[13:]}\n💰 Цена сеанса: {schedule.price_list(Date, Time)} грн')
			bot.delete_message(call.message.chat.id, call.message.message_id)
			booking(call)


		if call.data[8:12] == 'film':
			database.set_current_film(call.data[13:], '@' + call.from_user.username)
			bot.send_message(call.message.chat.id, f'🎥 Ты выбрал фильм: {call.data[13:]}')
			bot.delete_message(call.message.chat.id, call.message.message_id)

			keyboard = telebot.types.InlineKeyboardMarkup()
			info = database.information_about_film(call.data[13:])
			text = f"{call.data[13:]}:\n\n 🔸 Год: {info[0]}\n 🔸 Страна: {info[1]}\n 🔸 Режиссер(ы): {info[2]}\n 🔸 Жанр(ы): {info[3]}\n 🔸 Длительность: {info[4]} мин\n 🔸 Актеры: {info[5]} и др.\n 🔸 Рейтинг: {info[6]}"
			photo = open(database.photo(call.data[13:]), 'rb')
			if info[7] == '—':
				bot.send_photo(call.message.chat.id, photo, text)
			else:
				keyboard.add(telebot.types.InlineKeyboardButton(text='🔍   Узнать больше   🔎', url=info[7]))
				bot.send_photo(call.message.chat.id, photo, text, reply_markup=keyboard)

			if database.get_current_date(username) == '':
				choose_date(call)
			elif database.get_current_date(username) != '' and database.get_current_film(username) != '':
				choose_time(call)


		if call.data[8:11] == 'row':
			database.set_current_row(call.data[12:], '@' + call.from_user.username)
			bot.send_message(call.message.chat.id, f'👥 Ты выбрал ряд: {call.data[12:]}')
			bot.delete_message(call.message.chat.id, call.message.message_id)
			choose_col(call)


		if call.data[8:11] == 'col':
			database.set_current_col(call.data[12:], '@' + call.from_user.username)
			bot.send_message(call.message.chat.id, f'👤 Ты выбрал место: {call.data[12:]}')
			bot.delete_message(call.message.chat.id, call.message.message_id)
			to_book_site(call)


		if call.data[8:14] == 'rating':
			rating = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
			if call.data[15:16] != 'd':
				database.update_rating(call.data[15:16], call.data[17:])
				bot.send_message(call.message.chat.id, f'📈 Ты поставил фильму {call.data[17:]} оценку {rating[int(call.data[15:16])-1]}\nСпасибо за оставленный ответ 😘')
			else:
				database.update_rating('10', call.data[17:])
				bot.send_message(call.message.chat.id, f'📈 Ты поставил фильму {call.data[17:]} оценку {rating[-1]}\nСпасибо за оставленный ответ 😘')
			bot.delete_message(call.message.chat.id, call.message.message_id)
		



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Повторный старт
def start_call(call) -> None:
	username = '@' + call.from_user.username
	database.clean_current_date(username)
	database.clean_current_film(username)
	database.clean_current_time(username)
	database.clean_current_row(username)
	database.clean_current_col(username)
	main_menu(call)

# Начало работы бота
@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Привет, я KinoBot, давай погрузимся в мир кино вместе! Я помогу тебе бронировать билеты на любимые фильмы. Но вначале давай познакомимся, поэтому я внесу тебя в свою базу данных')
	if not message.from_user.username:
		bot.send_message(message.chat.id, 'Прости, но твое имя @User не задано. Задай свой username')
		return 
	username = '@' + message.from_user.username

	if database.is_user_exist(username):
		bot.send_message(message.chat.id, 'Прости, склероз, ты уже зарегестрирован в базе данных')

	elif not database.is_user_exist(username):
		database.add_user(message.chat.id, username)
		bot.send_message(message.chat.id, 'Все, ты зарегестрирован в базе данных')
	
	database.set_activity(username)
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(telebot.types.InlineKeyboardButton(text='😁   ДAAA   😁', callback_data='main_menu'))
	keyboard.add(telebot.types.InlineKeyboardButton(text='🙃   Да   🙃', callback_data='main_menu'))
	bot.send_message(message.chat.id, text="В кинотеатре есть 5️⃣ залов: Синий, Зеленый, Красный, Оранжевый, Желтый.\nВ зависимости от выбранных тобой времени и даты варируется цена:\n 🔺 Пн - Пт 9:00 - 18:00:    60 грн\n 🔺 Пн - Пт позже 18:00:  70 грн\n 🔺 Сб - Вс 9:00 - 18:00:    70 грн\n 🔺 Сб - Вс позже 18:00:   80 грн\n\nГотов начать?", reply_markup=keyboard)


# Ответ на текстовое смс
@bot.message_handler(content_types=['text'])
def answerTheMessage(message):
	bot.send_message(message.chat.id, '☹️ Следуй моим инструкциям, я не понимаю твоего сообщения')


# Стартовая функция
def start_def():
	for user in database.unactive_users(100):
		try:
			bot.send_message(database.getID(user), 'Ты не заходил ко мне на протяжении 100 дней, я удалил тебя из базы данных')
		except telebot.apihelper.ApiException:
			pass
		database.delete_user(user)

	for user in database.unactive_users(30): #если ты не заходил больше 30 дней
		if (datetime.datetime.now() - database.get_alert(user)).days >= 30: #если не было оповещений больше 30 дней
			delta = datetime.datetime.now() - database.get_activity(user)
			try:
				bot.send_message(database.get_user_id(user), f'Ты не заходил ко мне на протяжении {delta.days} дней')
				keyboard = telebot.types.InlineKeyboardMarkup()
				keyboard.add(telebot.types.InlineKeyboardButton(text='😐   Удали меня из базы данных   😐', callback_data='delete'))
				bot.send_message(database.get_user_id(user), 'Я удалю тебя из своей базы данных, если ты подолгу не будешь меня навещать', reply_markup=keyboard)
			except telebot.apihelper.ApiException:
				database.delete_user(user)
			else:
				database.set_alert(user)

	threading.Timer(60, start_def).start()


# Фильмы, что будут в ближайшее время
def novelty():
	keyboard = telebot.types.InlineKeyboardMarkup()
	if datetime.datetime.now().time().strftime(database.time_format) == datetime.time(16,46).strftime(database.time_format):
		data =[]
		for user in database.Users(): 
			List = schedule.novelty()

			Text = 'В ближайшие дни есть сеансы на интересные фильмы, такие как\n'
			for row in range(5):
				Text += f' 🎥 {List[row]}\n'
			Text += 'и многие другие\nСкорее нажимай /start'
			bot.send_message(database.get_user_id(user), Text)

	threading.Timer(60, novelty).start()


start_def()
novelty()
schedule.clean_halls()
schedule.clean_schedule()

print('Бот запущен')
bot.polling(none_stop = True, interval = 0)
# python C:\\Users\\Света\\Desktop\\Bot\\bot.py	
