import json
import threading
import requests
import httpx
import hashlib
import time
from pypresence import Presence 
from datetime import timedelta
import datetime
import dateutil.parser as dp
from itertools import cycle
import math
import random 
import psutil
import dhooks
import ctypes
import os


os.system('color')

VERSION = 2.3

with open('config.json', 'r+', encoding='utf-8') as cfgfile:
    try:
        config = json.load(cfgfile)
    except:
        print(f'{datetime.datetime.now().time()}: Your config file is in invalid format. Please troubleshoot it using jsonformatter.curiousconcept.com')

try:
    with open("values.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("values.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('{}')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted values.json')

try:
    with open("cooldown.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("cooldown.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('{}')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted cooldown.json')

try:
    with open("cached_inbounds.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("cached_inbounds.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('[]')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted cached_inbounds.json')

with open('proxies.txt','r+', encoding='utf-8') as f:
    ProxyPool = cycle(f.read().splitlines())
  
proxies = []

defaultCookie = {'.ROBLOSECURITY': config['authentication']['cookie']}
selfinventory = []
cachedinventory = []
queue = []

offerblacklist = []
requestblacklist = []

blacklistusers = []

useridtoname = {}
token = []

algorithmqueue = []

outboundsent = []
outboundsentcheck = []

firstInventory = []
secondInventory = []

with open("values.json", "r") as jsonFile:
    values = json.load(jsonFile)

if config['save_cooldown'] == True:
    with open("cooldown.json", "r") as jsonFile:
        cooldown = json.load(jsonFile)
else:
    cooldown = {}

with open("cached_inbounds.json", "r") as jsonFile:
    alreadyinboundchecked = json.load(jsonFile)

try:
    itemdetails = httpx.get("https://www.rolimons.com/itemapi/itemdetails")
except:
    print('Failed to fetch values from rolimons.')
# REMEMBER TO CHANGE

def my_value(number):
    return ("{:,}".format(number))

def firstInventoryCheck():
    global firstInventory
    r = requests.get(f'https://inventory.roblox.com/v1/users/{config["authentication"]["userid"]}/assets/collectibles?sortOrder=Asc&limit=100').json()
    firstInventory = [f"{item['assetId']}:{item['userAssetId']}" for item in r['data']]


def secondInventoryCheck():
    global secondInventory
    r = requests.get(f'https://inventory.roblox.com/v1/users/{config["authentication"]["userid"]}/assets/collectibles?sortOrder=Asc&limit=100').json()
    secondInventory = [f"{item['assetId']}:{item['userAssetId']}" for item in r['data']]

def compareInventories():
    itemLost = [item for item in firstInventory if not item in secondInventory]
    itemGained = [item for item in secondInventory if not item in firstInventory]
    if itemLost != [] and itemGained != []:
        formattedgive = []
        formattedgot = []
        for item in itemLost:
            formattedgive.append(item.split(':')[0])
        for item in itemGained:
            formattedgot.append(item.split(':')[0])
        Webhooks.sendCompleted(formattedgive, formattedgot)
        firstInventoryCheck()

def updateToken():
        getToken = httpx.post('https://auth.roblox.com/v1/logout', cookies={'.ROBLOSECURITY': config['authentication']['cookie']})
        if 'x-csrf-token' in getToken.headers:
            token.clear();token.append(getToken.headers['x-csrf-token'])
            #print(f'{datetime.datetime.now().time()}: Successfully updated token hash ' + Auth.md5(getToken.headers['x-csrf-token']))
            return True
        else:
            print(f'Invalidated cookie returned in updateToken; {getToken.headers}');return False

class Algo:
    def ballgAgo(myInv, harrsingInv):
        combinationsSending = []
        combinationsRecieving = []
        for i in range(1, 5):
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                multiplier = float(totalRecieving / totalSending)

                same = False
                for item in sending:
                    for item2 in recieving:
                        if(item["assetId"] == item2["assetId"]):
                            same = True
                
                if not same:
                    if totalRecieving >= config['valuation']['minimum_trade_value']:
                        if len(sending) == 2 and len(recieving) == 1 or len(sending) == 3 and len(recieving) == 1 or len(sending) == 4 and len(recieving) == 1:
                            if config['trading']['experimental_algorithm']['upgrade']['send_upgrade'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['upgrade']['upgrade_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['upgrade']['upgrade_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "upgrade"}
                        elif len(sending) == 1 and len(recieving) == 1 or len(sending) == 2 and len(recieving) == 2 or len(sending) == 2 and len(recieving) == 3 or len(sending) == 2 and len(recieving) == 4 or len(sending) == 4 and len(recieving) == 2 or len(sending) == 3 and len(recieving) == 2:
                            if config['trading']['experimental_algorithm']['mixed']['send_mixed'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['mixed']['mixed_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['mixed']['mixed_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "mixed"}
                        else:
                            if config['trading']['experimental_algorithm']['downgrade']['send_downgrade'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['downgrade']['downgrade_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['downgrade']['downgrade_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "downgrade"}
        

    def acierhothotAlgo(myInv, harrsingInv, minMultiplier, maxMultiplier):
        combinationsSending = []
        combinationsRecieving = []
        validTrades = []
        for i in range(4):
            i += 1
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                if totalSending == 0 or totalRecieving == 0:
                    print(f'{sending} {totalSending}')
                multiplier = float(totalRecieving / totalSending)
                if(multiplier >= minMultiplier and multiplier <= maxMultiplier):
                    same = False
                    for item in sending:
                        for item2 in recieving:
                            if(item["assetId"] == item2["assetId"]):
                                same = True
                    if not same:
                        return {"sending": sending, "recieving": recieving, "multiplier": multiplier}
        return validTrades
    
    def acieroldalgo(myInv, harrsingInv, minMultiplier, maxMultiplier):
        combinationsSending = []
        combinationsRecieving = []
        validTrades = []
        for i in range(4):
            i += 1
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                if totalSending == 0 or totalRecieving == 0:
                    print(f'{sending} {totalSending}')
                multiplier = float(totalRecieving / totalSending)
                if(multiplier >= minMultiplier and multiplier <= maxMultiplier):
                    same = False
                    for item in sending:
                        for item2 in recieving:
                            if(item["assetId"] == item2["assetId"]):
                                same = True
                    if not same:
                        return {"sending": sending, "recieving": recieving, "multiplier": multiplier}
        
        return validTrades

    def getTotalPrice(inv):
        value = 0
        for asset in inv:
            if asset["value"]:
                value += int(asset["value"])
        return value

    def combinations(inv, n):
        if n == 0:
            return [[]]
        combs = []
        for i in range(0, len(inv)):
            item = inv[i]
            restItems = inv[i+1:]
            for c in Algo.combinations(restItems, n-1):
                combs.append([item] + c)
        return combs

class Cooldown:
    def writenewCooldown(user):
        if str(user) in cooldown:
               cooldown[str(user)] = str(datetime.datetime.now() + timedelta(seconds=config['resend_cooldown']))
        else:
            cooldown[str(user)] = str(datetime.datetime.now() + timedelta(seconds=config['resend_cooldown']))

    def newcooldownOver(user):
        if str(user) in cooldown:
            if datetime.datetime.fromisoformat(cooldown[str(user)]) <= datetime.datetime.now():
                return True
            else:
                return False
        else:
            return True

    def getsavedValue(typec, item):
        if typec == 'offer':
            if Valuation.iscustomOffer(item):
                val = config['custom_values']['custom_offer_values'][str(item)]
                if "+" in val or "-" in val:
                    plus_minus = val[:1]
                    int_val = int(val[1:])
                    if plus_minus == "-":
                        int_val *= -1
                
                    return Valuation.getroliValue(item) + int_val
                return val
        if typec == 'request':
            if Valuation.iscustomRequest(item):
                val = config['custom_values']['custom_request_values'][str(item)]
                if "+" in val or "-" in val:
                    plus_minus = val[:1]
                    int_val = int(val[1:])
                    if plus_minus == "-":
                        int_val *= -1
                
                    return Valuation.getroliValue(item) + int_val
                return val

        if str(item) in values:
            if Cooldown.valuecooldownOver(item) == False:
                if typec == 'offer':
                    return values[str(item)]['offervalue']
                else:
                    return values[str(item)]['requestvalue']
            else:
                Valuation.generateValue(item)
                return Cooldown.getsavedValue(typec, item)
        else:
            Valuation.generateValue(item)
            return Cooldown.getsavedValue(typec, item)

    def valuecooldownOver(item):
        if str(item) in values:
            if datetime.datetime.fromisoformat(values[str(item)]['next_update']) <= datetime.datetime.now():
                return True
            else:
                return False
        else:
            return True
