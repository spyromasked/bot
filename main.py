import os
import io
import json
import time
import random
import asyncio
import discord
import aiohttp
import requests
import threading

from colorama import Fore
from datetime import datetime
from discord.ext import commands

client_id = "1221375404846092351"

gc_delay = 0.1
outlast_cd = 0.1
cooldown_time = 0.00


logs = []
rpc = None
clients = {}
sessions = {}
mimic2 = set()
rpc_thread = None
outlast_tasks = {}
rpc_running = False
user_reactions = {}
targeted_user = None
latest_ron_user = None
custom_auto_replies = {}
locked_group_dms = set()
user_action_cooldown = {}
original_group_members = {}
global_auto_replies = set()
stop_event = asyncio.Event()
global_bully_replies = set()
global_autotype_replies = set()
stop_eventText = asyncio.Event()
stop_eventText2 = asyncio.Event()
stop_eventText4 = asyncio.Event()
first_client_ready = asyncio.Event()

red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
cyan = Fore.CYAN
lightcyan = Fore.LIGHTCYAN_EX
blue = Fore.BLUE
reset = Fore.RESET
grey = Fore.LIGHTBLACK_EX


good_sign = f"{reset}[{green}+{reset}]"
bad_sign = f"{reset}[{red}-{reset}]"
mid_sign = f"{reset}[{yellow}/{reset}]"

logo =f'''{blue}
                        ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░▒▓███████▓▒░ 
                       ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░        
                       ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░        
                       ░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓██████▓▒░  
                       ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          ░▒▓█▓▒░     ░▒▓█▓▒░ 
                       ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          ░▒▓█▓▒░     ░▒▓█▓▒░ 
                       ░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░   ░▒▓█▓▒░   ░▒▓███████▓▒░▒▓███████▓▒░ 
'''

name =rf'''{yellow}
                                                                                     

           ______     _______ _____ 
     /\   |  _ \ \   / / ____/ ____|
    /  \  | |_) \ \_/ / (___| (___  
   / /\ \ |  _ < \   / \___ \\___ \ 
  / ____ \| |_) | | |  ____) |___) |
 /_/    \_\____/  |_| |_____/_____/ 
                                    
                                    

 
   '''

def load_tokens():
    with open("tokens.txt", "r") as file:
        return [line.strip() for line in file if line.strip()]

def load_spam_messages():
    with open("spam.txt", "r") as file:
        return [line.strip() for line in file if line.strip()]

def load_outlasts():
    try:
        with open("outlasts.txt", 'r') as file:
            lines = file.readlines()
            return [line.strip().replace(' ', '\n') for line in lines]
    except Exception as e:
        print(f"Error loading packs: {e}")
        return []

bully_messages = [
"CRY MORE BAFOON ASS SHIT FACE", "saggy breasts ass nigga", "ill bitch u till sunrise", "peon", "u get shoved in lockers", "nigga needs cpr lol", "now what do sum pussy", "ur bmi is over 40", "shut the fuck up", "youre useless and weak", "shit face", "fuck face", "dont tell me a sobstory", "we all know ur past", "failed semen", "punk ass loser", "slow ass fool", " ugly diabetic fuck", "lame ass nigga", "ill lynch you infront of everyone here", "dirty ass nigga" ,"ARE YOU GETTING TIRED?", "giving you ptsd?", "end it all youre useless", "quit fanboying loser", "ugly bastard venting to me", "ur miserable as fuck", "shut the fuck up before i punch you in ur shit", "ill\nrip\nur\nface\noff", "ur too weak to beef me", "give up u can never beat me", "shut the fuck up pathetic piece of shit", "fat bastard", "SORRY ASS NIGGA UR NOT SAFE FROM ME", "DIRTY ASS USELESS BASTARD CANT GET ENOUGH OF THIS ASS WHOPPING", "weak ass nigga ill rip ur jaw out", "# ant brain ass nigga", "ur slow as fuck pussy", "FIGHT BACK WEAKLING", "# or what pedo", "SHUT THE FUCK UP PEDO", "silly ass nigga quit crying bitch", "ill rip ur spine out ur back", "slut loser Ur not on my level", "stop venting to me cuck", "ILL BREAK UR FRAGILE ASS LEGS PUSSY", "just kill urself at this point", "loser ass nigga", "pluto jr? i don't claim u loser", "quit using my dms as therapy loser", "nigga is ass LMFAO", "..", "weak ass lil boy", "ur a bitch fuck nigga", "sup bitch why are u dying","cuck ass nigga" ,"slow ass nigga", "why the fuck are u so weak pussy", "show me ur wrist right now shitty ass faggot", "slow fucking loser", "pedophile dork", "make me stop?", "nigga getting run off by pluto LMAOO", " UR A BITCH", "# nb claims u fucktard"," ur too weak to face me", "id shit on u everyday", "whys this nigga so weak", "watch who u fucking step to", "u actually suck wtf", "quit crying loser", "retarded jr", "# cuck", "slow", "# pedo", "u cut for bitches", "# ðŸ¤¡ðŸ¤¡ðŸ¤¡", "# fuck up queer", "# or what LMFAO", "horrible ass cum gagler shut the fuck up", "wipe those tears off faggot", "ShUT THE FUCK UP Weak ASS PEON", "# lame ass nigga", "yo retard i heard youre a cuck", "broke bitch begging for my attention", "u look up to me", "corny ass jr LMAO", "nigga why are you so ass pedo", "# ur ass out here dying", "pussy boi", "nigga ur a cuck LMFAO", "slow ass pedo", "# ur ass a pedo dont wanna hear it", "ur ass weak fuck", "ur dogshit", "UR WEAK AS FUCK", "weak ass inbred", "u got no motion", "broke ass nigga"
]

