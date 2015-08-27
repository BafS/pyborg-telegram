#!/usr/bin/env python

import string
import re
import sys
import time
import telebot
import lib.pyborg

class PyborgTelegram:
	def __init__(self, pyborg, args):
		API_TOKEN = ""
		for x in xrange(1, len(args)):
			if args[x] == "-t":
				try:
					API_TOKEN = args[x+1]
				except IndexError:
					print "! API TOKEN is empty (-t arg)"

		if(len(API_TOKEN) > 40):
			self.tg_bot = telebot.TeleBot(API_TOKEN)
			self.infos = self.tg_bot.get_me() # {'username': u'pybot_bot', 'first_name': u'boty', 'last_name': None, 'id': 109641816}
			self.pyborg = pyborg
			self.start()
		else:
			print "! No API TOKEN specified (use -t arg)"

	def start(self):
		self.tg_bot.set_update_listener(self.on_messages)
		self.tg_bot.polling()

		print "\nPYBORG TELEGRAM\n"

		while 1:
			try:
				pass
			except (KeyboardInterrupt, EOFError), e:
				return
			time.sleep(150)

	def on_messages(self, messages):
		"""
		Handle new messages
		"""
		for message in messages:
			body = message.text.encode('utf-8')

			if body == "":
				1
				# continue
			if body[0] == "/":
				self.on_command(message)
					# continue
				# if self.linein_commands(body):
					# continue
			else :
				name = message.from_user.first_name
				self.last_message = message

				# Replace the name of the bot by "#nick" (case insensitive)
				reg = re.compile(re.escape(self.infos.first_name), re.IGNORECASE)

				# Replace the username of the bot by "#nick"
				body = body.replace('@' + self.infos.username.encode('utf-8'), '#nick')

				# pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
				self.pyborg.process_msg(self, body, 100, 1, ( name ), owner=1)

	def on_command(self, command):
		print "CMD : " + command.text

		body = command.text.encode('utf-8')
		if(body == '/quit'):
			sys.exit(0)
			# raise SystemExit()

	def output(self, message, args):
		"""
		Output a line of text.
		"""
		message = message.replace("#nick", args)

		message = message.replace(self.last_message.from_user.first_name.encode('utf-8'), args.encode('utf-8'))
		print message
		print args

		self.tg_bot.send_message(self.last_message.chat.id, message)
		# self.tg_bot.reply_to(self.last_message, message)


if __name__ == "__main__":

	if "--help" in sys.argv:
		print "Pyborg Telegram bot. Usage:"
		print " pyborg-telegram.py -t API_TOKEN"
		print
		sys.exit(0)

	my_pyborg = lib.pyborg.pyborg()
	try:
		PyborgTelegram(my_pyborg, sys.argv)
	except (KeyboardInterrupt, SystemExit), e:
		pass
	my_pyborg.save_all()
	del my_pyborg
