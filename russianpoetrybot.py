# Импортируем нужные компоненты

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from lingcorpora import Corpus
import pronouncing
from rupo.api import Engine
from sys import getdefaultencoding


from urllib import request
from urllib.parse import quote
from bs4 import BeautifulSoup
from pyparsing import *
import re
import random
import lxml
import tqdm


# Настройки прокси

#PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080', 'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}}



import logging

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',

					level=logging.INFO,

					filename='logs/bot.log'

					)



def greet_user(bot, update):

	text = 'Привет!'

	print(text)

	update.message.reply_text(text)

	# print('Привет!')



def talk_to_me(bot, update):

	Otmazki = dict([(1,'Совсем не знак бездушья – молчаливость,\n Гремит лишь то, что пусто изнутри…'),
		(2,'Не потому что нечего сказать,\n Совсем наоборот – такая странность!..\n Права вдруг предъявила несказанность –\n Нечаянная тишь и благодать.'),
		(3,'А всякое и каждое молчание, \nне зная никакого исключения, \nимеет сокровенное звучание, \nисполненное смысла и значения.'),
		(4,'Мне, правда, нечего сказать, сегодня, как всегда, \nНо этим не был я смущен, поверьте, никогда'),
		(5,'Такое чувство \nБудто нечего сказать \nУж всё сказано'),
		(6,'Эта мысль - украденный цветок, \nпросто рифма ей не повредит: \nчеловек совсем не одинок - \nкто-нибудь всегда за ним следит')]
		)
	temp_string = update.message.text

	print('Пользователь написал: ' + temp_string)
	print('Уберем все знаки препинания')
	temp_string = re.sub(r'[^A-Za-zА-ЯЁа-яё0-9 ]', '', update.message.text)
	print(len(temp_string))
	print(temp_string)
#	проверим, не слишком ли короткое слово в конце
	space_position = temp_string.rfind(' ', 1,len(temp_string)-2)
	print(space_position)
	if space_position < 0: 
		user_text = temp_string
	else:
		user_text = re.sub(' ', '', temp_string[space_position:len(temp_string):])
	print(user_text)
	rhyme_set = scrap_rhyme(user_text)

#	print(rhyme_set)
	for i in range(3):
		rhyme_number = random.randint(i, len(rhyme_set))
		print(rhyme_number)
		print(rhyme_set[rhyme_number])
		out_text = get_poem(rhyme_set[rhyme_number])
		if out_text == '':
			continue 
		else:
			break
	if out_text == '':
		out_text = Otmazki[random.randint(1,len(Otmazki))]
	print(out_text)
	
#	update.message.reply_text('Ваше обращение будет обработано')
	update.message.reply_text(out_text)
#	update.message.reply_text('Все получилось')


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота

def main():
#
	mybot = Updater("735369145:AAFQ4hmTBLVNy48lLsoouUoXu52Vr4FWBlA")
	#, request_kwargs=PROXY)



	dp = mybot.dispatcher

	dp.add_handler(CommandHandler("start", greet_user))

	dp.add_handler(MessageHandler(Filters.text, talk_to_me))

	mybot.start_polling()

	mybot.idle()


def scrap_rhyme(word):
	#print('вход в запрос рифмы')
	geourl = "http://rifmik.net/rhyme/{0}".format(quote(word))
#	print('сформирован geourl '+geourl)
	rhymes = []
#	print('передаем запрос на сервер')
	response = request.urlopen(geourl)
	content = response.read().decode('utf-8')
#	print('content = ' + content)
#	print(content.find("inline vowel"))
	if content.find("inline vowel")>=0:
		print('пробуем уточнить ударение')
#		если пришел запрос на уточнение ударения
		for i in range(len(word)-1,-1,-1):
			if word[i] in ['а','е','ё','и','о','у','ы','э','ю','я','А','Е','Ё','И','О','У','Ы','Э','Ю','Я']: 
				word_accent = i
				print('присвоили позицию ударению: '+ str(word_accent))
				break
		print(word_accent)
		geourl = ("http://rifmik.net/rhyme/{0}?accent="+str(word_accent)).format(quote(word))
		print('сформирован новый geourl '+geourl)
#		print('передаем запрос на сервер')
		response = request.urlopen(geourl)
		content = response.read().decode('utf-8')
#		print('content = ' + content)
		content_1 = BeautifulSoup(content, "html.parser")
#		print('content1 = ' + content_1)

	else: 
		print('работаем по первоначальной выборке')
		#print('content = ' + content)
		content_1 = BeautifulSoup(content, "html.parser")
		print('отработал парсер')
		#print('content1 = ' + content_1)
	
	print('анализируем ответ')
	syll_number = 0
	for i in range(0,len(word),1):
		if word[i] in ['а','е','ё','и','о','у','ы','э','ю','я','А','Е','Ё','И','О','У','Ы','Э','Ю','Я']: 
			syll_number += 1
#
	goodcontent = content_1.find('div', attrs={'id':['syll'+str(syll_number)], 'class':'results pad-1'})
	#print(goodcontent)
	for goodcontentline in goodcontent:
		goodcontentline = str(goodcontentline)
		rhyme = re.sub(' ', '',goodcontentline)
		rhyme = re.sub('[<>= "/a-z0-9-V().\n]', '',rhyme)
		rhyme = re.sub('показатьещё', '',rhyme)
#		print(rhyme)
		if rhyme!='':
			rhymes += [rhyme]

	return list(rhymes)

def get_poem(word):
	print('Вошли в get_poem')
	rus_corp = Corpus('rus')
#	rus_results = rus_corp.search(user_text, numResults = 1)
#	try:
	rus_results = rus_corp.search(word, numResults = 20, kwic = True, subcorpus = 'poetic', nRight = 0)
#	except UserWarning:
		# вернем неудачу в вызывающую функцию
#		print('fail to find in Corpus')
#	else:
#		print('succeed to find in Corpus')
#	print(rus_results)
	print(getattr(rus_results[0], 'N'))
	if getattr(rus_results[0], 'N') == 0:
		result_poem = ''
		print('не нашли ничего')
	else:
		for result in rus_results :
			for i, target in enumerate(result):
				if target.text.rfind(word, 1,len(target.text))>=len(target.text)-len(word)-2:
					print(target.text)
					result_poem = target.text
					break
				else:
					result_poem = ''
	#		print(result)
	#		print('target_text = "' + target.text + '"')
	return result_poem


# Вызываем функцию - эта строчка собственно запускает бота

main()