press_messages = [
"CRY MORE BAFOON ASS SHIT FACE", "saggy breasts ass nigga", "ill bitch u till sunrise", "peon", "u get shoved in lockers", "nigga needs cpr lol", "now what do sum pussy", "ur bmi is over 40", "shut the fuck up", "youre useless and weak", "shit face", "fuck face", "dont tell me a sobstory", "we all know ur past", "failed semen", "punk ass loser", "slow ass fool", " ugly diabetic fuck", "lame ass nigga", "ill lynch you infront of everyone here", "dirty ass nigga" ,"ARE YOU GETTING TIRED?", "giving you ptsd?", "end it all youre useless", "quit fanboying loser", "ugly bastard venting to me", "ur miserable as fuck", "shut the fuck up before i punch you in ur shit", "ill\nrip\nur\nface\noff", "ur too weak to beef me", "give up u can never beat me", "shut the fuck up pathetic piece of shit", "fat bastard", "SORRY ASS NIGGA UR NOT SAFE FROM ME", "DIRTY ASS USELESS BASTARD CANT GET ENOUGH OF THIS ASS WHOPPING", "weak ass nigga ill rip ur jaw out", "# ant brain ass nigga", "ur slow as fuck pussy", "FIGHT BACK WEAKLING", "# or what pedo", "SHUT THE FUCK UP PEDO", "silly ass nigga quit crying bitch", "ill rip ur spine out ur back", "slut loser Ur not on my level", "stop venting to me cuck", "ILL BREAK UR FRAGILE ASS LEGS PUSSY", "just kill urself at this point", "loser ass nigga", "pluto jr? i don't claim u loser", "quit using my dms as therapy loser", "nigga is ass LMFAO", "..", "weak ass lil boy", "ur a bitch fuck nigga", "sup bitch why are u dying","cuck ass nigga" ,"slow ass nigga", "why the fuck are u so weak pussy", "show me ur wrist right now shitty ass faggot", "slow fucking loser", "pedophile dork", "make me stop?", "nigga getting run off by pluto LMAOO", " UR A BITCH", "# nb claims u fucktard"," ur too weak to face me", "id shit on u everyday", "whys this nigga so weak", "watch who u fucking step to", "u actually suck wtf", "quit crying loser", "retarded jr", "# cuck", "slow", "# pedo", "u cut for bitches", "# ðŸ¤¡ðŸ¤¡ðŸ¤¡", "# fuck up queer", "# or what LMFAO", "horrible ass cum gagler shut the fuck up", "wipe those tears off faggot", "ShUT THE FUCK UP Weak ASS PEON", "# lame ass nigga", "yo retard i heard youre a cuck", "broke bitch begging for my attention", "u look up to me", "corny ass jr LMAO", "nigga why are you so ass pedo", "# ur ass out here dying", "pussy boi", "nigga ur a cuck LMFAO", "slow ass pedo", "# ur ass a pedo dont wanna hear it", "ur ass weak fuck", "ur dogshit", "UR WEAK AS FUCK", "weak ass inbred", "u got no motion", "broke ass nigga"
]

press_messages_sended = [
"CRY MORE BAFOON ASS SHIT FACE", "saggy breasts ass nigga", "ill bitch u till sunrise", "peon", "u get shoved in lockers", "nigga needs cpr lol", "now what do sum pussy", "ur bmi is over 40", "shut the fuck up", "youre useless and weak", "shit face", "fuck face", "dont tell me a sobstory", "we all know ur past", "failed semen", "punk ass loser", "slow ass fool", " ugly diabetic fuck", "lame ass nigga", "ill lynch you infront of everyone here", "dirty ass nigga" ,"ARE YOU GETTING TIRED?", "giving you ptsd?", "end it all youre useless", "quit fanboying loser", "ugly bastard venting to me", "ur miserable as fuck", "shut the fuck up before i punch you in ur shit", "ill\nrip\nur\nface\noff", "ur too weak to beef me", "give up u can never beat me", "shut the fuck up pathetic piece of shit", "fat bastard", "SORRY ASS NIGGA UR NOT SAFE FROM ME", "DIRTY ASS USELESS BASTARD CANT GET ENOUGH OF THIS ASS WHOPPING", "weak ass nigga ill rip ur jaw out", "# ant brain ass nigga", "ur slow as fuck pussy", "FIGHT BACK WEAKLING", "# or what pedo", "SHUT THE FUCK UP PEDO", "silly ass nigga quit crying bitch", "ill rip ur spine out ur back", "slut loser Ur not on my level", "stop venting to me cuck", "ILL BREAK UR FRAGILE ASS LEGS PUSSY", "just kill urself at this point", "loser ass nigga", "pluto jr? i don't claim u loser", "quit using my dms as therapy loser", "nigga is ass LMFAO", "..", "weak ass lil boy", "ur a bitch fuck nigga", "sup bitch why are u dying","cuck ass nigga" ,"slow ass nigga", "why the fuck are u so weak pussy", "show me ur wrist right now shitty ass faggot", "slow fucking loser", "pedophile dork", "make me stop?", "nigga getting run off by pluto LMAOO", " UR A BITCH", "# nb claims u fucktard"," ur too weak to face me", "id shit on u everyday", "whys this nigga so weak", "watch who u fucking step to", "u actually suck wtf", "quit crying loser", "retarded jr", "# cuck", "slow", "# pedo", "u cut for bitches", "# ðŸ¤¡ðŸ¤¡ðŸ¤¡", "# fuck up queer", "# or what LMFAO", "horrible ass cum gagler shut the fuck up", "wipe those tears off faggot", "ShUT THE FUCK UP Weak ASS PEON", "# lame ass nigga", "yo retard i heard youre a cuck", "broke bitch begging for my attention", "u look up to me", "corny ass jr LMAO", "nigga why are you so ass pedo", "# ur ass out here dying", "pussy boi", "nigga ur a cuck LMFAO", "slow ass pedo", "# ur ass a pedo dont wanna hear it", "ur ass weak fuck", "ur dogshit", "UR WEAK AS FUCK", "weak ass inbred", "u got no motion", "broke ass nigga"
]

tokens = load_tokens()

def start_rpc():
    global rpc, rpc_running
    try:
        rpc = Presence(client_id)
        rpc.connect()
        rpc.update(
            large_image="main",
            large_text="amo realm"
        )
        rpc_running = True
    except Exception as e:
        log_action(f"Error starting RPC: {e}")

def stop_rpc():
    global rpc, rpc_running
    try:
        if rpc:
            rpc.close()
            rpc = None
            rpc_running = False
    except Exception as e:
        log_action(f"Error stopping RPC: {e}")

def banner(ascii):
    lines = ascii.split('\n')
    for line in lines:
        print(line)
        time.sleep(0.03)

def log_action(action, channel=None):
    timestamp = datetime.now().strftime('%H:%M:%S')
    location = "N/A"
    if channel:
        if isinstance(channel, discord.DMChannel):
            location = "DM"
        elif isinstance(channel, discord.TextChannel):
            location = f"#{channel.name}"
        elif isinstance(channel, discord.GroupChannel):
            location = "GC"
    log_entry = f"{grey}{timestamp}{reset} - in {yellow}{location}{reset}: {cyan}{action}{reset}"
    logs.append(log_entry)
    print(log_entry)

current_prefix = ">"

