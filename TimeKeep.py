import discord
import asyncio
import random
import time
import math
from discord.ext import commands
from DiscordTimeKeep import SecretFile

description = '''An bot designed to get time'''
bot = commands.Bot(command_prefix='t!', description=description)
bot.remove_command("help")


stored_time = 0
latest_clear = 0
cooldown = 43200


async def start_timer():
    global stored_time
    while True:
        await update_time()
        await asyncio.sleep(4.975)


async def update_time():
    flowed_time = int(time.time() - latest_clear)
    time_str = '{}:{}:{}'.format(int(flowed_time / 3600),  # hour
                                 int((flowed_time % 3600) / 60),  # minutes
                                 int(flowed_time % 60))  # seconds
    await bot.change_presence(game=discord.Game(name='{}'.format(time_str)))


@bot.event
async def on_ready():  # when ready it prints the username, id, and starts the status update
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global latest_clear
    latest_clear = time.time()
    await start_timer()


@bot.command(pass_context=True)
async def reap(ctx):
    global latest_clear
    author_id = ctx.message.author.id
    contain = False
    added_time = int(time.time() - latest_clear)

    # database storage
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()
    with open("./data/playerData.txt", "w") as f:
        for line in content:
            if line.startswith(author_id):
                s_line = line.split('|')
                if time.time() < float(s_line[3]):
                    flowed_time = float(s_line[3]) - float(time.time())
                    print(flowed_time)
                    await bot.say('Sorry reaping is still on cooldown\n'
                                  ' please wait another {} hours {} minutes and {} seconds'
                                  ''.format(int(flowed_time / 3600),  # hours
                                            int((flowed_time % 3600) / 60),  # minutes
                                            int(flowed_time % 60)))  # seconds
                    contain = True
                    f.write(line)
                else:
                    await bot.say('<@!{}> has added {} seconds to their total'.format(author_id, added_time))
                    s_line[2] = int(s_line[2]) + added_time
                    s_line[3] = time.time() + cooldown
                    f.write('|'.join(str(x) for x in s_line))
                    contain = True
                    latest_clear = time.time()
            else:
                f.write(line)
        if not contain:
            await bot.say('<@!{}> has added {} seconds to their total'.format(author_id, added_time))
            init = '{}|{}|{}|{}'.format(author_id, ctx.message.author, added_time, time.time() + cooldown)
            print(init)
            f.write(str(init) + '\n')
            latest_clear = time.time()
            await update_time()


@bot.command(pass_context=True)
async def me(ctx):
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()
    for line in content:
        if line.startswith(ctx.message.author.id):
            seconds = float(line.split('|')[2])
            await bot.say('<@!{}> have stored {} seconds\nor {} hours {} minutes and {} seconds'.format(
                ctx.message.author.id, seconds,
                int(seconds / 3600),  # hours
                int((seconds % 3600) / 60),  # minutes
                int(seconds % 60)))  # seconds
            return
    await bot.say('<@!{}> have stored 0 seconds'.format(ctx.message.author.id))


@bot.command(pass_context=True)
async def ping(ctx):
    t = await bot.say('Pong!')
    ms = (t.timestamp - ctx.message.timestamp).total_seconds() * 1000
    await bot.edit_message(t, new_content='Pong! Took: {}ms'.format(int(ms)))


@bot.command(pass_context=True)
async def dev(ctx):
    if not str(ctx.message.author.id) == '297971074518351872':
        await bot.say("Sorry~ this one's only for mango")
        return
    global latest_clear
    latest_clear -= 60
    await bot.say("Dev detected: {}".format("added 60 seconds"))


@bot.command()
async def help():
    embed = discord.Embed()
    embed.title = "available commands: "
    embed.description = "t!start: uh...\n" \
                        "t!reap: reap the time as your own\n" \
                        "t!me: see how much time you reaped\n" \
                        "t!leaderboard: WIP\n"
    await bot.say(embed=embed)


bot.run(SecretFile.get_token())  # are you happy now Soap????
