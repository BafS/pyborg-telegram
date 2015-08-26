# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

import json      # parse cli's json
import socket    # connect with cli
import atexit    # shutdown nicely
import inspect   # resultparser exceptions
import logging   # well, logging. Duh.
import threading # so we don't miss messages.
from time import sleep # waiting on reconnect
from collections import OrderedDict # keep the the functions dict in order
from errno import ECONNREFUSED, EINTR # socket errors
from socket import error as socket_error # socket errors

from DictObject import DictObject  # pack the result as object.
from luckydonaldUtils.encoding import to_unicode as u
from luckydonaldUtils.encoding import to_binary as b
from luckydonaldUtils.encoding import to_native as n
from luckydonaldUtils.encoding import text_type, binary_type

from . import result_parser as res
from . import argument_types as args
from .exceptions import UnknownFunction, ConnectionError, NoResponse, IllegalResponseException
from .fix_msg_array import fix_message
from .this_py_version import set_docstring, get_dict_items

logger = logging.getLogger(__name__)

SOCKET_SIZE = 1 << 25

FUNC_CMD  = 0  # cli commands
FUNC_ARGS = 1  # arguments
FUNC_RES  = 2  # return parser
FUNC_TIME = 3  # Timeout
FUNC_DESC = 4  # Description
__all__ = ["Sender"]
functions = OrderedDict()

	# function to call      		# actual telegram command, [required arguments], expected return parser, timeout (None = global default), Description
# messages
# send messages
functions["msg"]				= ("msg", [args.Peer("peer"), args.UnicodeString("test")], res.success_fail, 60.0, "Sends text message to peer")
functions["send_msg"] 			= functions["msg"]
functions["send_text"] 			= functions["msg"]
functions["send_audio"]			= ("send_audio", [args.Peer("peer"), args.File("file")], res.success_fail, 120.0, "")
functions["send_typing"]		= ("send_typing", [args.Peer("peer")], res.success_fail, None, "")
functions["send_typing_abort"]	= ("send_typing_abort", [args.Peer("peer")], res.success_fail, None, "")
functions["send_photo"]			= ("send_photo", [args.Peer("peer"), args.File("file"), args.UnicodeString("caption", optional=True)], res.success_fail, 120.0, "")
functions["send_video"]			= ("send_video", [args.Peer("peer"), args.File("file"), args.UnicodeString("caption", optional=True)], res.success_fail, 120.0, "")
functions["send_document"]		= ("send_document", [args.Peer("peer"), args.File("file")], res.success_fail, 120.0, "")
functions["send_file"] 			= ("send_file", [args.Peer("peer"), args.File("file")], res.success_fail, 120.0, "")
functions["send_location"]		= ("send_location", [args.Peer("peer"), args.Double("latitude"), args.Double("longitude")], res.success_fail, None, "")
functions["send_contact"]		= ("send_contact", [args.Peer("peer"), args.UnicodeString("phone"), args.UnicodeString("first_name"), args.UnicodeString("last_name")], res.something, 60.0, "ret: formated message")
functions["send_text_from_file"]= ("send_text", [args.Peer("peer"), args.File("file")], res.success_fail, 60.0, "")
functions["fwd"]				= ("fwd", [args.Peer("peer"), args.MsgId("msg_id")], res.success_fail, None, "Forwards message to peer. Forward to secret chats is forbidden")
functions["fwd_media"]			= ("fwd_media", [args.Peer("peer"), args.MsgId("msg_id")], res.success_fail, None, "Forwards message media to peer. Forward to secret chats is forbidden. Result slightly differs from fwd")
functions["reply_text"]			= ("reply", [args.MsgId("msg_id"), args.UnicodeString("text")], res.success_fail, None, "Sends text reply to message")
functions["reply_audio"]		= ("reply_audio", [args.MsgId("msg_id"),args.File("file")], res.success_fail, 120.0, "Sends audio to peer")
functions["reply_contact"]		= ("reply_contact", [args.MsgId("msg_id"), args.UnicodeString("phone"), args.UnicodeString("first_name"), args.UnicodeString("last_name")], res.success_fail, 120.0, "Sends contact (not necessary telegram user)")
functions["reply_document"]		= ("reply_document", [args.MsgId("msg_id"), args.File("file")], res.success_fail, None, "Sends document to peer")
functions["reply_file"]			= ("reply_file", [args.MsgId("msg_id"), args.File("file")], res.success_fail, 120.0, "Sends document to peer")
functions["reply_location"]		= ("reply_location", [args.MsgId("msg_id"), args.Double("latitude"), args.Double("longitude")], res.success_fail, None, "Sends geo location")
functions["reply_photo"]		= ("reply_photo", [args.MsgId("msg_id"), args.File("file"), args.UnicodeString("caption", optional=True)], res.success_fail, 120.0, "Sends photo to peer")
functions["reply_video"]		= ("reply_video", [args.MsgId("msg_id"), args.File("file"), args.UnicodeString("caption", optional=True)], res.success_fail, 120.0, "Sends video to peer")
functions["broadcast_text"]		= ("broadcast", [args.User("user", multible=True), args.UnicodeString("text")], res.success_fail, 60.0, "Sends text to several users at once")