async def setup_client(token):
    intents = discord.Intents.all()
    kamo = commands.Bot(command_prefix=lambda bot, msg: current_prefix, self_bot=True, intents=intents)
    clients[token] = kamo

    @kamo.event
    async def on_ready():
        global first_client_ready
        
        if not first_client_ready.is_set():
            os.system("cls")
            print(name)
            first_client_ready.set()
    
        twitch_url = "https://www.twitch.tv/aa"
        stream_name = "̣"
        await kamo.change_presence(activity=discord.Streaming(name=stream_name, url=twitch_url))
        log_action(f"{good_sign} Client Connected To -> {yellow}{kamo.user.name}{reset}")

    kamo.remove_command('help')
    @kamo.command()
    async def help(ctx):
        log_action(f"{good_sign} Executed help command", ctx.channel)
        await ctx.message.delete()
        try:
            help_message = (
                f"```ansi\n"
                f"[2;33m[2;34m[2;31mdeath[0m[2;34m[0m[2;33m[0m[2;41m[2;47m[0m[2;41m[0m"
                f"```"
                f"\n"
                f"```fix\n"
                f"- {current_prefix}h1             - tier Viscount\n"
                f"- {current_prefix}h2             - tier Duke\n"
                f"- {current_prefix}h3             - tier Royality\n"
                f"```"
                f"\n"
                f"```ansi\n"
                f"[2;31m[{kamo.user.name}][0m [2;37m|[0m [2;31m[Royality Client][0m [2;37m|[0m [2;31m[Prefix: {current_prefix} ][0m"
                f"```"
            )
            await ctx.send(help_message, delete_after=10)

        except Exception as k:
            log_action(f"{bad_sign} Error in help command: {k}", ctx.channel)

    @kamo.command()
    async def h1(ctx):
        log_action(f"{good_sign} Executed help command", ctx.channel)
        await ctx.message.delete()
        try:
            help_message = (
                f"```ansi\n"
                f"[2;33m[2;34m[2;31mdeath[0m[2;34m[0m[2;33m[0m[2;41m[2;47m[0m[2;41m[0m"
                f"```"
                f"\n"
                f"```fix\n"
                f"- {current_prefix}ap <user>                  - ap\n"
                f"- {current_prefix}apstop                     - stops ap user\n"
                f"- {current_prefix}ladderap <user>            - ap but ladderd\n"
                f"- {current_prefix}stopladderap               - stops ladderap\n"
                f"- {current_prefix}cd <delay>                 - changes the delay of the aps\n"
                f"- {current_prefix}ar <user> <message>        - sends the message u enter when the ar user talk\n"
                f"- {current_prefix}arstop <user>              - stops ar\n"
                f"- {current_prefix}prefix <prefix>            - changes the prefix\n"
                f"- {current_prefix}stream <title>             - changes the title of all alt tokens\n"
                f"- {current_prefix}mstream <title>            - changes the title of the main token\n"
                f"```"
                f"\n"
                f"```ansi\n"
                f"[2;31m[{kamo.user.name}][0m [2;37m|[0m [2;31m[Royalty Client][0m [2;37m|[0m [2;31m[Prefix: {current_prefix} ][0m"
                f"```"
            )
            await ctx.send(help_message, delete_after=10)

        except Exception as k:
            log_action(f"{bad_sign} Error in help command: {k}", ctx.channel)

    @kamo.command()
    async def h2(ctx):
        log_action(f"{good_sign} Executed help command", ctx.channel)
        await ctx.message.delete()
        try:
            help_message = (
                f"```ansi\n"
                f"[2;33m[2;34m[2;31mdeath[0m[2;34m[0m[2;33m[0m[2;41m[2;47m[0m[2;41m[0m"
                f"```"
                f"\n"
                f"```fix\n"
                f"- {current_prefix}gay <user>                 - gay rate\n"
                f"- {current_prefix}cum <user>                 - cums\n"
                f"- {current_prefix}cuck <user>                - cuck rate\n"
                f"- {current_prefix}seed <user>                - seed rate\n"
                f"- {current_prefix}aura <user>                - aura vault\n"
                f"- {current_prefix}femboy <user>              - femboy rate\n"
                f"- {current_prefix}pp <user>                  - pp length\n"
                f"- {current_prefix}ph <user> <message>        - ph comment\n"
                f"- {current_prefix}jvc <cid>                  - joins vc\n"
                f"- {current_prefix}dvc <cid>                  - leaves vc\n"
                f"- {current_prefix}mute <cid>                 - mutes mic\n"
                f"- {current_prefix}unmute <cid>               - unmutes mic\n"
                f"- {current_prefix}react <user> <emoji> ...   - auto react\n"
                f"- {current_prefix}unreact [user] [emoji] ... - auto react\n"
                f"```"
                f"\n"
                f"```ansi\n"
                f"[2;31m[{kamo.user.name}][0m [2;37m|[0m [2;31m[Royalty Client][0m [2;37m|[0m [2;31m[Prefix: {current_prefix} ][0m"
                f"```"
            )
            await ctx.send(help_message, delete_after=10)

        except Exception as k:
            log_action(f"{bad_sign} Error in help command: {k}", ctx.channel)

    @kamo.command()
    async def h3(ctx):
        log_action(f"{good_sign} Executed help command", ctx.channel)
        await ctx.message.delete()
        try:
            help_message = (
                f"```ansi\n"
                f"[2;33m[2;34m[2;31mdeath[0m[2;34m[0m[2;33m[0m[2;41m[2;47m[0m[2;41m[0m"
                f"```"
                f"\n"
                f"```fix\n"
                f"- {current_prefix}rpc                        - starts RPC\n"
                f"- {current_prefix}rpcoff                     - stops RPC\n"
                f"- {current_prefix}outlast <user>             - starts to outlast an user with all bot accounts\n"
                f"- {current_prefix}stopoutlast <user>         - stops with outlasting an user with all bot accounts\n"
                f"- {current_prefix}ocd                        - cooldown for outlast\n"
                f"- {current_prefix}gc <title>, ...            - gc name changer\n"
                f"- {current_prefix}stopgc                     - stops gc\n"
                f"- {current_prefix}gcd                        - cooldown for gc\n"
                f"- {current_prefix}sound <cid>                - spams a voice channel with a soundboard\n"
                f"- {current_prefix}bully <user>               - auto bullys a user when he types\n"
                f"- {current_prefix}stopbully [user]           - stops auto bully\n"
                f"- {current_prefix}mimic                      - mimics the main client\n"
                f"- {current_prefix}unmimic                    - stops with mimicing the main client\n"
                f"- {current_prefix}lockgc                     - locks a group chat\n"
                f"- {current_prefix}unlockgc                   - unlocks the group chat\n"
                f"- {current_prefix}press <user>               - press an user when they type\n"
                f"- {current_prefix}unpress [user]             - stops pressing an user when they type\n"
                f"```"
                f"\n"
                f"```ansi\n"
                f"[2;31m[{kamo.user.name}][0m [2;37m|[0m [2;31m[Royalty Client][0m [2;37m|[0m [2;31m[Prefix: {current_prefix} ][0m"
                f"```"
            )
            await ctx.send(help_message, delete_after=10)

        except Exception as k:
            log_action(f"{bad_sign} Error in help command: {k}", ctx.channel)

    @kamo.command()
    async def prefix(ctx, new_prefix: str):
        log_action(f"Executed prefix command", ctx.channel)
        await ctx.message.delete()
        global current_prefix
        current_prefix = new_prefix
        sent_message = await ctx.send(f"Command prefix changed to: {new_prefix}")
        log_action(f"{good_sign} Command prefix changed to {new_prefix} by {ctx.author.name}", ctx.channel)
        await asyncio.sleep(5)
        await sent_message.delete()

    @kamo.command()
    async def cd(ctx, seconds: float):
        log_action(f"{good_sign} Executed cd command", ctx.channel)
        global cooldown_time
        await ctx.message.delete()
        cooldown_time = seconds
        await ctx.send(f"Cooldown time set to {cooldown_time} seconds.", delete_after=5)
        log_action(f"Cooldown time set to {cooldown_time} seconds", ctx.channel)

    @kamo.command()
    async def ap(ctx, user: discord.User):
        log_action(f"{good_sign} Executed ap command", ctx.channel)
        global stop_eventText
        stop_eventText.clear()
        channel_id = ctx.channel.id
        user_id = user.id
        await ctx.message.delete()
    
        spam_message_list = load_spam_messages()
        
        tasks = [send_spam_messages(token, channel_id, spam_message_list, user_id) for token in tokens[1:]]
        
        await asyncio.gather(*tasks)

    @kamo.command()
    async def apstop(ctx):
        global stop_eventText
        stop_eventText.set()
        log_action(f"{good_sign} Executed drop command to stop ap command", ctx.channel)
        await ctx.message.delete()
        await ctx.send("Stopped ap command", delete_after=5)

    @kamo.command()
    async def stream(ctx, *, stream_name: str):
        twitch_url = "https://www.twitch.tv/aa"
        tasks = []
        
        main_token = list(clients.keys())[0]

        for token, bot_client in clients.items():
            if token != main_token:
                tasks.append(bot_client.change_presence(activity=discord.Streaming(name=stream_name, url=twitch_url)))

        await asyncio.gather(*tasks)
        
        log_action(f"{good_sign} Alt clients set to streaming: {stream_name}", ctx.channel)
        await ctx.send(f"Alt bots are now streaming: {stream_name}", delete_after=5)
        await ctx.message.delete()

    @kamo.command()
    async def mstream(ctx, *, stream_name: str):
        twitch_url = "https://www.twitch.tv/aa"
        tasks = []
        
        main_token = list(clients.keys())[0]

        for token, bot_client in clients.items():
            if token == main_token:
                tasks.append(bot_client.change_presence(activity=discord.Streaming(name=stream_name, url=twitch_url)))

        await asyncio.gather(*tasks)
        
        log_action(f"{good_sign} Main Client set to streaming: {stream_name}", ctx.channel)
        await ctx.send(f"Main bot is now streaming: {stream_name}", delete_after=5)
        await ctx.message.delete()

    @kamo.command()
    async def rpc(ctx):
        global rpc_thread, rpc_running
        log_action(f"Executed rpc command", ctx.channel)
        await ctx.message.delete()
    
        if rpc_running:
            await ctx.send("RPC is already running!", delete_after=5)
            log_action(f"{good_sign} RPC already running", ctx.channel)
            return
    
        rpc_thread = threading.Thread(target=start_rpc)
        rpc_thread.start()
        await ctx.send("Starting RPC...", delete_after=5)
        log_action(f"{good_sign} RPC started by {ctx.author.name}", ctx.channel)

    
    @kamo.command()
    async def rpcoff(ctx):
        global rpc_running
        log_action(f"{good_sign} Executed rpcoff command", ctx.channel)
        await ctx.message.delete()
    
        if not rpc_running:
            await ctx.send("RPC is not running!", delete_after=5)
            log_action(f"{good_sign} RPC is not running", ctx.channel)
            return
    
        stop_rpc()
        await ctx.send("Stopping RPC...", delete_after=5)
        log_action(f"{good_sign} RPC stopped by {ctx.author.name}", ctx.channel)
     
    @kamo.command()
    async def ar(ctx, user: discord.User, *, text: str):
        await ctx.message.delete()
        global_auto_replies.add(user.id)
        custom_auto_replies[user.id] = text  
        await ctx.send(f"Auto-reply enabled for {user.mention} with custom message: {text}", delete_after=5)
        log_action(f"{good_sign} Auto-reply enabled for {user.name} across all bots with custom message.", ctx.channel)
    
    @kamo.command()
    async def arstop(ctx, user: discord.User):
        await ctx.message.delete()
        if user.id in global_auto_replies:
            global_auto_replies.remove(user.id)
            custom_auto_replies.pop(user.id, None)
            await ctx.send(f"Auto-reply disabled for {user.mention} across all bots.", delete_after=5)
            log_action(f"{good_sign} Auto-reply disabled for {user.name} across all bots.", ctx.channel)
        else:
            await ctx.send(f"Auto-reply was not enabled for {user.mention} across all bots.", delete_after=5)
            log_action(f"{bad_sign} Auto-reply was not enabled for {user.name} across all bots.", ctx.channel)

    @kamo.command()
    async def ladderap(ctx, user: discord.User):
        global stop_eventText4
        stop_eventText4.clear()
        channel_id = ctx.channel.id
        user_id = user.id
        await ctx.message.delete()
    
        spam_message_list = load_spam_messages()
        
        laddered_message_list = ['\n'.join(message.split()) for message in spam_message_list]
        
        tasks = [send_spam_messagesladdder(token, channel_id, laddered_message_list, user_id) for token in tokens[1:]]
        
        await asyncio.gather(*tasks)

    @kamo.command()
    async def stopladderap(ctx):
        global stop_eventText4
        stop_eventText4.set()
        log_action(f"{good_sign} Executed stopladderap command to stop ladderap command", ctx.channel)
        await ctx.message.delete()
        await ctx.send("Stopped ladderap command", delete_after=5)

    @kamo.command()
    async def outlast(ctx, user: discord.User):
        global stop_eventText2
        stop_eventText2.clear()
    

        spam_messages = load_outlasts()
        tokenint = len(tokens)
        current_value = 1
        token_index = 1
        user_id = user.id
    
        await ctx.message.delete()
        log_action(f"{good_sign} Executed outlast command", ctx.channel)
    
        async with aiohttp.ClientSession() as session:
            while not stop_eventText2.is_set():
                current_token = tokens[token_index]
                headers = {"Authorization": f"{current_token}"}
                message = random.choice(spam_messages)
                message_with_all = f"{message} <@{user_id}> \n ```{current_value}```"
                json_data = {"content": message_with_all}
                url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    
                if token_index == 0:
                    log_action(f"{mid_sign} Skipping request for token 1", ctx.channel)
                    token_index = (token_index + 1) % len(tokens)
                    await asyncio.sleep(outlast_cd)
                    continue
    
    
                try:
                    async with session.post(url, json=json_data, headers=headers) as response:
                        if response.status == 200:
                            log_action(f"{good_sign} Sent message with token {token_index + 1}", ctx.channel)
                            current_value += 1
                        elif response.status == 429:
                            log_action(f"{mid_sign} Rate Limited", ctx.channel)
                            await asyncio.sleep(20)
                        else:
                            log_action(f"{bad_sign} Failed: {response.status}", ctx.channel)
    
                except Exception as e:
                    log_action(f"{bad_sign} Error: {e}", ctx.channel)
    
                token_index = (token_index + 1) % len(tokens)
    
                if current_value % tokenint == 1:
                    log_action(f"{good_sign} Sleeping for 10 secs", ctx.channel)
                    await asyncio.sleep(10)
                else:
                    await asyncio.sleep(outlast_cd)

    @kamo.command()
    async def stopoutlast(ctx):
        global stop_eventText2
        stop_eventText2.set()
        await ctx.message.delete()
        log_action(f"{good_sign} Executed stopoutlast command. Stopping spamming.", ctx.channel)
        await ctx.send("Spamming process has been stopped.", delete_after=5)

    @kamo.command()
    async def ocd(ctx, seconds: float):
        log_action(f"Executed ocd command", ctx.channel)
        global outlast_cd
        await ctx.message.delete()
        outlast_cd = seconds
        await ctx.send(f"Cooldown time set to {outlast_cd} seconds.", delete_after=5)
        log_action(f"Cooldown time set to {outlast_cd} seconds", ctx.channel)

    @kamo.command()
    async def gc(ctx, *, names):
        global stop_event
        stop_event.clear()
    
        tokenint = len(tokens)
        current_value = 1
        token_index = 1
    
        sentences = [s.strip() for s in names.split(",")]
    
        await ctx.message.delete()
        log_action(f"{good_sign} Executed gc command with names: {names}", ctx.channel)
    
        if not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.send("This command can only be used in group chats.", delete_after=5)
            return
    
        async with aiohttp.ClientSession() as session:
            while not stop_event.is_set():
                random_name = random.choice(sentences)
                new_name = f"{random_name} | {current_value}"
                current_token = tokens[token_index]
                headers = {"Authorization": f"{current_token}"}
                json_data = {"name": new_name}
                url = f"https://discord.com/api/v10/channels/{ctx.channel.id}"
    
                if token_index == 0:
                    log_action(f"{mid_sign} Skipping request for token 1", ctx.channel)
                    token_index = (token_index + 1) % len(tokens)
                    await asyncio.sleep(gc_delay)
                    continue
    
                try:
                    async with session.patch(url, json=json_data, headers=headers) as response:
                        if response.status == 200:
                            log_action(f"{good_sign} Group renamed to: {new_name} with token {token_index + 1}", ctx.channel)
                            current_value += 1
                        elif response.status == 429:
                            log_action(f"{mid_sign} Rate Limited", ctx.channel)
                            await asyncio.sleep(15)
                        else:
                            log_action(f"{bad_sign} Failed: {response.status}", ctx.channel)
    
                except Exception as e:
                    log_action(f"{bad_sign} Error: {e}", ctx.channel)
    
                token_index = (token_index + 1) % len(tokens)
    
                if current_value % tokenint == 1:
                    log_action(f"{good_sign} Sleeping for 5 secs", ctx.channel)
                    await asyncio.sleep(5)
                else:
                    await asyncio.sleep(gc_delay)

    @kamo.command()
    async def stopgc(ctx):
        global stop_event
        stop_event.set()
        await ctx.message.delete()
        log_action(f"{good_sign} Executed stopgc command. Stopping renaming.", ctx.channel)
        await ctx.send("Renaming process has been stopped.", delete_after=5)

    @kamo.command()
    async def gcd(ctx, seconds: float):
        log_action(f"Executed gcd command", ctx.channel)
        global gc_delay
        await ctx.message.delete()
        gc_delay = seconds
        await ctx.send(f"Cooldown time set to {gc_delay} seconds.", delete_after=5)
        log_action(f"Cooldown time set to {gc_delay} seconds", ctx.channel)

    @kamo.command()
    async def gay(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed gay command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% gay!")

    @kamo.command()
    async def cum(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed cum command.", ctx.channel)
        await ctx.send(f"{user.mention}, cum.")

    @kamo.command()
    async def cuck(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed cuck command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% cuck!")

    @kamo.command()
    async def seed(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed seed command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% my seed!")

    @kamo.command()
    async def aura(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed aura command.", ctx.channel)
        aura_value = random.randint(1, 10000)
        await ctx.send(f"{user.mention} has {aura_value} aura!")

    @kamo.command()
    async def femboy(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed femboy command.", ctx.channel)
        percentage = random.randint(1, 100)
        await ctx.send(f"{user.mention} is {percentage}% femboy!")

    @kamo.command()
    async def pp(ctx, user: discord.User):
        await ctx.message.delete()
        log_action(f"Executed pp command.", ctx.channel)
        if user == kamo.user:
            pp_length = "=" * random.randint(15, 20)
        else:
            pp_length = "=" * random.randint(3, 15)
        await ctx.send(f"{user.mention} pp results = 8{pp_length}>")

    @kamo.command()
    async def react(ctx, user: discord.User, *emojis):
        await ctx.message.delete()
    
        user_id = user.id
        global latest_ron_user
        latest_ron_user = user
    
        if user_id not in user_reactions:
            user_reactions[user_id] = list(emojis)
        else:
            user_reactions[user_id].extend(emojis)
    
        emoji_list = ' '.join(emojis)
        await ctx.send(f"Reactions {emoji_list} added for {user.name}.", delete_after=5)
        log_action(f"Added auto-reactions {emoji_list} for {blue}{user.name}{cyan}.", ctx.channel)

    @kamo.command()
    async def unreact(ctx, user: discord.User = None, *emojis):
        await ctx.message.delete()
        
        global latest_ron_user
        if user is None:
            user = latest_ron_user

        if user is None:
            await ctx.send(f"No previous user from 'ron' to clear.", delete_after=5)
            return

        user_id = user.id
        if user_id in user_reactions:
            if emojis:
                for emoji in emojis:
                    if emoji in user_reactions[user_id]:
                        user_reactions[user_id].remove(emoji)
                emoji_list = ' '.join(emojis)
                await ctx.send(f"Reactions {emoji_list} removed for {user.name}.", delete_after=5)
                log_action(f"Removed auto-reactions {emoji_list} for {blue}{user.name}{cyan}.", ctx.channel)
            else:
                user_reactions.pop(user_id)
                await ctx.send(f"All auto-reactions cleared for {user.name}.", delete_after=5)
                log_action(f"Cleared all auto-reactions for {blue}{user.name}{cyan}.", ctx.channel)
        else:
            await ctx.send(f"No reactions found for {user.name}.", delete_after=5)

    @kamo.command()
    async def purge(ctx, amount: int):
        await ctx.message.delete()
        log_action(f"{good_sign} Executed purge command.")
        try:
            async for message in ctx.channel.history(limit=amount):
                if message.author == ctx.author:
                    await message.delete()
    
            log_action(f"{good_sign} Deleted {amount} messages by {ctx.author}.", ctx.channel)
            await ctx.send(f"Deleted {amount} messages.", delete_after=5)
        except Exception as e:
            log_action(f"{bad_sign} Error in >c command: {e}", ctx.channel)
            await ctx.send(f"An error occurred: {e}", delete_after=5)

    @kamo.command()
    async def ph(ctx, user: discord.User, *, text: str):
        log_action(f"{good_sign} Executed ph command.")
        
        await ctx.message.delete()
        
        try:
            avatar_url = user.avatar_url_as(format="png")
            
            endpoint = f"https://nekobot.xyz/api/imagegen?type=phcomment&text={text}&username={user.name}&image={avatar_url}"
            r = requests.get(endpoint)
            res = r.json()
    
            if res["success"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(res["message"]) as resp:
                        image = await resp.read()
    
                with io.BytesIO(image) as file:
                    await ctx.send(file=discord.File(file, f"{user.name}_pornhub_comment.png"))
                log_action(f"Pornhub comment image generated for {user.name}")
    
            else:
                await ctx.send(f"Failed to generate image. Try again later.")
                log_action(f"Failed to generate image for {user.name}")
        
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            log_action(f"An error occurred during phcomment command: {str(e)}")

    @kamo.command()
    async def jvc(ctx, channel_id: str):
        guild_id = ctx.guild.id
        log_action(f"Executed ovc command to join voice channel", ctx.channel)
        await ctx.message.delete()
        log_action(f"Joining {len(tokens)} tokens to voice channel {channel_id} in guild {guild_id}", ctx.channel)
        tasks = [voice_channel_join(token, guild_id, channel_id) for token in tokens[1:]]
        await asyncio.gather(*tasks)
        await ctx.send(f"All tokens are joining voice channel {channel_id} in guild {guild_id}.", delete_after=5)

    @kamo.command()
    async def dvc(ctx, channel_id: str):
        guild_id = ctx.guild.id
        log_action(f"Executed dcv command to leave voice channel", ctx.channel)
        await ctx.message.delete()
        
        if not sessions:
            await ctx.send("No tokens are currently in a voice channel.", delete_after=5)
            return
    
        tasks = [voice_channel_leave(token, guild_id, channel_id) for token in tokens[1:]]
        await asyncio.gather(*tasks)
        
        await ctx.send(f"All tokens are leaving voice channels in guild {guild_id}.", delete_after=5)

    @kamo.command()
    async def mute(ctx, channel_id: str):
        guild_id = ctx.guild.id
        log_action(f"Executed mute command", ctx.channel)
        await ctx.message.delete()

        if not sessions:
            await ctx.send("No tokens are in a voice channel to mute.", delete_after=5)
            return

        tasks = [update_voice_state(token, guild_id, channel_id, True) for token in tokens[1:]]
        await asyncio.gather(*tasks)
        await ctx.send(f"All tokens muted in voice channel {channel_id} in guild {guild_id}.", delete_after=5)

    @kamo.command()
    async def unmute(ctx, channel_id: str):
        guild_id = ctx.guild.id
        log_action(f"Executed unmute command", ctx.channel)
        await ctx.message.delete()

        if not sessions:
            await ctx.send("No tokens are in a voice channel to unmute.", delete_after=5)
            return

        tasks = [update_voice_state(token, guild_id, channel_id, False) for token in tokens[1:]]
        await asyncio.gather(*tasks)
        await ctx.send(f"All tokens unmuted in voice channel {channel_id} in guild {guild_id}.", delete_after=5)

    @kamo.command()
    async def sound(ctx, channel_id: str):
        await ctx.message.delete()
        log_action(f"Executed sound command to spam soundboards", ctx.channel)
        max_threads = len(tokens)
        
        token = random.choice(tokens).strip()
        headers = {"Authorization": token}
        response = requests.get("https://discord.com/api/v9/soundboard-default-sounds", headers=headers)
        
        if response.status_code == 200:
            sounds = response.json()
        else:
            await ctx.send(f"Failed to fetch soundboard sounds: {response.status_code}", delete_after=5)
            return
        
        threads = []
        for _ in range(max_threads):
            token = random.choice(tokens).strip()
            thread = threading.Thread(target=send, args=(channel_id, sounds, token))
            threads.append(thread)
            thread.start()
        
        await ctx.send(f"Soundboard spammer started with {max_threads} threads in channel {channel_id}.", delete_after=5)
        
        for thread in threads:
            thread.join()
    
        await ctx.send("Soundboard spammer stopped after 50 requests per token.", delete_after=5)

    @kamo.command()
    async def bully(ctx, user: discord.User):
        await ctx.message.delete()
        global_bully_replies.add(user.id)
        await ctx.send(f"Auto-bully enabled for {user.mention}", delete_after=5)
        log_action(f"{good_sign} Auto-bully enabled for {user.name} across all bots", ctx.channel)
    
    @kamo.command()
    async def stopbully(ctx, user: discord.User = None):
        await ctx.message.delete()
    
        if user:
            if user.id in global_bully_replies:
                global_bully_replies.remove(user.id)
                await ctx.send(f"Auto-bully disabled for {user.mention}.", delete_after=5)
                log_action(f"{good_sign} Auto-bully disabled for {user.name} across all bots.", ctx.channel)
            else:
                await ctx.send(f"Auto-bully was not enabled for {user.mention}.", delete_after=5)
                log_action(f"{bad_sign} Auto-bully was not enabled for {user.name}.", ctx.channel)
        else:
            global_bully_replies.clear()
            await ctx.send(f"Auto-bully disabled for all users.", delete_after=5)
            log_action(f"{good_sign} Auto-bully disabled for all users.", ctx.channel)

    @kamo.command()
    async def mimic(ctx):
        mimic2.add(ctx.author.id)
        log_action(f"{good_sign} Mimic mode enabled for {ctx.author.name}", ctx.channel)
        await ctx.message.delete() 

    @kamo.command()
    async def unmimic(ctx):
        if ctx.author.id in mimic2:
            mimic2.remove(ctx.author.id)
            log_action(f"{good_sign} Mimic mode disabled for {ctx.author.name}", ctx.channel)
            await ctx.message.delete()
        else:
            log_action(f"{mid_sign} Mimic mode was not active for {ctx.author.name}", ctx.channel)

    async def mimic_message(client_instance, message_content, channel_id, message_channel):
        try:
            channel = client_instance.get_channel(channel_id)
            
            if isinstance(channel, discord.DMChannel):
                await channel.send(message_content)
                log_action(f"{good_sign} {client_instance.user.name} mimicked message in DM: {message_content}", message_channel)
            elif isinstance(channel, discord.GroupChannel):
                await channel.send(message_content)
                log_action(f"{good_sign} {client_instance.user.name} mimicked message in Group Chat: {message_content}", message_channel)
            else:
                if channel.permissions_for(channel.guild.me).send_messages:
                    await channel.send(message_content)
                    log_action(f"{good_sign} {client_instance.user.name} mimicked message: {message_content}", message_channel)
                else:
                    log_action(f"{bad_sign} Missing permissions to send message in {channel.name}", message_channel)
        except discord.Forbidden as e:
            log_action(f"{bad_sign} Forbidden error with {client_instance.user.name}: {e}", message_channel)
        except discord.HTTPException as e:
            log_action(f"{bad_sign} HTTPException with {client_instance.user.name}: {e}", message_channel)
        except Exception as e:
            log_action(f"{bad_sign} Unexpected error with {client_instance.user.name}: {e}", message_channel)


    @kamo.command()
    async def lockgc(ctx):
        await ctx.message.delete() 
        if isinstance(ctx.channel, discord.GroupChannel):
            locked_group_dms.add(ctx.channel.id)
            original_group_members[ctx.channel.id] = {member.id for member in ctx.channel.recipients}
            await ctx.send(f"Group chat is now locked and original members are stored.", delete_after=5)
            log_action(f"{good_sign} lockgc enabled", ctx.channel)
        else:
            await ctx.send("This command can only be used in group chats.", delete_after=5)
            log_action(f"{bad_sign} can only be used in a group chat", ctx.channel)
    
    @kamo.command()
    async def unlockgc(ctx):
        await ctx.message.delete() 
        if isinstance(ctx.channel, discord.GroupChannel):
            if ctx.channel.id in locked_group_dms:
                locked_group_dms.remove(ctx.channel.id)
                original_group_members.pop(ctx.channel.id, None)
                await ctx.send(f"Group chat {ctx.channel.id} is now unlocked.", delete_after=5)
                log_action(f"{good_sign} unlocked groupchat enabled", ctx.channel)
            else:
                await ctx.send("This group chat is not locked.", delete_after=5)
                log_action(f"{mid_sign} this group chat was not locked", ctx.channel)
        else:
            await ctx.send("This command can only be used in group chats.", delete_after=5)
            log_action(f"{bad_sign} can only be used in a group chat", ctx.channel)

    @kamo.command()
    async def press(ctx, user: discord.User):
        await ctx.message.delete()
        global_autotype_replies.add(user.id)
        await ctx.send(f"Auto-press enabled for {user.mention}", delete_after=5)
        log_action(f"{good_sign} Auto-press enabled for {user.name} across all bots", ctx.channel)
    
    @kamo.command()
    async def unpress(ctx, user: discord.User = None):
        await ctx.message.delete()
    
        if user:
            if user.id in global_autotype_replies:
                global_autotype_replies.remove(user.id)
                await ctx.send(f"Auto-press disabled for {user.mention}.", delete_after=5)
                log_action(f"{good_sign} Auto-press disabled for {user.name} across all bots.", ctx.channel)
            else:
                await ctx.send(f"Auto-press was not enabled for {user.mention}.", delete_after=5)
                log_action(f"{bad_sign} Auto-press was not enabled for {user.name}.", ctx.channel)
        else:
            global_autotype_replies.clear()
            await ctx.send(f"Auto-press disabled for all users.", delete_after=5)
            log_action(f"{good_sign} Auto-press disabled for all users.", ctx.channel)

    @kamo.event
    async def on_group_remove(channel, user):
        if channel.id in locked_group_dms:
            if user.id not in original_group_members.get(channel.id, set()) and user_action_cooldown.get((channel.id, user.id)) is None:
                await add_member_to_channel(user.id, channel.id, token)
                await channel.send(f"{user.name} was readded because this group is in lockdown")
                user_action_cooldown[(channel.id, user.id)] = 'readded'
    
                await asyncio.sleep(5)
                del user_action_cooldown[(channel.id, user.id)]
    
    @kamo.event
    async def on_group_join(channel, user):
        if channel.id in locked_group_dms:
            if user.id not in original_group_members.get(channel.id, set()) and user_action_cooldown.get((channel.id, user.id)) is None:
                await remove_user_from_channel(user.id, channel.id, token)
                await channel.send(f"{user.name} was removed because this group is in lockdown")
                user_action_cooldown[(channel.id, user.id)] = 'removed'
    
                await asyncio.sleep(5)
                del user_action_cooldown[(channel.id, user.id)]


    @kamo.event
    async def on_message(message):
        main_token = list(clients.keys())[0]

        if message.author.id in user_reactions:
            emojis = user_reactions[message.author.id]
            for emoji in emojis:
                try:
                    await message.add_reaction(emoji)
                    log_action(f"Reacted to {blue}{message.author.name}'s{cyan} message with {emoji}", message.channel)
                except discord.HTTPException as e:
                    log_action(f"Failed to add reaction {emoji}: {e}", message.channel)
    
        elif token != main_token:
            if message.author.id in global_auto_replies:
                try:
                    if message.author.id in custom_auto_replies:
                        reply_message = custom_auto_replies[message.author.id]
                    await message.reply(f"{reply_message} {message.author.mention}")
                    log_action(f"{good_sign} Global auto-replied to {message.author.name}", message.channel)
                except Exception as e:
                    log_action(f"{bad_sign} Error in global auto-reply: {e}", message.channel)

            elif message.author.id in global_autotype_replies:
                reply = random.choice(press_messages_sended)
                await message.reply(f"{reply}")

        elif message.author.id in mimic2 and not message.content.startswith(current_prefix):
            if message.content.strip():
                tasks = [
                    mimic_message(client_instance, message.content, message.channel.id, message.channel)
                    for client_token, client_instance in clients.items()
                    if client_token != token
                ]
                
                await asyncio.gather(*tasks)
            else:
                log_action(f"{mid_sign} Skipped mimicking an empty message from {message.author.name}", message.channel)   


        await kamo.process_commands(message)

    @kamo.event
    async def on_typing(channel, user, when):
        main_token = list(clients.keys())[0]

        if token != main_token:

            if user.id in global_bully_replies:
                asyncio.create_task(send_bully_message(user, channel))

            elif user.id in global_autotype_replies:
                reply = random.choice(press_messages)
                await channel.send(f"{reply} <@{user.id}>")
            
    try:
        await kamo.start(token, bot=False)
    except discord.errors.LoginFailure:
        log_action(f"{bad_sign} Login failed for token: {blue}{token[:-20]}{reset}. Skipping to the next token.")
        del clients[token]

async def remove_user_from_channel(user_id, channel_id, token):
    url = f"https://discord.com/api/v9/channels/{channel_id}/recipients/{user_id}"
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        log_action(f"Successfully removed user from channel {channel_id}.")
    else:
        log_action(f"Failed to remove user from channel {channel_id}.")

async def add_member_to_channel(user_id, channel_id, token):
    url = f"https://discord.com/api/v9/channels/{channel_id}/recipients/{user_id}"
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        log_action(f"Successfully readded user to channel {channel_id}.")
    else:
        log_action(f"Failed to readd user to channel {channel_id}.")

async def send_bully_message(user, channel):
    while user.id in global_bully_replies:
        selected_message = random.choice(bully_messages)
        laddered = random.choice([True, False])
        tag_user = random.choice([True, False])

        if laddered:
            laddered_message = "\n".join(selected_message.split())
        else:
            laddered_message = selected_message

        formatted_message = f"{laddered_message} {user.mention}" if tag_user else laddered_message

        try:
            async with channel.typing():
                typing_duration = random.uniform(1, 3)
                await asyncio.sleep(typing_duration)

            await channel.send(formatted_message)
            log_action(f"{good_sign} Sent bully message to {user.name}", channel)
        except Exception as e:
            log_action(f"{bad_sign} Error in sending bully message: {e}", channel)

        await asyncio.sleep(random.uniform(2, 5))

async def send_spam_messages(token, channel_id, spam_message_list, user_id):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        log_action(f"Sending messages to channel {channel_id} with token {token[:10]}...")

        while not stop_eventText.is_set(): 
            try:
                while not stop_eventText.is_set():
                    spam_message = random.choice(spam_message_list)
                    message_with_mention = f"{spam_message} <@{user_id}>"
                    json_data = {"content": message_with_mention}

                    try:
                        async with session.post(
                            url, headers=headers, json=json_data
                        ) as response:
                            await handle_response(response)

                    except Exception as e:
                        log_action(f"An error occurred during sending: {e}")

                    await asyncio.sleep(cooldown_time)

            except Exception as e:
                log_action(f"An error occurred in the loop: {e}")
                await asyncio.sleep(1)

async def send_spam_messagesladdder(token, channel_id, spam_message_list, user_id):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        log_action(f"Sending messages to channel {channel_id} with token {token[:10]}...")

        while not stop_eventText4.is_set(): 
            try:
                while not stop_eventText4.is_set():
                    spam_message = random.choice(spam_message_list)
                    message_with_mention = f"{spam_message} <@{user_id}>"
                    json_data = {"content": message_with_mention}

                    try:
                        async with session.post(
                            url, headers=headers, json=json_data
                        ) as response:
                            await handle_response(response)

                    except Exception as e:
                        log_action(f"An error occurred during sending: {e}")

                    await asyncio.sleep(cooldown_time)

            except Exception as e:
                log_action(f"An error occurred in the loop: {e}")
                await asyncio.sleep(1)

            
async def handle_response(response):
    if response.status == 200:
        log_action("Message sent successfully.")
    elif response.status == 429:
        log_action("Rate limited. Retrying after 10 seconds...")
        await asyncio.sleep(10)
    else:
        log_action(f"Failed to send message. Status: {response.status}")

async def heartbeat(ws, interval):
    try:
        while True:
            await asyncio.sleep(interval)
            await ws.send(json.dumps({"op": 1, "d": None}))
    except websockets.ConnectionClosed:
        log_action("Connection closed, stopping heartbeat.")
        return

async def voice_channel_join(token, guild_id, channel_id):
    session_id = None
    async with websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json', max_size=None) as ws:
        response = await ws.recv()
        response = json.loads(response)

        heartbeat_interval = response['d']['heartbeat_interval'] / 1000
        asyncio.create_task(heartbeat(ws, heartbeat_interval))

        payload = {
            "op": 2,
            "d": {
                "token": token,
                "intents": 513,
                "properties": {
                    "$os": "linux",
                    "$browser": "disco",
                    "$device": "disco"
                }
            }
        }
        await ws.send(json.dumps(payload))

        while True:
            response = await ws.recv()
            response = json.loads(response)
            if response['t'] == 'READY':
                session_id = response['d']['session_id']
                break

        sessions[token] = {
            "session_id": session_id,
            "guild_id": guild_id,
            "channel_id": channel_id
        }

        voice_state_update = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": False,
                "self_deaf": False
            }
        }
        await ws.send(json.dumps(voice_state_update))

        while True:
            try:
                response = await ws.recv()
                response = json.loads(response)
                if response['t'] == 'VOICE_STATE_UPDATE' and response['d']['channel_id'] == channel_id:
                    voice_server_update = {
                        "op": 4,
                        "d": {
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "self_mute": False,
                            "self_deaf": False
                        }
                    }
                    await ws.send(json.dumps(voice_server_update))

            except websockets.ConnectionClosedError:
                log_action("WebSocket disconnected. Attempting to reconnect...")
                await reconnect_voice_channel(ws, token, guild_id, channel_id, session_id)

async def reconnect_voice_channel(ws, token, guild_id, channel_id, session_id):
    async with websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json', max_size=None) as ws:
        payload = {
            "op": 6,
            "d": {
                "token": token,
                "session_id": session_id,
                "seq": None
            }
        }
        await ws.send(json.dumps(payload))

        voice_state_update = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": False,
                "self_deaf": False
            }
        }
        await ws.send(json.dumps(voice_state_update))

        log_action(f"Reconnected to voice channel {channel_id} in guild {guild_id}.")

async def voice_channel_leave(token, guild_id, channel_id):
    try:
        async with websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json', max_size=None) as ws:
            response = await ws.recv()
            response = json.loads(response)

            heartbeat_interval = response['d']['heartbeat_interval'] / 1000
            asyncio.create_task(heartbeat(ws, heartbeat_interval))

            payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "intents": 513,
                    "properties": {
                        "$os": "linux",
                        "$browser": "disco",
                        "$device": "disco"
                    }
                }
            }
            await ws.send(json.dumps(payload))

            session_id = None
            while True:
                response = await ws.recv()
                response = json.loads(response)
                if response['t'] == 'READY':
                    session_id = response['d']['session_id']
                    break

            if session_id:
                log_action(f"Token {token[:10]} successfully left the voice channel {channel_id} in guild {guild_id}")
            else:
                log_action(f"Token {token[:10]} failed to obtain a session ID.")

            if session_id:
                sessions[token] = {
                    "session_id": session_id,
                    "guild_id": guild_id,
                    "channel_id": channel_id
                }

            voice_state_update = {
                "op": 4,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "self_mute": False,
                    "self_deaf": False
                }
            }
            await ws.send(json.dumps(voice_state_update))

    except Exception as e:
        log_action(f"Token {token[:10]} failed to leave the voice channel. Error: {e}")


