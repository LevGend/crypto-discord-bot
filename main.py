import asyncio
import json

import requests
import discord
from discord.ext import commands,tasks


from dotenv import load_dotenv

# https://coinglass.github.io/API-Reference/#general-info
TOKEN = "***"
FILENAME = "alerts.json"
CHANNEL_ID = 991681642320109629 #trading channel kino's serveur
load_dotenv()

def does_token_exist(symbol):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd"
    response = requests.request("GET", url)
    response = response.json()
    if response[symbol]["usd"] is not None:
        return True
    else:
        return False

def does_alert_exist(symbol,price):
    data = read_file()
    for obj in data:
        if obj['Token'] == symbol and obj['Alert'] == price:
            return True
        else:
            return False


def read_file():
    with open(FILENAME,'r') as file:
        data = json.load(file)
        return data

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

    ### ALERTES ###
                data = read_file()
                for obj in data:
                    if get_price(obj['Token']) == obj['Alert']:
                        channel = bot_discord.bot.get_channel(CHANNEL_ID)
                        await channel.send('⚠️ Le token {} a atteint {}'.format(obj['Token'], obj['Alert']))

    #Ajoute un objet au fichier alerts.json
    @bot.command()
    async def set_alert(message,symbol, price):
        if does_token_exist(symbol):
            if not does_alert_exist(symbol, price):
                data = read_file()
                with open(FILENAME, 'w') as file:
                    jsonData = [{"Token": symbol, "Alert": price}]
                    data.extend(jsonData)
                    file = json.dump(data, file)
            else:
                await message.channel.send("L'alerte pour {} à ${} est déjà active".format(symbol, price))

    #Retire une alerte du fichier alerts.json
    @bot.command()
    async def remove_alert(message,symbol, price):
        if does_alert_exist(symbol, price):
            data = read_file()
            newdata = []
            for obj in data:
                if obj['Token'] == symbol and obj['Alert'] == price:
                    await message.channel.send("{} et {}".format(obj['Token'], obj['Alert']))
                else:
                    newdata.append(obj)
            with open(FILENAME, 'w') as file:
                json.dump(newdata, file)

        else:
            await message.channel.send("L'alerte {} à ${} n'existe pas".format(symbol, price))

    async def alertlist(message):
        data = read_file()
        msg="Il y a {} alertes actives :\n".format(len(data))
        for obj in data:
            msg=("{} à ${}\n".format(obj["Token"], obj["Alert"]))
        await message.channel.send(msg)

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
    bot_discord.bot.run(TOKEN)