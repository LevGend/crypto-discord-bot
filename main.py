import asyncio
import csv

import requests
import os
import discord
from discord.ext import commands,tasks
from discord.ext.commands import bot
from typing import Optional


from dotenv import load_dotenv

# https://coinglass.github.io/API-Reference/#general-info
TOKEN = "**********************************************************************"
load_dotenv()

def does_token_exist(symbol):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd"
    response = requests.request("GET", url)
    response = response.json()
    if response[symbol]["usd"] is not None:
        return True
    else:
        return False


def get_price(symbol):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd"
        params = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=params)
        response = response.json()
        price = float(response[symbol]["usd"])
        return float(price)
    except KeyError:
        pass

async def changeActivity(bot):
    while True:
        bot.change_presence(
            activity=discord.Activity(status=discord.Status.idle, activity="Ceci est un test"))
        await asyncio.sleep(30)
        bot.change_presence(
            activity=discord.Activity(status=discord.Status.idle, activity="TEST OK"))

class bot_discord():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(intents=intents,command_prefix='!',description="En developpement..")

    @bot.event
    async def on_ready():
        print("Anders est prêt !")
        ### Faire tourner les crypto présente sur le fichier caroussel ###
        while True:
            with open('caroussel.csv','r') as csvfile:
                data = csvfile.read()
                data = data.split(',')
                for i in data:
                    if i != "":
                        activity = i + " : $" + "{:,.2f}".format(get_price(i))
                        myActivity = discord.Game(name=activity ,type=3)
                        await bot_discord.bot.change_presence(status=discord.Status.idle, activity=myActivity)
                        await asyncio.sleep(10)
                    else:
                        pass

    ### AJOUTE UN TOKEN AU FICHIER TXT ###
    @bot.command()
    async def addtoken(message,symbol,*args):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd"
        response = requests.request("GET", url)
        response = response.json()
        try:
            if response[symbol]["usd"] is not None:
                with open('caroussel.csv','r') as myfile:
                    if myfile.read().find(symbol) == -1:
                        with open('caroussel.csv','a') as csvfile:
                            csvfile.write(str(symbol)+",")
                            await message.channel.send(symbol + " ajouté !")
                    else:
                        await message.channel.send(symbol + " déjà présent")
        except KeyError:
            await message.channel.send(symbol + " non trouvé.")

    ### SUPPRIME UN TOKEN AU FICHIER TXT ###
    @bot.command()
    async def removetoken(message,symbol,*args):
        try:
            if does_token_exist(symbol):
                with open('caroussel.csv','r') as csvfile:
                    data = csvfile.read()
                    data = data.split(',')
                    data.remove(symbol)
                    data = ','.join(data)
                with open('caroussel.csv','w') as csvfile:
                    csvfile.write(data)
                    await message.channel.send(symbol + " retiré")

        except KeyError:
            await message.channel.send(symbol + " Non trouvé : " + KeyError)
            print(KeyError)

    @bot.command()
    async def caroussel(message,*args):
        try:
            token_list = ""
            with open('caroussel.csv','r') as csvfile:
                data = csvfile.read()
                data = data.split(',')
                for i in data:
                    token_list = token_list + " " + i +","
                await message.channel.send("Voici la liste des tokens dans le caroussel : " + token_list)



        except KeyError :
            await message.channel.send(KeyError)

    @bot.command()
    async def exvol(message,*args):
        #TODO
        pass

    @bot.command()
    async def price(message,symbol,*args):
        try :
            #symbol = str.upper(symbol)
            url = "https://api.coingecko.com/api/v3/simple/price?ids="+symbol+"&vs_currencies=usd"
            params = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=params)
            response = response.json()
            await message.channel.send(str(symbol) +" : $"+ str(response[symbol]["usd"]))
        except KeyError:
            await message.channel.send(KeyError)

    @bot.command()
    async def convert(message,amount, symbol, *args):
        #TODO: faire une fonction pour recuperer le prix et réduire avec !price
        try:
            #symbol = str.upper(symbol)
            url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd"
            params = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=params)
            response = response.json()
            price = float(response[symbol]["usd"])
            total = float(amount)*price
            await message.channel.send(str(amount) + " " + str(symbol) + " : $" + str(total))
        except KeyError:
            await message.channel.send(KeyError)


    @bot.command()
    async def lsrate(message,symbol,*args):
        try:
            symbol = str.upper(symbol)
            embed = discord.Embed(title="LONG SHORT RATIO", url="https://www.coinglass.com/LongShortRatio",
                              description=str(symbol)+" Long/Short Ratio")
            embed.set_thumbnail(
                url="https://play-lh.googleusercontent.com/dFDFjZvN8WSc3dn8Ci3EXRavYGSX-zZyWpJkTrocAg6cpndV7P9GWj13_NHYm7NSUaA")
            embed.add_field(name="Time Frame : ", value=long_short_rate("timeframe", symbol), inline=True)
            embed.add_field(name="Short Rate : ", value=long_short_rate("shortsRate", symbol), inline=True)
            embed.add_field(name="Long Rate :", value=long_short_rate("longRate", symbol), inline=True)
            embed.add_field(name="Long/Short Ratio :", value=long_short_rate("longshortRate", symbol), inline=True)
            embed.add_field(name="Symbol :", value=symbol, inline=True)
            await message.channel.send(embed=embed)
        except KeyError :
            await message.channel.send("Je ne connais pas cette crypto 😢")


def long_short_rate(var,symbol):
    timeframe = 2  # (1h=2, 4h=1, 12h=4, 24h=5)
    timeframeDict = {2: "1 heure",
                     1: "4 heures",
                     4: "12 heures",
                     5: "24 heures"}
    url = "https://open-api.coinglass.com/api/pro/v1/futures/longShort_chart?symbol=" + symbol + "&interval=" + str(
        timeframe)
    params = {}
    headers = {
        'coinglassSecret': '178c860751e94b06b248766b0e6f6e4b'
    }
    response = requests.request("GET", url, headers=headers, data=params)
    response = response.json()

    if(var == "timeframe"):
        return timeframeDict[timeframe]
    elif(var == "shortsRate"):
        return response['data']['shortsRateList'][len(response['data']['shortsRateList']) - 1]
    elif(var == "longRate"):
        return response['data']['longRateList'][len(response['data']['longRateList']) - 1]
    elif(var == "longshortRate"):
        return response['data']['longShortRateList'][len(response['data']['longShortRateList']) - 1]

def exchange_volume(symbole):
    #TODO
    url= "https://api.coingecko.com/api/v3/ping"

    response = requests.request("GET", url)
    response = response.json()

def liquidation():
    #TODO
    url = "https://open-api.coinglass.com/api/pro/v1/futures/liquidation_chart?symbol=BTC&exName=Binance"
    params = {}
    headers = {
        'coinglassSecret': '178c860751e94b06b248766b0e6f6e4b'
    }
    response = requests.request("GET", url, headers=headers, data=params)
    response = response.json()

    print(response)


if __name__ == '__main__':
    # long_short_rate()
    #liquidation()
    bot_discord.bot.run(TOKEN)
    #exchange_volume("BTC")
