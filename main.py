import sys
import time
import os
import json
import requests
from datetime import datetime, date
import traceback
from dotenv import load_dotenv
from diskcache import Cache
load_dotenv()

def main(argv):
    cache = Cache('./cache')
    host = os.getenv('NODE_HOST')
    remote_host = os.getenv('REMOTE_STATUS_URL')
    auth_token = os.getenv('AUTH_TOKEN')
    block_behind_tolerance = int(os.getenv('BLOCK_BEHIND_TOLERANCE', 4))
    alert_interval = int(os.getenv('ALERT_INTERVAL', 3600))
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if host is None:
        print('NODE_HOST is required')
        sys.exit(1)    
    if remote_host is None:
        print('REMOTE_STATUS_URL is required')
        sys.exit(1)    
    if auth_token is None:
        print('AUTH_TOKEN is required')
        sys.exit(1)    
    if telegram_token is None:
        print('TELEGRAM_TOKEN is required')
        sys.exit(1)    
    if telegram_chat_id is None:
        print('TELEGRAM_CHAT_ID is required')
        sys.exit(1)    

    while True:

        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            block = -1
            explorer_block = -1
            error = None

            # Get the block height from the local node
            payload = {  "id": 1,  "jsonrpc": "2.0",  "method": "header.LocalHead",  "params": []}
            response = requests.post("{}".format(host), json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    block = int(data['result']['header']['height'])
                


            # Get the reference block height from a remote node
            response = requests.get(remote_host)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    explorer_block = int(data['result']['sync_info']['latest_block_height'])
                    
                    

            print(f'Node height {block}, Remote height {explorer_block}')


            error_keys = ['error_no_block_from_node', 'error_no_block_from_remote', 'last_notification_attempt']
            for x in error_keys:
                if x not in cache:
                    cache[x] = 0

            
            # We have a small degree of tolerance for connection/data issues
            if block == -1:
                cache['error_no_block_from_node'] += 1
            else:
                cache['error_no_block_from_node'] = 0
            if explorer_block == -1:
                cache['error_no_block_from_remote'] += 1
            else:
                cache['error_no_block_from_remote'] = 0

            

            if cache['error_no_block_from_node'] > 2:
                error = 'Unable to get block height from node'
            elif cache['error_no_block_from_remote'] > 2:
                error = 'Unable to get block height from remote node'
            elif block != -1 and explorer_block != -1 and (explorer_block - block) > block_behind_tolerance:
                diff = explorer_block - block
                if diff > block_behind_tolerance:
                    error = f'Node is behind remote by {diff} blocks'

            # Send out an alert message if we have an error and are within the alert interval
            if error and (int(time.time()) - cache['last_notification_attempt']) > alert_interval:
                cache['last_notification_attempt'] = int(time.time())
                message = f"Error from Celestia node monitor: '{error}'"
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text={message}"
                requests.get(url)

        except Exception as e: 
            traceback.print_exc()

        time.sleep(60)

if __name__ == "__main__":
    main(sys.argv[1:])