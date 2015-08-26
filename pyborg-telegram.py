#!/usr/bin/env python

import string
import sys
import telebot
import pyborg


class Boty:
	def __init__(self, boty, tg_bot):
		self.tg_bot = tg_bot
		self.pyborg = boty
		self.start()

	def handle_messages(self, messages):
		for message in messages:
			self.last_message = message
			name = message.from_user.first_name
			# self.pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
			self.pyborg.process_msg(self, message.text.encode('utf-8'), 100, 1, ( name ), owner=1)

	def start(self):
		self.tg_bot.set_update_listener(self.handle_messages)
		self.tg_bot.polling()
		
		while 1:
			try:
				pass
			except (KeyboardInterrupt, EOFError), e:
				return

	def output(self, message, args):
		"""
		Output a line of text.
		"""
		message = message.replace("#nick", args)
		print message

		self.tg_bot.reply_to(self.last_message, message)


API_TOKEN = '109641816:AAEYM_Q3g-1twI-7iEtk3yCB2jzc8-5iqh0'

telegram_bot = telebot.TeleBot(API_TOKEN)

my_pyborg = pyborg.pyborg()
try:
	Boty(my_pyborg, telegram_bot)
except SystemExit:
	pass
my_pyborg.save_all()
del my_pyborg
