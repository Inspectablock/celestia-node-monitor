# Celestia Node Monitor

This Python tool will periodically query your Celestia node's block height and compare this against a reference node's height to check 
if your node is falling out of sync. It will also check for basic connectivity to your node's RPC endpoint.

If any errors do occur, the tool will send a message to a predesignated Telegram bot.


## Dependencies

* pip
* pipenv (https://pypi.org/project/pipenv/)


## Authentication Token

You'll need an authentication token from your node to be able to query its RPC endpoint. You can obtain this token by running the following command.

```bash
celestia full auth admin --p2p.network blockspacerace 
```

## Installation and Execution

Copy the example environment config and change the variables with your settings. 

`cp .env.example .env`

Install the required python modules

`pipenv install`

**Ensure that the 'cache' directory is writable by the user running the script.**

Run the tool

`pipenv run python main.py`


## Telegram

To send Telegram messages from this tool you will first need to create a Telegram bot (https://core.telegram.org/bots/tutorial) and then create a chat group and assign the bot as a member.

Once you've done this, you'll need to obtain the Chat Id of the group. You can obtain the chat id by visiting this URL https://api.telegram.org/bot--TOKEN--/getUpdates and looking for the  chat id parameter in the response. Be sure to replace --TOKEN-- with your chatbot token.

```json
{
	"ok": true,
	"result": [{
		"update_id": ....,
		"message": {
			"message_id": .....
			"from": ....
			"chat": {
				"id": -74776,
				........
			},
			"text": "Hello"
		}
	}]
}
```

If you get no content in the response, try sending a message to the group using your standard Telegram client.

## Alerts

There is a config setting (ALERT_INTERVAL) which is used to prevent the tool from spamming your bot with to many alerts. Adjust the value in seconds to suit your preference. 