async def update_voice_state(token, guild_id, channel_id, mute):
    async with websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json', max_size=None) as ws:
        response = await ws.recv()
        response = json.loads(response)

        heartbeat_interval = response['d']['heartbeat_interval'] / 1000
        asyncio.create_task(heartbeat(ws, heartbeat_interval))

        payload = {
            "op": 2,
            "d": {
                "token": token,
                "intents": 513,
                "properties": {
                    "$os": "linux",
                    "$browser": "disco",
                    "$device": "disco"
                }
            }
        }
        await ws.send(json.dumps(payload))

        session_id = None
        while True:
            response = await ws.recv()
            response = json.loads(response)
            
            if response['t'] == 'READY':
                session_id = response['d']['session_id']
                break

        voice_state_update = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": mute,
                "self_deaf": False
            }
        }
        await ws.send(json.dumps(voice_state_update))

        while True:
            response = await ws.recv()
            response = json.loads(response)
            
            if response['t'] == 'VOICE_STATE_UPDATE' and response['d']['channel_id'] == channel_id:
                if mute:
                    log_action(f"Token {token[:10]} muted in voice channel {channel_id}.")
                else:
                    log_action(f"Token {token[:10]} unmuted in voice channel {channel_id}.")

def send(channel_id, sounds, token):
    with requests.Session() as session:
        headers = {"Authorization": token}

        for _ in range(50):
            sound = random.choice(sounds)
            data = {
                "sound_id": sound.get("sound_id"),
                "emoji_id": None,
                "emoji_name": sound.get("emoji_name")
            }

            result = session.post(f"https://discord.com/api/v9/channels/{channel_id}/send-soundboard-sound", json=data, headers=headers)

            if result.status_code == 204:
                continue
            else:
                log_action(f"Error: ({result.status_code}): {result.text}")

        log_action("Completed 50 requests for this token.")

def change_cmd_title():
    if not first_client_ready.is_set():
        os.system("title Loading Best Client Ever Made .")
        time.sleep(0.25)
        os.system("title Loading Best Client Ever Made ..")
        time.sleep(0.25)
        os.system("title Loading Best Client Ever Made ...")
        time.sleep(0.25)
    os.system("title royalty")

def show_loading_screen():
    banner(logo)

async def main():
    os.system("cls")
    title_thread = threading.Thread(target=change_cmd_title)
    title_thread.start()

    loading_thread = threading.Thread(target=show_loading_screen)
    loading_thread.start()

    tasks = []
    for token in tokens:
        tasks.append(setup_client(token))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())