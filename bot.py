from keep_alive import start
start()

import os
os.system("playwright install")
# check if playright is installed, if not keep trying to install it
while True:
    try:
        from playwright.sync_api import sync_playwright
        break
    except:
        os.system("playwright install")

import interactions
from interactions import *
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext

from characterai import PyCAI
from characterai import PyAsyncCAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

CAiKey = os.getenv("CAIKEY")
char = "YntB_ZeqRq2l_aVf2gWDCZl4oBttQzDvhj9cXafWcF8"

bot_intents: Intents = Intents.MESSAGE_CONTENT | Intents.GUILD_MEMBERS | Intents.GUILDS | Intents.DIRECT_MESSAGES | Intents.MESSAGES | Intents.GUILD_MESSAGES

bot = Client(send_command_tracebacks=False, intents=bot_intents, prefix="AI=")
prefixed_commands.setup(bot)

stopped = False

messages = []

requests = {}

@listen()
async def on_ready():
    global client
    global chat
    await bot.change_presence(
        status=Status.IDLE, activity=Activity(type=ActivityType.WATCHING, name="the chat 🔮")
    )
    client = PyAsyncCAI(CAiKey)
    await client.start()
    chat = await client.chat.get_chat(char)
    print(f"{bot.user} has logged in!")
    while True:
        if messages != []:
            await compose_answer(messages[0])
            messages.remove(messages[0])
        else:
            await asyncio.sleep(1)
        
        if requests != {}:
            for key in requests:
                if requests.get(key)["limit"] == True:
                    await asyncio.sleep(5)
                    requests[key]["limit"] = False



async def respond(message, user):
    participants = chat['participants']

    if not participants[0]['is_human']:
        tgt = participants[0]['user']['username']
    else:
        tgt = participants[1]['user']['username']

    message = f"{user}: {message}"

    print(message)

    data = await client.chat.send_message(chat["external_id"], tgt, message)

    # name = data["src_char"]["participant"]["name"]
    text = data["replies"][0]["text"]

    return text

async def compose_answer(message):
    await message.channel.trigger_typing()
    response = await respond(message.content, message.author.display_name)
    await message.reply(response)

def calc_request(user):
    if requests.get(user.id) == None:
        requests[user.id] = { "messages":1 , "limit":True }
        return True
    else:
        if requests[user.id]["limit"] == False:
            if requests[user.id]["messages"] >= 5:
                return False
            else:
                requests[user.id]["messages"] += 1
                requests[user.id]["limit"] = True
                return True
        elif requests[user.id]["limit"] == True:
            return False

    

@listen()
async def on_message_create(ctx):
    global stopped
    global messages

    if ctx.message.content == "<@1039221480157884496> halt":
        if ctx.message.author == bot.owner:
            stopped = True
            await ctx.message.reply("AI Answering Halted")

    if ctx.message.author.bot:
        return
    if stopped == False:
        if ctx.message.channel.id == 1071105901299241091:
            if calc_request(ctx.message.author):
                messages.append(ctx.message)
                if requests.get(ctx.message.author.id)["messages"] == 1:
                    await asyncio.sleep(60)
                    requests.pop(ctx.message.author.id)
    
            elif requests.get(ctx.message.author.id)["limit"]:
                msg = await ctx.message.reply("You are sending too many messages, please wait a little before sending another one")
                await asyncio.sleep(5)
                await msg.delete()

            else:
                msg = await ctx.message.reply("You are sending too many messages, please wait a minute before sending another one.")
                await asyncio.sleep(5)
                await msg.delete()

        elif ctx.message.channel.type == ChannelType.DM:
            if calc_request(ctx.message.author):
                messages.append(ctx.message)
                if requests.get(ctx.message.author.id)["messages"] == 1:
                    await asyncio.sleep(60)
                    requests.pop(ctx.message.author.id)
    
            elif requests.get(ctx.message.author.id)["limit"]:
                msg = await ctx.message.reply("You are sending too many messages, please wait a little before sending another one")
                await asyncio.sleep(5)
                await msg.delete()

            else:
                msg = await ctx.message.reply("You are sending too many messages, please wait a minute before sending another one.")
                await asyncio.sleep(5)
                await msg.delete()

    if ctx.message.content == "<@1039221480157884496> resume":
        if ctx.message.author == bot.owner:
            stopped = False
            await ctx.message.reply("AI Answering Resumed")

    # await bot.process_commands(ctx)

token = os.environ["TOKEN"]
bot.start(token)