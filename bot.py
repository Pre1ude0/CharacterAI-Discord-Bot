import interactions
from interactions import *
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext

from characterai import PyCAI
from characterai import PyAsyncCAI
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

CAiKey = os.getenv("CAIKEY")
char = "YntB_ZeqRq2l_aVf2gWDCZl4oBttQzDvhj9cXafWcF8"

stopped = False

from keep_alive import start


bot_intents: Intents = Intents.MESSAGE_CONTENT | Intents.GUILD_MEMBERS | Intents.GUILDS | Intents.DIRECT_MESSAGES | Intents.MESSAGES | Intents.GUILD_MESSAGES

bot = Client(send_command_tracebacks=False, intents=bot_intents, prefix="AI=")
prefixed_commands.setup(bot)

start()

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


@listen()
async def on_message_create(ctx):
    if ctx.message.author.bot:
        return
    if stopped == False:
        if ctx.message.channel.id == 1071105901299241091:
            await ctx.message.channel.trigger_typing()
            response = await respond(ctx.message.content, ctx.message.author.display_name)
            await ctx.message.channel.send(response)
        elif ctx.message.channel.type == ChannelType.DM:
            await ctx.message.channel.trigger_typing()
            response = await respond(ctx.message.content, ctx.message.author.display_name)
            await ctx.message.channel.send(response)

@prefixed_command(name="stop")
async def stop(ctx: PrefixedContext):
    if ctx.message.author == bot.owner:
        global stopped
        stopped = True
        await ctx.reply("AI Answering Halted")

@prefixed_command(name="start")
async def start(ctx: PrefixedContext):
    if ctx.message.author == bot.owner:
        global stopped
        stopped = False
        await ctx.reply("AI Answering Resumed")

token = os.environ["TOKEN"]
bot.start(token)