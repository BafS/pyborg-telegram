
#Changelog.

## Version 0.4.1d: ##
- Bug Fix: Unicode error on Python 3.0 - 3.2 [issue #39](https://github.com/luckydonald/pytg/issues/39), also exported the encoding functions to a sepreate package called ```luckydonaldUtils``` (```pip install luckydonald-utils```).
- Bug Fix: Result_parser method for the chat_add_user command. Thanks @juanprq 
- Bug Fix: Exception on calling sender.contacts_list(). Thanks @vonabarak 

## Version 0.4.1c: ##
- Bug Fix: encoding.to_binary and to_unicode now transform other datatypes (like int) into that type as well.  Fixes [issue #32](https://github.com/luckydonald/pytg/issues/32), and that closes [issue 31](https://github.com/luckydonald/pytg/issues/31)

## Version 0.4.1b: ##
- added ```Receiver.queued_messages()```, showing how many messages are waiting in the queue.

## Version 0.4.1a: ##
- fixed ```Sender``` not working with python 2. ([issue #26](https://github.com/luckydonald/pytg/issues/26), thanks @Meisolsson.)

## Version 0.4.1``` ```:     
**Big rename**:     
```pytg2``` -> ```pytg```    
Thats it.

## Version 0.4.1: ##

for documentation, see:
```python
help(pytg.sender.Sender)
```

- added reply and preview capabilities.    
- added commands.    


## Version 0.4.0: ##
official cli support.
CLI fork not updated? That is a problem of the past!
> It was fun to develop that json bridge by myself though, and It hurts a bit too left that behind :cry:.
> But: I learned a lot about C and git on that journy, and are letting my experience with json flow back into the original cli.
> Everybody will profit from this.

- ```pytg.Telegram```, ```pytg.sender.Sender```, ```pytg.receiver.Receiver``` 
	- sending and receiving now uses the same port.   
		- changed tg.Telegram() parameters: ```port_receive```, ```port_send``` are unified to ```port```:
			```python
			tg.Telegram(port=4458)  # sending and receiving now uses the same port.
			```
	- Sender and Receiver both alter the resulting message dict (versus the json output):
		- ```from``` -> ```sender``` (Reserved word in python)
		- ```to``` -> ```receiver```
		- ```out``` -> ```own``` (out is not intuitive as not mandatory this cli has send the message but the account did.)
		- ```peer``` [added] This is where you most likly want to reply to.
			It will be the group where the message got send, or the user if it is a private message.
		- ~~```print_name```~~ [removed] use "cmd" and "name" instead.
		- + ```cmd``` the unique identifier string which will not change. (exception: secret chats might be replaced by a new one)
		- + ```name``` is a display name. Either the first name or, if not set, the username.
		

- ```pytg.sender.Sender```
	- **all commands** can now raise an exception if the connection (i.e. the connecting) to the cli failed after given number of retries. You should try to restart the cli.
	- **all commands** now have a ```retry_connect=<value>``` parameter (as ```**kwargs```).
		```retry_connect=2``` means 3 tries, first try + 2 retries. This is the *default setting*.
		```retry_connect=0```, ```retry_connect=False``` and ```retry_connect=None``` will not retry,
		```retry_connect=True``` or ```retry_connect= -1``` means to retry infinite times. (this was the default before.)
		```python
		sender.send_msg("luckydonald", "test message", retry_connect= 10
		```
	
	- ```send_photo()```: added optional attribute ```caption``` (string, max length: 140).    
	
	- ```send_video()```: added optional```caption``` parameter (max length: 140).    
		Example:    
		```python
		#send_photo <peer> <file> [caption]
		sender.send_photo(peer, file)
		sender.send_photo(peer, file, caption)
		sender.send_photo("user#1234", "/path/to/image.png")
		sender.send_photo("user#1234", "/path/to/image.png", "This is a image")
		```
