import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from statistics import mean
from schedule import TIME, SIZE, get_is_busy, is_session_exist
from database import date_format, time_format, halls, users
import datetime
import os

rus_weekday = ['понедельникам', 'вторникам', 'средам', 'четвергам', 'пятницам', 'субботам', 'воскресеньям']
rus_halls = {'Синий': 'Синего', 'Зеленый': 'Зеленого', 'Желтый': 'Желтого', 'Красный': 'Красного', 'Оранжевый': 'Оранжевого'}
color_hall = {'Синий':('#0009b8'), 'Зеленый':('green'), 'Желтый':('#ffd800'), 'Красный':('#d80000'),'Оранжевый':('orange')}


# Вернуть график загруженности зала
def return_congestion_hall(Date, Film, username: str):
	session = is_session_exist(lambda x: x == Film, lambda x: x == Date) 
	hall = session[0][-1] 
	congestion_hall(Date, hall, username)
	return users + username + os.sep + 'current' + os.sep + 'congestion_hall.png'


# Загруженность зала на все сеансы по дню недели == day за полгода
def get_stats(day, hall) -> list:
	stats = [0] * len(TIME[hall])
	count = [0] * len(TIME[hall])

	for week in range(1, 20):
		prev_day = day - week * datetime.timedelta(days=7)
		for session in range(len(TIME[hall])):
			if os.path.exists(halls + hall + os.sep + prev_day.strftime(date_format) + os.sep + TIME[hall][session]):
				count[session] += 1
				matrix = get_is_busy(prev_day, datetime.datetime.strptime(TIME[hall][session], time_format).time(), hall)
				stats[session] += sum(row.count(True) for row in matrix) / (SIZE[hall][0] * SIZE[hall][1])

	return [stats[i] / max(count[i], 1) * 100 for i in range(len(TIME[hall]))]


# Отрисовка графика загруженности
def congestion_hall(day, hall: str, username: str ) -> None:
	y = get_stats(day, hall)
	x = TIME[hall]
	fig, ax = plt.subplots()
	ax.bar(x, y, color = color_hall[hall])

	ax.set_title(f'Занятость {rus_halls[hall]} зала по {rus_weekday[datetime.datetime.weekday(day)]}', fontsize=15)
	ax.set_ylabel('Занятость зала в %')
	ax.set_facecolor('white')
	ax.set_ylim(0, 100)

	#ax.spines['bottom'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)

	ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

	fig.set_facecolor('white')
	fig.set_figwidth(6)
	fig.set_figheight(6)
	fig.savefig(users + username + os.sep + 'current' + os.sep + 'congestion_hall.png')
	#plt.show()

#congestion_hall(day=datetime.date(2020, 4, 23), hall='Оранжевый')
#python C:\\Users\\Света\\Desktop\\Bot\\congestion_hall.py