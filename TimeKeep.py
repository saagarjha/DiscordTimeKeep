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


latest_clear = 0
CD = 43200


async def start_timer():
    while True:
        await update_time_status()
        await asyncio.sleep(4.975)


async def update_time_status():
    flowed_time = int(time.time() - latest_clear)
    time_str = '{}H {}M {}S'.format(int(flowed_time / 3600),  # hour
                                    int((flowed_time % 3600) / 60),  # minutes
                                    int(flowed_time % 60))  # seconds
    await bot.change_presence(game=discord.Game(name='t!: {}'.format(time_str)))


@bot.event
async def on_ready():  # when ready it prints the username, id, and starts the status update
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global latest_clear
    latest_clear = float(get_latest_time())
    # latest_clear = time.time()
    await start_timer()


def get_latest_time():
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()
    return content[0]


@bot.command()
async def start():
    embed = discord.Embed(color=0x42d7f4)
    embed.title = "Welcome~ "
    embed.description = ('Thank you for playing REAPER\n'
                         'in this game I store every single second for you to reap\n'
                         'the amount of time I stored is set as my status\n'
                         'using <t!reap> you will take all the stored time as your own\n'
                         'it will take 12 hours for you to recharge your reap\n'
                         'feel free to @mention me to get the stored time\n'
                         'compete with others to become the TOP REAPER! Good Luck~')
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def reap(ctx):
    global latest_clear
    author_id = ctx.message.author.id
    added_time = int(time.time() - latest_clear)
    # database storage
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()

    contain = False
    updated = False
    for i in range(len(content)):
        line = content[i]
        if line.startswith(author_id):
            s_line = line.split('|')
            if time.time() < float(s_line[3]):
                flowed_time = float(s_line[3]) - float(time.time())
                await bot.say('Sorry reaping is still on cooldown\n'
                              ' please wait another {} hours {} minutes and {} seconds'
                              ''.format(int(flowed_time / 3600),  # hours
                                        int((flowed_time % 3600) / 60),  # minutes
                                        int(flowed_time % 60)))  # seconds
            else:
                await bot.say('<@!{}> has added {} to their total'.format(author_id, seconds_format(added_time)))
                s_line[2] = int(s_line[2]) + added_time
                s_line[3] = time.time() + CD
                content[i] = ('|'.join(str(x) for x in s_line) + '\n')

                j = i - 1
                while j > 0 and int(content[j].split('|')[2]) < s_line[2]:
                    temp = content[j+1]
                    content[j+1] = content[j]
                    content[j] = temp
                    j -= 1
                updated = True
            contain = True
            break
    if not contain:
        await bot.say('<@!{}> has added {} to their total'.format(author_id, seconds_format(added_time)))
        init = '{}|{}|{}|{}'.format(author_id, ctx.message.author, added_time, time.time() + CD)
        content.append(str(init) + '\n')
        j = len(content) - 2
        while j > 0 and int(content[j].split('|')[2]) < added_time:
            temp = content[j + 1]
            content[j + 1] = content[j]
            content[j] = temp
            j -= 1
        updated = True
    if updated:
        latest_clear = time.time()
        content[0] = str(time.time()) + '\n'
        update_logs(str(ctx.message.author)[:-5], seconds_format(added_time))
        await update_time_status()
    with open("./data/playerData.txt", "w") as f:
        f.writelines(content)
    print("reap attempt by {}".format(ctx.message.author))


def update_logs(author, added_time):
    with open("./data/reapLog.txt", "r") as f:
        content = f.readlines()
    info = '{} reaped for {}\n'.format(author, added_time)
    content = [info] + content
    if len(content) > 10:
        content.pop()
    with open("./data/reapLog.txt", "w") as f:
        f.writelines(content)


@bot.command(pass_context=True)
async def me(ctx):
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()
    i = 0
    for line in content:
        if line.startswith(ctx.message.author.id):
            seconds = float(line.split('|')[2])
            if float(line.split('|')[3]) - time.time() > 0:
                next_reap = seconds_format(float(line.split('|')[3]) - time.time())
            else:
                next_reap = 'Your Next Reap is Up'
            await bot.say('<@!{}> have stored {} seconds\n'
                          'or {}\nNext Reap: {}\nRank: {}'
                          ''.format(ctx.message.author.id, seconds, seconds_format(seconds), next_reap, i))
            return
        i += 1
    await bot.say('<@!{}> have stored 0 seconds\nuse t!reap to get started'.format(ctx.message.author.id))


@bot.command(pass_context=True)
async def log(ctx):
    with open("./data/reapLog.txt", "r") as f:
        content = f.readlines()
    log_string = '\n'.join(content)
    embed = discord.Embed(color=0x42d7f4)
    embed.title = "Reap Log"
    embed.description = log_string
    await bot.say(embed=embed)


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
    await bot.say("Dev detected: {}".format("storing extra 60 seconds"))


@bot.command()
async def help():
    help_str = "**t!start:** game description~\n" \
               "**t!reap:** reap the time as your own\n" \
               "**t!me:** see how much time you reaped\n" \
               "**t!leaderboard:** shows who's top 10\n" \
               "**t!log:** shows who recently reaped\n"
    await bot.say(help_str)


def seconds_format(seconds):
    return '{} Hours {} Minutes {} Seconds'.format(
        int(seconds / 3600),  # hours
        int((seconds % 3600) / 60),  # minutes
        int(seconds % 60))  # seconds


@bot.command(pass_context=True)
async def leaderboard(ctx):
    with open("./data/playerData.txt", "r") as f:
        content = f.readlines()
    embed = discord.Embed(color=0x42d7f4)
    embed.title = "Current Top 10 are!~ "
    size = 11
    if len(content) < 11:
        size = len(content)
    for i in range(1, size):
        embed.add_field(name='#{} {}'.format(i, content[i].split('|')[1][:-5]),
                        value=seconds_format(float(content[i].split('|')[2])))
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def invite(ctx):
    embed = discord.Embed(color=0x42d7f4)
    embed.description = \
        "[Invite me~](https://discordapp.com/api/oauth2/authorize?client_id=538078061682229258&permissions=0&scope=bot)"
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def stored(ctx):
    await bot.say('Currently stored {}'.format(seconds_format(int(time.time() - latest_clear))))


@bot.event
async def on_message(message):
    if '538078061682229258' in message.content:
        await bot.send_message(message.channel, 'Currently stored {}'
                               .format(seconds_format(int(time.time() - latest_clear))))
    await bot.process_commands(message)


bot.run(SecretFile.get_token())  # are you happy now Soap????