# message related
functions["message_delete"]		= ("delete_msg", [args.MsgId("msg_id")], res.success_fail, None, "Deletes message")
functions["message_get"]		= ("get_message", [args.NonNegativeNumber("msg_id")], res.something, None, "Get message by id")
functions["messages_search"]	= ("search", [
												args.Peer("peer", optional=True),
												args.NonNegativeNumber("limit", optional=True),
												args.NonNegativeNumber("from", optional=True),
												args.NonNegativeNumber("to", optional=True),
												args.NonNegativeNumber("offset", optional=True),
												args.UnicodeString("pattern")
											],							res.something, None, "")

# load media
functions["load_audio"]			= ("load_audio", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_chat_photo"]	= ("load_chat_photo", [args.Chat("chat")], res.success_fail, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_file"]			= ("load_file", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_file_thumb"]	= ("load_file_thumb", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_document"]		= ("load_document", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_document_thumb"]= ("load_document_thumb", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_photo"]			= ("load_photo", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_video"]			= ("load_video", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")
functions["load_video_thumb"]	= ("load_video_thumb", [args.MsgId("msg_id")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")

# peer
functions["mark_read"]			= ("mark_read", [args.Peer("peer")], res.success_fail, None, "Marks messages with peer as read")
functions["history"]			= ("history", [args.Peer("user"), args.PositiveNumber("limit", optional=True), args.NonNegativeNumber("offset", optional=True)], res.something, None, "Prints messages with this peer (most recent message lower). Also marks messages as read")


# user
functions["user_info"]			= ("user_info", [args.User("user")], res.something, None, "")
functions["load_user_photo"]	= ("load_user_photo", [args.User("user")], res.something, 120.0, "Downloads file to downloads dirs. Prints file name after download end")

#contacts
functions["contact_add"]		= ("add_contact", [args.UnicodeString("phone"), args.UnicodeString("first_name"), args.UnicodeString("last_name")], res.something, None, "Tries to add user to contact list")
functions["contact_add_by_card"]= ("import_card", [args.UnicodeString("card")], res.success_fail, None, "Gets user by card and prints it name. You can then send messages to him as usual #todo: add args type")
functions["contact_rename"]		= ("rename_contact", [args.User("user"), args.UnicodeString("first_name"), args.UnicodeString("last_name")], res.something, None, "Renames contact #returns the new name")
functions["contact_delete"]		= ("del_contact", [args.User("user")], res.success_fail, None, "Deletes contact from contact list")
functions["contacts_list"]		= ("contact_list", [], res.List(), None, "Prints contact list")
functions["contacts_search"]	= ("contact_search", [args.UnicodeString("user_name"), args.NonNegativeNumber("limit", optional=True)], res.success_fail, None, "Searches contacts by username")

# group chats
functions["chat_info"]			= ("chat_info", [args.Chat("chat")], res.something, None, "Prints info about chat (id, members, admin, etc.)")
functions["chat_set_photo"]		= ("chat_set_photo", [args.Chat("chat"), args.File("file")], res.success_fail, 120,0, "Sets chat photo. Photo will be cropped to square")
functions["chat_add_user"]		= ("chat_add_user", [args.Chat("chat"), args.User("user"), args.NonNegativeNumber("msgs_to_forward", optional=True)], res.success_fail, 60.0, "Adds user to chat. Sends him last msgs-to-forward message from this chat. Default 100")
functions["chat_del_user"]		= ("chat_del_user", [args.Chat("chat"), args.User("user")], res.success_fail, None, "Deletes user from chat")
functions["chat_rename"]		= ("rename_chat", [args.Chat("chat"), args.UnicodeString("new_name")], res.success_fail, None, "Renames chat")
functions["create_group_chat"]	= ("create_group_chat", [args.UnicodeString("name"), args.User("user", multible=True)], res.success_fail, None, "Creates group chat with users")
functions["import_chat_link"]	= ("import_chat_link", [args.UnicodeString("hash")], res.success_fail, None, "Joins to chat by link")
functions["export_chat_link"]	= ("export_chat_link", [args.Chat("chat")], res.success_fail, None, "Prints chat link that can be used to join to chat")

# secret chats
functions["create_secret_chat"]	= ("create_secret_chat", [args.User("user")], res.success_fail, None, "Starts creation of secret chat")
functions["accept_secret_chat"]	= ("accept_secret_chat", [args.SecretChat("secret_chat")], res.success_fail, None, "")
functions["set_ttl"]			= ("set_ttl", [args.NonNegativeNumber("secret_chat")], res.success_fail, None, "Sets secret chat ttl. Client itself ignores ttl")
functions["visualize_key"]		= ("visualize_key", [args.SecretChat("secret_chat")], res.success_fail, None, "Prints visualization of encryption key (first 16 bytes sha1 of it in fact)")

# own profile
functions["set_profile_name"]	= ("set_profile_name", [args.UnicodeString("first_name"), args.UnicodeString("last_name")], res.something, 60.0, "Sets profile name.")
functions["set_username"]		= ("set_username", [args.UnicodeString("name")], res.success_fail, None, "Sets username.")
functions["set_profile_photo"]	= ("set_profile_photo", [args.File("file")], res.something, 120.0, "Sets profile photo. Photo will be cropped to square")
functions["status_online"]		= ("status_online", 		[],																res.success_fail, None, "Sets status as online")
functions["status_offline"]		= ("status_offline", 		[],																res.success_fail, None, "Sets status as offline")
functions["export_card"]		= ("export_card", [], res.success_fail, None, "Prints card that can be imported by another user with import_card method")

# system
functions["quit"]				= ("quit", 				[],																res.response_fails, None, "Quits immediately")
functions["safe_quit"]			= ("safe_quit",	 		[],																res.response_fails, None, "Waits for all queries to end, then quits")
functions["main_session"]		= ("main_session", [], res.success_fail, None, "Sends updates to this connection (or terminal). Useful only with listening socket")
functions["dialog_list"]		= ("dialog_list", [args.NonNegativeNumber("limit", optional=True, default=100), args.NonNegativeNumber("offset", optional=True, default=0)], res.List(), None, "List of last conversations")
functions["set_password"]		= ("set_password", [args.UnicodeString("hint", optional=True, default="empty")], res.success_fail, None, "Sets password")

# diversa
functions["raw"]				= ("", 					[args.UnescapedUnicodeString("command")], res.raw, 120.0, "just send custom shit to the cli. Use, if there are no fitting functions, because I didn't update.")
functions["cli_help"]			= ("help", [], res.raw, None, "Prints the help. (Needed for pytg itself!)")

	# these are commented out in the cli too:

	#//"reply_text": ("reply_text", [args.MsgId("msg_id"), ca_number, ca_file_name_end, ca_none,"<msg-id> <file>"], res.success_fail, None),  # Sends contents of text file as plain text message
	#//"restore_msg": ("restore_msg", [args.MsgId("msg_id"), ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Restores message. Only available shortly (one hour?) after deletion
	#//	functions["secret_chat_rekey"] = ("secret_chat_rekey", [args.SecretChat("secret_chat")], res.success_fail, None, "generate new key for active secret chat"
	#"set": ("set", [ca_string, ca_number, ca_none,"<param> <value>"], res.success_fail, None),  # Sets value of param. Currently available: log_level, debug_verbosity, alarm, msg_num

	#These are not concidered useful, so I implement other things first. If needed, create an issue, or send an pull-request.

	#	functions["show_license"] = ("show_license", [ca_none,""], res.success_fail, None, "Prints contents of GPL license"
	#	functions["stats"] = ("stats", [ca_none,""], res.success_fail, None, "For debug purpose"
	#"view_audio": ("view_audio", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_chat_photo": ("view_chat_photo", [ca_chat, ca_none,"<chat>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_document": ("view_document", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_document_thumb": ("view_document_thumb", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_file": ("view_file", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_file_thumb": ("view_file_thumb", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_photo": ("view_photo", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_user_photo": ("view_user_photo", [ca_user, ca_none,"<user>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_video": ("view_video", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view_video_thumb": ("view_video_thumb", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Downloads file to downloads dirs. Then tries to open it with system default action
	#"view": ("view", [ca_number, ca_none,"<msg-id>"], res.success_fail, None),  # Tries to view message contents

# regex to transform the C function list of the CLI to the one for pytg (in Python, obviously)
##^\s*(?://)?\s*\{"(.*?)", \{\s*((?:ca_(?:[a-z_A-Z]+)(?:(?:,|\s+\|)\s+)?)+)\},\s+[a-z_A-Z]+,\s+"(?:(?:\1\s*(.*?)\\t)?)(.+?)",\s+NULL}(,?)$##
#  replace with:
##\t"$1": ("$1", [$2,"$3"], res.success_fail, None)$5  # $4##
# then
##"([_a-z]+)":\s+\("([_a-z]+)",\s+\[([a-zA-Z\.\(\)=", _]+)\],\s+(res\.\w+),\s+(None|\d+\.\d+)\),(?:\s*#\s*(.*))?##
# with
##\tfunctions["$1"] = ("$2", [$3], $4, $5, "$6"##



_ANSWER_SYNTAX = b("ANSWER ")
_LINE_BREAK = b("\n")


class Sender(object):
	"""
	Provides wrappers for the CLI commands.
	The functions are generated dynamically.
	They can be inspected with the help() command.
	If you need to see their resulting cli command syntax, you can have a look in the `.cli_command` string of the function.
	"""
	_do_quit = False
	default_answer_timeout = 1.0 # how long it should wait for a answer. DANGER: if set to None it will block!

	def __init__(self, host, port):
		"""
		Create a new Sender object. Specify host and port.

		:param host: host ip
		:param port:
		:return:
		"""
		self.s = None
		self.host = host
		self.port_out = port
		self.debug = False
		self._socked_used = threading.Semaphore(1)  # start unblocked.
		atexit.register(self.terminate)

	def execute_function(self, function_name, *arguments, **kwargs):
		"""
		Execute a function.
		Will check a bit, if the parameters looks fitting.
		If you specify retry_connect=int keyword.

		This is wrapped by .execute_function() to support both py3 and py2 syntax.

		:param function_name: The function name.
		:type  function_name: str

		Now you may apply your arguments for that command.

		:keyword reply_id: The message id which this command is a reply to. (will be ignored on non-sending commands)
		:type    reply_id: int or None

		:keyword enable_preview: If the URL found in a message should have a preview. Defaults to False. (Will be ignored by the CLI with non-sending commands)
		:type    enable_preview: bool

		:keyword retry_connect: How often it should try to reconnect (-1 = infinite times) or fail if it can't establish the first connection. (default is 2)
		:type    retry_connect: int

		:return: parsed result/exception
		:rtype: Object or IllegalResponseException

		:raises pytg.exceptions.NoResponse: If the CLI answer command timed out.
		"""
		command_name, new_args = self._validate_input(function_name, arguments)
		reply_id=None
		# python 2 fix
		if "reply_id" in kwargs:
			reply_id = kwargs["reply_id"]
		enable_preview=None
		if "enable_preview" in kwargs:
			enable_preview = kwargs["enable_preview"]
		retry_connect=2
		if "retry_connect" in kwargs:
			retry_connect = kwargs["retry_connect"]

		if self._do_quit and not "quit" in command_name:
			raise AssertionError("Socket already terminated.")
		result_parser = functions[function_name][FUNC_RES]
		result_timeout = functions[function_name][FUNC_TIME]
		try:
			if result_timeout:
				result = self._do_command(command_name, new_args, answer_timeout=result_timeout, retry_connect=retry_connect, enable_preview=enable_preview, reply_id=reply_id)
			else:
				result = self._do_command(command_name, new_args, answer_timeout=self.default_answer_timeout, retry_connect=retry_connect, enable_preview=enable_preview, reply_id=reply_id)
		except ConnectionError as err:
			raise
		except NoResponse as err:
			args_ = inspect.getargspec(result_parser)[0]
			if not "exception" in args_:
				logger.exception("Result parser does not allow exceptions, but we got one: ")
				raise IllegalResponseException("Result parser does not allow exceptions.")
			try:
				return_result = result_parser(exception=err)
				return return_result
			except TypeError:
				logger.error("Result parser did not allow exceptions.")
				raise
		if result_parser != res.raw: # skip json'ing stuff marked as raw output.
			try:
				json_dict = json.loads(result)
				message = DictObject.objectify(json_dict)
				message = fix_message(message)
			except:
				logger.exception("Parsing of answer failed, maybe not valid json?\nMessage: >{}<".format(result))
				#result_parser todo
				return IllegalResponseException("Parsing of answer failed, maybe not valid json?\nMessage: >{}<".format(result))  #TODO: This is *very* bad code.
			return result_parser(message)
		return result_parser(result) # raw()

	@staticmethod
	def _validate_input(function_name, arguments):
		"""
		This will check if the arguments fit the functions needed parameters.
		Returns a tuple of cli command name and the arguments formated as unicode strings.

		:param function_name: The name of the called function.
		:type function_name: str
		:param arguments: given arguments, as a list.
		:type arguments: list of str or tuple of str
		:returns: unicode cli command and a list of unicode parameters.
		:rtype: tuple of (str, list of str)
		"""
		if not function_name in functions:
			raise UnknownFunction(function_name)
		command_name    = functions[function_name][FUNC_CMD]
		arguments_types = functions[function_name][FUNC_ARGS]
		""":type arguments_types: list of pytg.argument_types.Argument"""
		if len(arguments) > len(arguments_types):
			raise ValueError(
				"Error in function {function_name}: {expected_number} paramters expected, but {given_number} were given.".format(
					function_name=function_name, expected_number=len(arguments_types), given_number=len(arguments))
			)
		#end if
		i = 0
		new_args = []
		error = None
		for func_type in arguments_types:
			""":type func_type: pytg.argument_types.Argument"""
			if i >= len(arguments): # if to many arguments
				if not func_type.optional:
					raise ValueError(
						"Error in function {function_name}: Not enough parameter given, {arg_name} missing. Arguments got: {arguments}".format(
							function_name=function_name, arguments=arguments, arg_name=str(func_type))
					)
				else:
					logger.debug("Skipping missing optional parameter #{number} {arg_name} (type {type}) in function {function_name}.".format(
						type=func_type.__class__.__name__, function_name=function_name,  number=i, arg_name=str(func_type))
					)
					continue  # do not increment i, we are still processing the same arg.
				#end if optional
			#end if to many arguments
			arg = arguments[i]
			logger.debug("Parsing {function_name}: Argument {arg} - {type} ({opt})".format(function_name=n(function_name), arg=n(arg), type=func_type, opt=("optional" if hasattr(func_type, "_optional") else "needed")))
			# arg is the given one, which should be func_type.

			arg_value = None
			try:
				arg_value = func_type.parse(arg)
			except Exception as err:
				logger.debug("Got error", exc_info=True)
				if func_type.optional:
					logger.debug("Skipping unfitting optional parameter #{number} {param} (type {type}) in function {function_name}.".format(type=func_type.__class__.__name__, function_name=function_name, param=str(func_type),  number=i))
					continue  # do not increment i, we are still processing the same arg.
				raise ValueError("Error in function {function_name}: parameter #{number} {param} is not type {type}. ({error})".format(
					function_name=function_name, number=i, type=func_type.__class__.__name__, param=str(func_type), error=str(err)))
			new_args.append(u(arg_value))
			i += 1
		return command_name, new_args

	def _do_command(self, cli_command, args, reply_id=None, enable_preview=None, answer_timeout=default_answer_timeout, retry_connect=2):
		"""
		This function will join the cli_command with the given parameters (dynamic *args),
		and execute _do_send(request,**kwargs)

		:keyword reply_id: The message id which this command is a reply to. (will be ignored by the CLI with non-sending commands)
		:type    reply_id: int or None
		:keyword enable_preview: If the URL found in a message should have a preview. (will be ignored by the CLI with non-sending commands)
		:type    enable_preview: bool
		:keyword retry_connect: How often the initial connection should be retried. default: 2. Negative number means infinite.
		:type    retry_connect: int
		"""
		reply_part = ""
		if reply_id:
			if not isinstance(reply_id, int):
				raise AttributeError("reply_id keyword argument is not integer.")
			reply_part = "[reply=%i]" % reply_id
		preview_part = "[enable_preview]" if enable_preview else "[disable_preview]"
		arg_string = " ".join([u(x) for x in args])
		request = " ".join([reply_part, preview_part, cli_command,  arg_string])
		request = "".join([request, "\n"]) #TODO can this be deleted?
		result = self._do_send(request, answer_timeout=answer_timeout, retry_connect=retry_connect)
		return result

	def _do_send(self, command, answer_timeout=default_answer_timeout, retry_connect=2):
		"""
		You can force retry with retry_connect=2 (3 tries, default settings, first try + 2 retries)
		retry_connect=0 , retry_connect=False and retry_connect=None  means not to retry,
		retry_connect=True or retry_connect= -1 means to retry infinite times.

		:type command: builtins.str
		:type answer_timeout: builtins.float or builtins.int
		:param retry_connect: How often the initial connection should be retried. default: 2. Negative number means infinite.
		:type  retry_connect: int
		:return:
		"""
		if isinstance(retry_connect, int):
			pass # correct
		elif isinstance(retry_connect, bool):
			if retry_connect: # True = forever
				retry_connect = -1
			else:
				retry_connect = 0
		elif retry_connect is None:
			retry_connect = 0 # not forever.
		else:
			raise ValueError("retry_connect is not type int, bool or None.")
		retry_connect_original = retry_connect

		if not isinstance(command, (text_type, binary_type)):
			raise TypeError("Command to send is not a unicode(?) string. (Instead of %s you used %s.) " % (str(text_type), str(type(command))))
		logger.debug("Sending command >%s<" % n(command))
		with self._socked_used:
			while not self._do_quit:
				if self.s:
					self.s.close()
					self.s = None
				self.s = socket.socket()
				try:
					self.s.connect((self.host, self.port_out))
				except socket_error as error:
					self.s.close()
					if error.errno == ECONNREFUSED and not self._do_quit:
						if retry_connect != 0:
							sleep(1)
							if retry_connect > 0:
								retry_connect -= 1
							continue
						else:
							raise ConnectionError("Could not establish connection to the cli port, failed after {number} tries. (called with retry_connect={retry_connect})".format(number=(retry_connect_original+1), retry_connect=retry_connect_original))
					raise error  # Not the error we are looking for, re-raise
				except Exception as error:
					self.s.close()
					raise error
				logger.debug("Socket Connected.")
				try:
					self.s.sendall(b(command))
				except Exception as error:
					self.s.close()
					raise error #retry?
				logger.debug("All Sent.")
				completed = -1 # -1 = answer size yet unknown, >0 = got remaining answer size
				buffer = b("")
				self.s.settimeout(answer_timeout) # in seconds.
				while completed != 0:
					try:
						while 1: #retry if CTRL+C'd
							try:
								answer = self.s.recv(1)
								# recv() returns an empty string if the remote end is closed
								if len(answer) == 0:
									raise ConnectionError("Remote end closed")
								break
							except socket_error as err:
								if err.errno != EINTR:
									raise
								else:
									logger.exception("Uncatched exception in reading answer from cli.")
						self.s.settimeout(max(self.default_answer_timeout, answer_timeout)) # in seconds.
						# If there was input the input is now either the default one or the given one, which waits longer.
						buffer += answer
						if completed < -1 and buffer[:len(_ANSWER_SYNTAX)] != _ANSWER_SYNTAX[:len(buffer)]:
							raise ArithmeticError("Server response does not fit.")
						if completed <= -1 and buffer.startswith(_ANSWER_SYNTAX) and buffer.endswith(_LINE_BREAK):
							completed = int(n(buffer[7:-1])) #TODO regex.
							buffer = b("")
						completed -= 1
					except ConnectionError:
						self.s.close()
						raise
					except socket.timeout:
						raise NoResponse(command)
					except KeyboardInterrupt as error:
						logger.exception("Exception while reading the Answer for \"%s\". Got so far: >%s< of %i\n" % (n(command), n(buffer), completed))  # TODO remove me
						self.s.close()
						raise
					except Exception as error:
						logger.exception("Exception while reading the Answer for \"%s\". Got so far: >%s<\n" % (n(command), n(buffer))) #TODO remove me
						self.s.close()
						raise
						#raise error
				# end while completed != 0
				if self.s:
					self.s.close()
					self.s = None
				return u(buffer)
			# end while not self._do_quit
		# end with lock
		if self.s:
			self.s.close()
	# end of function

	def stop(self):
		"""
		Disallow further sending.
		"""
		if self._do_quit:
			logger.debug("Already did quit Sending. Not allowing sending.")
		else:
			logger.info("Quit Sending. Not allowing sending anymore.")
			self._do_quit = True

	def unstop(self):
		"""
		Should reenable sending.
		"""
		if self._do_quit:
			logger.info("Unquit Sending. Allowing sending again.")
			self._do_quit = False
		else:
			logger.debug("Already did unquit Sending. Allowing sending.")
		logger.info("Unquit Sending. Allowing sending again.")

	def terminate(self):
		"""
		Stops the Sender, and abort current requests.
		This may result in loss of data/messages.
		"""
		self.stop()
		logger.warn("Terminating currently sending request.")
		if self._socked_used.acquire(blocking=False):
			# Nothing is going on, just quit then.
			logger.info("Currently not Sending.")
			self._socked_used.release() # someone can use it again.
			return
		else:
			# Something was using the socket for more than 15 seconds.
			logger.warn("Aborting Sending.")
			if self.s:
				#self.s.settimeout(0)
				self.s.close()  # not let the cli end close first -> avoid bind: port already in use.
			return # don't abort sending, let it do stuff, it will suceed or fail soon anyway.
			#	   # Well, hopefully. Else something like this should work:
			#if self.s:
			#	self.s.close()

	@staticmethod
	def help(*args):
		"""
		Display help about a command. Without given arguments this list all dynamic commands.
		"""
		print("Command help:")
		if len(args) == 0:
			for func, doc in get_dict_items(Sender.registered_functions):
				print("| {func}\n|\t{doc}\n|".format(func=func, doc=doc.replace("\n", "\n|\t")))
		for arg in args:
			if isinstance(arg, str):
				if arg in Sender.registered_functions:
					print("| {func}\n|\t{doc}\n|".format(func=arg, doc=Sender.registered_functions[arg].replace("\n", "\n|\t")))


"""
class Sender(object):
	def execute_function(*args, **kwargs):
		print(args, kwargs)
"""  # """ # ignore me, I a sender dummy class for tests, easiable copy-paste-able.


def _register_all_functions():
	"""
	This function registers all the cli functions found in the functions dict to the Sender class.
	This is used to change/add commands easily in the future.
	:return:
	"""
	if hasattr(Sender, "registered_functions"):
		raise AssertionError("Sender class already did register all custom functions.")
	setattr(Sender, "registered_functions", OrderedDict())
	for function, meta in get_dict_items(functions):  # slow in python 2:  http://stackoverflow.com/a/3294899
		def command_alias_wrapper(command_name):
			def command_alias(self,*args, **kwargs):
				return self.execute_function(command_name, *args, **kwargs)
			return command_alias

		arguments = []
		cli_args = []
		args_description = []
		for current_arg in meta[FUNC_ARGS]:
			assert isinstance(current_arg, args.Argument)
			arguments.append(current_arg.name)
			cli_args.append(str(current_arg))
			args_description.append("\t`{arg_name}`: {optional}, needs a {arg_class} (type: {type}), and may {allow_multible} be repeated.".format(
									arg_name=current_arg.name,
									optional="optional" if current_arg.optional else "mandatory",
									arg_class=current_arg.__class__.__name__,
									allow_multible="not" if not current_arg.multible else "",
									type=current_arg.type))
		if len(args_description) == 0:
			argument_description = "\tNo arguments."
		else:
			argument_description = "\n".join(args_description)
		if meta[FUNC_DESC]:
			description = meta[FUNC_DESC] + "\n"
		else:
			description = ""

		docstring = "\n`def {func_name}({arguments})`\n" \
					"{description}\n" \
					"Arguments:\n" \
					"{argument_description}\n" \
					"\n" \
					"Keyword arguments:\n" \
					"\t`reply_id`: optional, the message id (int) which this command is a reply to. Default: None. (Will be ignored by the CLI with non-sending commands.)\n" \
					"\t`enable_preview`: optional, if the URL found in a message should have a preview. Default: False. (Will be ignored by the CLI with non-sending commands.)\n" \
					"\t`retry_connect`: optional, how often the initial connection should be retried. Default: 2. Negative number means infinite.\n" \
					"".format(
			description=description,
			func_name=function,
			arguments=", ".join(arguments),
			argument_description=argument_description)
		Sender.registered_functions[function] = docstring
		command_func = command_alias_wrapper(function)
		set_docstring(command_func, docstring)
		setattr(command_func, "cli_command", meta[FUNC_CMD] + (" " if len(cli_args)>0 else "") + " ".join(cli_args))
		setattr(Sender, function, command_func)
_register_all_functions()
