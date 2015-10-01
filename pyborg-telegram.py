#!/usr/bin/env python

import string
import re
import sys
import time
import telebot
import lib.pyborg
import os
#import thread

class PyborgTelegram:
    quiet = False
    sleep_time = 150
    talk = 1
    treshold = 1 # in s

    def __init__(self, pyborg, args):

        self.settings = lib.pyborg.cfgfile.cfgset()
        self.settings.load('pyborg-telegram.cfg',
            {
                  "owners": ("Owner(s) username (without the @)", ["myusername"]),
                  "replyrate": ("Chance of reply (%) per message", 33),
                  "api_token": ("Telegram API Token", "<API_TOKEN>"),
                  "quitmsg": ("Quit message", "Bye :-(")
            })
        self.owners = self.settings.owners[:]

        for x in range(1, len(args)):
            if args[x] == '-T':
                try:
                    if args[x+1].isdigit(): self.sleep_time = float(args[x+1])
                except IndexError:
                    if not self.quiet: print 'Invalid sleep_time value, set to 150'

            elif args[x] == '-q':
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

        #while 1:
        #    try:
        #        pass
        #    except (KeyboardInterrupt, EOFError), e:
        #        return
        #    time.sleep(self.sleep_time)

    def on_messages(self, messages):
        '''
        Handle new messages
        '''
        for message in messages:
            print message
            body = message.text.encode('utf-8')

            if not body:
                pass
            elif body[0] == '/':
                print int(time.time())
                print message.date
                print int(time.time()) - int(message.date)
                if int(time.time()) - int(message.date) <= self.treshold:
                    self.on_command(message)

            else:
                name = message.from_user.first_name
                self.last_message = message
                print name
                
                # Replace the name of the bot by '#nick' (case insensitive)
                reg = re.compile(re.escape(self.infos.first_name), re.IGNORECASE)
                body = reg.sub('#nick', body)

                # Replace the username of the bot by '#nick'
                print self.infos.username
                body = body.replace('@' + self.infos.username.encode('utf-8'), '#nick')

                if not self.quiet: print body

                # pyborg.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
                source = ''

                self.pyborg.process_msg(self, body, self.talk * self.settings.replyrate, 1, ( body, source, name ), owner=1)
                #thread.start_new_thread(self.pyborg.process_msg, (self, body, self.talk * self.settings.replyrate, 1, ( body, source, name ), owner=1))

    def on_command(self, message):
        '''
        Handle commands
        '''
        if not self.quiet: print 'Command: ' + message.text

        is_owner = message.from_user.username.encode('utf-8') in self.owners

        body = message.text.encode('utf-8')

        if is_owner:
            if body == '/bequiet':
                self.talk = 0
                rep = 'I will stop talking :('
            elif body == '/talk':
                self.talk = 1
                rep = 'I will talk !'
            elif body == '/quit':
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

        print "OUTPUT"
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
        sys.exit(0)

    my_pyborg = lib.pyborg.pyborg()
    try:
        PyborgTelegram(my_pyborg, sys.argv)
    except (KeyboardInterrupt, SystemExit), e:
        pass
    my_pyborg.save_all()
    del my_pyborg
