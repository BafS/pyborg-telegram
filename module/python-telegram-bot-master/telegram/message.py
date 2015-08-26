#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].


from telegram import TelegramObject
from datetime import datetime
from time import mktime


class Message(TelegramObject):
    def __init__(self,
                 message_id,
                 from_user,
                 date,
                 chat,
                 forward_from=None,
                 forward_date=None,
                 reply_to_message=None,
                 text=None,
                 audio=None,
                 document=None,
                 photo=None,
                 sticker=None,
                 video=None,
                 voice=None,
                 caption=None,
                 contact=None,
                 location=None,
                 new_chat_participant=None,
                 left_chat_participant=None,
                 new_chat_title=None,
                 new_chat_photo=None,
                 delete_chat_photo=None,
                 group_chat_created=None):
        self.message_id = message_id
        self.from_user = from_user
        self.date = date
        self.chat = chat
        self.forward_from = forward_from
        self.forward_date = forward_date
        self.reply_to_message = reply_to_message
        self.text = text
        self.audio = audio
        self.document = document
        self.photo = photo
        self.sticker = sticker
        self.video = video
        self.voice = voice
        self.caption = caption
        self.contact = contact
        self.location = location
        self.new_chat_participant = new_chat_participant
        self.left_chat_participant = left_chat_participant
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created

    @property
    def chat_id(self):
        return self.chat.id

    @staticmethod
    def de_json(data):
        if 'from' in data:  # from is a reserved word, use from_user instead.
            from telegram import User
            from_user = User.de_json(data['from'])
        else:
            from_user = None

        if 'date' in data:
            date = datetime.fromtimestamp(data['date'])
        else:
            date = None

        if 'chat' in data:
            if 'first_name' in data['chat']:
                from telegram import User
                chat = User.de_json(data['chat'])
            if 'title' in data['chat']:
                from telegram import GroupChat
                chat = GroupChat.de_json(data['chat'])
        else:
            chat = None

        if 'forward_from' in data:
            from telegram import User
            forward_from = User.de_json(data['forward_from'])
        else:
            forward_from = None

        if 'forward_date' in data:
            forward_date = datetime.fromtimestamp(data['forward_date'])
        else:
            forward_date = None

        if 'reply_to_message' in data:
            reply_to_message = Message.de_json(data['reply_to_message'])
        else:
            reply_to_message = None

        if 'audio' in data:
            from telegram import Audio
            audio = Audio.de_json(data['audio'])
        else:
            audio = None

        if 'document' in data:
            from telegram import Document
            document = Document.de_json(data['document'])
        else:
            document = None

        if 'photo' in data:
            from telegram import PhotoSize
            photo = [PhotoSize.de_json(x) for x in data['photo']]
        else:
            photo = None

        if 'sticker' in data:
            from telegram import Sticker
            sticker = Sticker.de_json(data['sticker'])
        else:
            sticker = None

        if 'video' in data:
            from telegram import Video
            video = Video.de_json(data['video'])
        else:
            video = None

        if 'voice' in data:
            from telegram import Voice
            voice = Voice.de_json(data['voice'])
        else:
            voice = None

        if 'contact' in data:
            from telegram import Contact
            contact = Contact.de_json(data['contact'])
        else:
            contact = None

        if 'location' in data:
            from telegram import Location
            location = Location.de_json(data['location'])
        else:
            location = None

        if 'new_chat_participant' in data:
            from telegram import User
            new_chat_participant = User.de_json(data['new_chat_participant'])
        else:
            new_chat_participant = None

        if 'left_chat_participant' in data:
            from telegram import User
            left_chat_participant = User.de_json(data['left_chat_participant'])
        else:
            left_chat_participant = None

        if 'new_chat_photo' in data:
            from telegram import PhotoSize
            new_chat_photo = \
                [PhotoSize.de_json(x) for x in data['new_chat_photo']]
        else:
            new_chat_photo = None

        return Message(message_id=data.get('message_id', None),
                       from_user=from_user,
                       date=date,
                       chat=chat,
                       forward_from=forward_from,
                       forward_date=forward_date,
                       reply_to_message=reply_to_message,
                       text=data.get('text', ''),
                       audio=audio,
                       document=document,
                       photo=photo,
                       sticker=sticker,
                       video=video,
                       voice=voice,
                       caption=data.get('caption', ''),
                       contact=contact,
                       location=location,
                       new_chat_participant=new_chat_participant,
                       left_chat_participant=left_chat_participant,
                       new_chat_title=data.get('new_chat_title', None),
                       new_chat_photo=new_chat_photo,
                       delete_chat_photo=data.get('delete_chat_photo', None),
                       group_chat_created=data.get('group_chat_created', None))

    def to_dict(self):
        data = {'message_id': self.message_id,
                'from': self.from_user.to_dict(),
                'chat': self.chat.to_dict()}
        try:
            # Python 3.3+ supports .timestamp()
            data['date'] = int(self.date.timestamp())

            if self.forward_date:
                data['forward_date'] = int(self.forward_date.timestamp())
        except AttributeError:
            # _totimestamp() for Python 3 (< 3.3) and Python 2
            data['date'] = self._totimestamp(self.date)

            if self.forward_date:
                data['forward_date'] = self._totimestamp(self.forward_date)

        if self.forward_from:
            data['forward_from'] = self.forward_from.to_dict()
        if self.reply_to_message:
            data['reply_to_message'] = self.reply_to_message.to_dict()
        if self.text:
            data['text'] = self.text
        if self.audio:
            data['audio'] = self.audio.to_dict()
        if self.document:
            data['document'] = self.document.to_dict()
        if self.photo:
            data['photo'] = [p.to_dict() for p in self.photo]
        if self.sticker:
            data['sticker'] = self.sticker.to_dict()
        if self.video:
            data['video'] = self.video.to_dict()
        if self.voice:
            data['voice'] = self.voice.to_dict()
        if self.caption:
            data['caption'] = self.caption
        if self.contact:
            data['contact'] = self.contact.to_dict()
        if self.location:
            data['location'] = self.location.to_dict()
        if self.new_chat_participant:
            data['new_chat_participant'] = self.new_chat_participant.to_dict()
        if self.left_chat_participant:
            data['left_chat_participant'] = \
                self.left_chat_participant.to_dict()
        if self.new_chat_title:
            data['new_chat_title'] = self.new_chat_title
        if self.new_chat_photo:
            data['new_chat_photo'] = [p.to_dict() for p in self.new_chat_photo]
        if self.delete_chat_photo:
            data['delete_chat_photo'] = self.delete_chat_photo
        if self.group_chat_created:
            data['group_chat_created'] = self.group_chat_created
        return data

    @staticmethod
    def _totimestamp(dt):
        return int(mktime(dt.timetuple()))
