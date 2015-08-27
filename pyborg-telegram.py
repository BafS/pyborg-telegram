#!/usr/bin/env python

import string
import sys
import time
import telebot
import pyborg


class PyborgTelegram:
	def __init__(self, pyborg, args):
		for x in xrange(1, len(args)):
			if args[x] == "-t":
				try:
					API_TOKEN = args[x+1]
				except IndexError:
					print "! No API TOKEN specified (use -t arg)"
					return

		self.tg_bot = telebot.TeleBot(API_TOKEN)
		self.pyborg = pyborg
		self.start()

	def start(self):
		self.tg_bot.set_update_listener(self.on_messages)
		self.tg_bot.polling()

		print "__ PYBORG TELEGRAM __"

		while 1:
			try:
				pass
			except (KeyboardInterrupt, EOFError), e:
				return
			time.sleep(100)

	def on_messages(self, messages):
		for message in messages:
			self.last_message = message
			name = message.from_user.first_name
			# self.pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)

			body = message.text.encode('utf-8')

			if body == "":
				1
				# continue
			if body[0] == "!":
				1
				# if self.linein_commands(body):
					# continue
			else :
				# pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
				self.pyborg.process_msg(self, body, 100, 1, ( name ), owner=1)

	def output(self, message, args):
		"""
		Output a line of text.
		"""
		# message = message.replace("#nick", args)

		message = message.replace(self.last_message.from_user.first_name.encode('utf-8'), args.encode('utf-8'))
		print message
		print args

		self.tg_bot.reply_to(self.last_message, message)


if __name__ == "__main__":

	if "--help" in sys.argv:
		print "Pyborg Telegram bot. Usage:"
		print " pyborg-telegram.py -t API_TOKEN [options]"
		# print " -n   nickname"
		# print "Defaults stored in pyborg-telegram.cfg"
		print
		sys.exit(0)

	my_pyborg = pyborg.pyborg()
	try:
		PyborgTelegram(my_pyborg, sys.argv)
	except (KeyboardInterrupt, SystemExit), e:
		pass
	my_pyborg.save_all()
	del my_pyborg
