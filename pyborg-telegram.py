#!/usr/bin/env python

import string
import re
import sys
import time
import telebot
import lib.pyborg
import os
from threading import Thread
import sys  

# fix utf8
reload(sys)  
sys.setdefaultencoding('utf8')

class PyborgTelegram:
    quiet = False
    talk = 1
    treshold = 3 # in s

    def __init__(self, pyborg, args):

        self.settings = lib.pyborg.cfgfile.cfgset()
        self.settings.load('pyborg-telegram.cfg',
            {
                  "owners": ("Owner(s) username (without the @)", ["myusername"]),
                  "replyrate": ("Chance of reply (%) per message", 33),
                  "name": ("Name of the bot", "Boty"),
                  "api_token": ("Telegram API Token", "<API_TOKEN>"),
                  "quitmsg": ("Quit message", "Bye :-(")
            })
        self.owners = self.settings.owners[:]

        for x in range(1, len(args)):
            if args[x] == '-q':
                self.quiet = True

        if self.settings.api_token is '<API_TOKEN>':
            self.settings.api_token = raw_input('Enter Telegram API TOKEN > ')
            self.settings.save()

        if len(self.settings.api_token) > 40:
            self.tg_bot = telebot.TeleBot(self.settings.api_token)
            self.infos = self.tg_bot.get_me() # {'username': u'pybot_bot', 'first_name': u'boty', 'last_name': None, 'id': 109641816}
            self.pyborg = pyborg
            self.start()
        else:
            if not self.quiet: print 'api_token is not valid'
            return

    def start(self):
        if not self.quiet: print '\r\nPYBORG TELEGRAM\r\n'

        self.tg_bot.set_update_listener(self.on_messages)
        self.tg_bot.polling()

    def on_messages(self, messages):
        '''
        Handle new messages
        '''
        for message in messages:

            # Check if it's a text message
            if hasattr(message, 'text'):
                body = message.text.encode('utf-8')
            else:
                body = ''

            if not body:
                pass

            elif body[0] == '/' or body[0] == '!':
                if int(time.time()) - int(message.date) <= self.treshold:
                    self.on_command(message)
            else:
                pattern = re.compile(self.settings.name, re.IGNORECASE)
                if pattern.match(message.text):
                    replyrate = 99
                else:
                    replyrate = self.settings.replyrate
                    
                name = message.from_user.first_name
                self.last_message = message

                # Replace the name of the bot by '#nick' (case insensitive)
                reg = re.compile(re.escape(self.infos.first_name), re.IGNORECASE)
                body = reg.sub('#nick', body)

                # Replace the username of the bot by '#nick'
                body = body.replace('@' + self.infos.username.encode('utf-8'), '#nick')

                if not self.quiet: print "{0} : {1}".format(name, body)

                # pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
                
                t = Thread(target=self.pyborg.process_msg, args=(self, body, self.talk * replyrate, 1, ( name ), 1))
                t.start()

    def on_command(self, message):
        '''
        Handle commands
        '''
        if not message or not message.text:
            print "Encoding error" # add try
            return

        rep = None

        if not self.quiet: print 'Command: ' + message.text

        is_owner = message.from_user.username.encode('utf-8') in self.owners
    
        
        words = message.text.split(' ')
        command = words[0].encode('utf-8')
        if len(words) > 1:
            arg = words[1]

        if is_owner:
            if command == '/save':
                self.pyborg.save_all()
            if command == '/bequiet':
                self.talk = 0
                rep = 'I will stop talking :('
            elif command == '/talk':
                self.talk = 1
                rep = 'I will talk !'
            elif command == '/replyrate':
                arg = int(arg)
                if arg <= 100:
                    if arg > self.settings.replyrate:
                        rep = 'Yeeess, I will talk moar ! (' + str(arg) + '%)'
                    elif arg < self.settings.replyrate:
                        rep = 'Ok I will try to be less chatty (' + str(arg) + '%)'

                    self.settings.replyrate = arg

            elif command == '/quit':
                self.pyborg.save_all()
                os._exit(0)

        else:
                if not self.quiet: print message.from_user.username.encode('utf-8') + ' is not an owner'

        if rep:
            self.tg_bot.send_message(message.chat.id, rep)

    def output(self, message, args):
        '''
        Output a line of text.
        '''

        message = message.replace('#nick', args.encode('utf-8'))

        message = message.replace(self.last_message.from_user.first_name.encode('utf-8'), args.encode('utf-8'))
        if not self.quiet: print '> ' + message

        self.tg_bot.send_message(self.last_message.chat.id, message)
        # self.tg_bot.reply_to(self.last_message, message)


if __name__ == '__main__':

    if '--help' in sys.argv:
        print 'Pyborg Telegram bot. Usage:'
        print ' pyborg-telegram.py [options]'
        print ''
        print ' -q               quiet mode'
        print ' -T               sleep time between messages (default 150ms)'
        print

    else:
        my_pyborg = lib.pyborg.pyborg()
        try:
            PyborgTelegram(my_pyborg, sys.argv)
        except (KeyboardInterrupt, SystemExit), e:
            pass
        my_pyborg.save_all()
        del my_pyborg
