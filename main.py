from discord.ext import commands, tasks
from utils.helpers.patches import interaction

import tracemalloc
import discord.ext
import discord
import asyncpg
import os, glob
import dotenv
import string, secrets
import time, random, asyncio
from datetime import datetime
import aiohttp, random, os, orjson, logging, typing, json, traceback
from typing import Optional, List
from pathlib import Path
import re
import random

tracemalloc.start()
dotenv.load_dotenv(verbose=True)

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

class Utils:
    async def quick_match(g, mems=[], user=False):
        members = []
        notmems = []

        for mem in mems:
            if isinstance(mem, int):  
                m = g.get_member(mem)
                if not m:
                    notmems.append(str(mem))
                else:
                    members.append(m)
            else: 
                if isinstance(mem, discord.Member):  
                    members.append(mem)
                    continue
                if mem.startswith('<@') and mem.endswith('>') and mem[2:-1].isnumeric():
                    mem = mem[2:-1]
                elif mem.startswith('<@!') and mem.endswith('>') and mem[3:-1].isnumeric():
                    mem = mem[3:-1]

                if mem.isnumeric(): 
                    m = g.get_member(int(mem))
                    if not m: 
                        notmems.append(mem)
                    else:
                        members.append(m)
                else: 
                    mem = mem.lower()
                    if '#' in mem:
                        uname, utag = mem.split('#', 1)
                        m = [M for M in g.members if M.name.lower().startswith(uname) and M.discriminator == utag]
                        if m:
                            members.append(m[0])
                        elif user:
                            m = [M for M in user.users if M.name.lower() == uname and M.discriminator == utag]
                            if m:
                                members.append(m[0])
                    else:
                        m = [M for M in g.members if M.name.lower().startswith(mem)]
                        if m:
                            members.append(m[0])
                        else:
                            notmems.append(mem)

        return members, notmems
    
    def convert_datetime(date: datetime=None):
       if date is None: return None  
       month = f'0{date.month}' if date.month < 10 else date.month 
       day = f'0{date.day}' if date.day < 10 else date.day 
       year = date.year 
       minute = f'0{date.minute}' if date.minute < 10 else date.minute 
       if date.hour < 10: 
           hour = f'0{date.hour}'
           meridian = "AM"
       elif date.hour > 12: 
           hour = f'0{date.hour - 12}' if date.hour - 12 < 10 else f"{date.hour - 12}"
           meridian = "PM"
       else: 
           hour = date.hour
           meridian = "PM"  
       return f"{month}/{day}/{year} at {hour}:{minute} {meridian} ({discord.utils.format_dt(date, style='R')})" 
    
    async def create_tables(bot):
        await bot.db.execute("CREATE TABLE IF NOT EXISTS male_gifs (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS female_gifs (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS anime_gifs (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS anime_pfps (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS male_pfps (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS female_pfps (channel_id BIGINT NOT NULL);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS errors (code TEXT PRIMARY KEY NOT NULL, trace TEXT);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id INTEGER, message TEXT, channel INTEGER);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id BIGINT, username TEXT);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS lastfmcc (user_id BIGINT, command TEXT);")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS lfmode (user_id BIGINT, mode TEXT)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS lfcrowns (user_id BIGINT, artist TEXT)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS lfreactions (user_id BIGINT, reactions TEXT)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS starboardmes (guild_id BIGINT, channel_starboard_id BIGINT, channel_message_id BIGINT, message_starboard_id BIGINT, message_id BIGINT)") 
        await bot.db.execute("CREATE TABLE IF NOT EXISTS starboard (guild_id BIGINT, channel_id BIGINT, count INTEGER, emoji_id BIGINT, emoji_text TEXT)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id BIGINT NOT NULL, channel_id BIGINT NOT NULL, message TEXT)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS blacklisted_user (user_id BIGINT NOT NULL)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS blacklisted_guild (guild_id BIGINT NOT NULL)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id BIGINT NOT NULL, vc INTEGER, interface INTEGER)")
        await bot.db.execute("CREATE TABLE IF NOT EXISTS vc (user_id INTEGER, voice INTEGER)")
        bot.log.info("created the tables")

    class KawaiiTranslator:
        __uwu_pattern = [
            (r"[rl]", "w"),
            (r"[RL]", "W"),
            (r"n([aeiou])", r"ny\g<1>"),
            (r"N([aeiou])", r"Ny\g<1>"),
            (r"N([AEIOU])", r"NY\g<1>"),
            (r"ove", "uv"),
            (r"pog", "poggies"),
        ]

        __actions = [
            "***blushes***",
            "***whispers to self***",
            "***cries***",
            "***screams***",
            "***sweats***",
            "***runs away***",
            "***screeches***",
            "***walks away***",
            "***looks at you***",
            "***huggles tightly***",
            "***boops your nose***",
            "***wags my tail***",
            "***pounces on you***",
            "***nuzzles your necky wecky***",
            "***licks lips***",
            "***glomps and huggles***",
            "***glomps***",
            "***looks around suspiciously***",
            "***smirks smuggly***",
        ]

        __nsfw_actions = [
            "***twerks***",
            "***sees bulge***",
            "***notices buldge***",
            "***starts twerking***",
            "***unzips your pants***",
            "***pounces on your buldge***",
        ]

        __exclamations = [
            "!?",
            "?!!",
            "?!?1",
            "!!11",
            "!!1!",
            "?!?!",
        ]

        __faces = [
            r"(・\`ω\´・)",
            ";;w;;",
            "OwO",
            "owo",
            "UwU",
            r"\>w\<",
            "^w^",
            "ÚwÚ",
            "^-^",
            ":3",
            "x3",
            "Uwu",
            "uwU",
            "(uwu)",
            "(ᵘʷᵘ)",
            "(ᵘﻌᵘ)",
            "(◡ ω ◡)",
            "(◡ ꒳ ◡)",
            "(◡ w ◡)",
            "(◡ ሠ ◡)",
            "(˘ω˘)",
            "(⑅˘꒳˘)",
            "(˘ᵕ˘)",
            "(˘ሠ˘)",
            "(˘³˘)",
            "(˘ε˘)",
            "(˘˘˘)",
            "( ᴜ ω ᴜ )",
            "(„ᵕᴗᵕ„)",
            "(ㅅꈍ ˘ ꈍ)",
            "(⑅˘꒳˘)",
            "( ｡ᵘ ᵕ ᵘ ｡)",
            "( ᵘ ꒳ ᵘ ✼)",
            "( ˘ᴗ˘ )",
            "(ᵕᴗ ᵕ⁎)",
            "*:･ﾟ✧(ꈍᴗꈍ)✧･ﾟ:*",
            "*˚*(ꈍ ω ꈍ).₊̣̇.",
            "(。U ω U。)",
            "(U ᵕ U❁)",
            "(U ﹏ U)",
            "(◦ᵕ ˘ ᵕ◦)",
            "ღ(U꒳Uღ)",
            "♥(。U ω U。)",
            "– ̗̀ (ᵕ꒳ᵕ) ̖́-",
            "( ͡U ω ͡U )",
            "( ͡o ᵕ ͡o )",
            "( ͡o ꒳ ͡o )",
            "( ˊ.ᴗˋ )",
            "(ᴜ‿ᴜ✿)",
            "~(˘▾˘~)",
            "(｡ᴜ‿‿ᴜ｡)",
        ]

        def __init__(
            self,
            seed: int | None = None,
            stutter_chance: float = 0.1,
            face_chance: float = 0.05,
            action_chance: float = 0.075,
            exclamation_chance: float = 1,
            nsfw_actions: bool = False,
        ):
            if not 0.0 <= stutter_chance <= 1.0:
                raise ValueError(
                    "Invalid input value for stutterChance, supported range is 0-1.0"
                )
            if not 0.0 <= face_chance <= 1.0:
                raise ValueError(
                    "Invalid input value for faceChance, supported range is 0-1.0"
                )
            if not 0.0 <= action_chance <= 1.0:
                raise ValueError(
                    "Invalid input value for actionChance, supported range is 0-1.0"
                )
            if not 0.0 <= exclamation_chance <= 1.0:
                raise ValueError(
                    "Invalid input value for exclamationChance, supported range is 0-1.0"
                )

            random.seed(seed)
            self._stutter_chance = stutter_chance
            self._face_chance = face_chance
            self._action_chance = action_chance
            self._exclamation_chance = exclamation_chance
            self._nsfw_actions = nsfw_actions

        def _uwuify_words(self, _msg):
            words = _msg.split(" ")

            for idx, word in enumerate(words):
                if not word:
                    continue
                if re.search(r"((http:|https:)//[^ \<]*[^ \<\.])", word):
                    continue
                if word[0] == "@" or word[0] == "#" or word[0] == ":" or word[0] == "<":
                    continue
                for pattern, substitution in self.__uwu_pattern:
                    word = re.sub(pattern, substitution, word)

                words[idx] = word

            return " ".join(words)

        def _uwuify_spaces(self, _msg):
            words = _msg.split(" ")

            for idx, word in enumerate(words):
                if not word:
                    continue
                if word[0] == "@" or word[0] == "#" or word[0] == ":" or word[0] == "<":
                    continue

                next_char_case = word[1].isupper() if len(word) > 1 else False
                _word = ""

                if random.random() <= self._stutter_chance:
                    stutter_len = random.randrange(1, 3)
                    for j in range(stutter_len + 1):
                        _word += (
                            word[0]
                            if j == 0
                            else (word[0].upper() if next_char_case else word[0].lower())
                        ) + "-"

                    _word += (
                        word[0].upper() if next_char_case else word[0].lower()
                    ) + word[1:]

                if random.random() <= self._face_chance:
                    _word = (_word or word) + " " + random.choice(self.__faces)

                if random.random() <= self._action_chance:
                    _word = (
                        (_word or word)
                        + " "
                        + random.choice(
                            self.__actions
                            if not self._nsfw_actions
                            else self.__actions + self.__nsfw_actions
                        )
                    )

                words[idx] = _word or word

            return " ".join(words)

        def _uwuify_exclamations(self, _msg):
            words = _msg.split(" ")

            for idx, word in enumerate(words):
                if not word:
                    continue
                if (
                    not re.search(r"[?!]+$", word)
                ) or random.random() > self._exclamation_chance:
                    continue

                word = re.sub(r"[?!]+$", "", word) + random.choice(self.__exclamations)
                words[idx] = word

            return " ".join(words)

        def uwuify(self, msg):
            msg = self._uwuify_words(msg)
            msg = self._uwuify_spaces(msg)
            msg = self._uwuify_exclamations(msg)

            return msg

class Logging:
    def info(self, text):
        message = text
        main = "rive.log"
        start = "\033[94m"
        end = "\033[0m"
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        name = "INFO"
        dt = datetime.now().strftime(dt_fmt)
        esc = f"\x1b[30;1m{dt}\x1b[0m"
        colors = {
            "grey": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37,
        }
        send_color = lambda n, m: f"[{colors[n]}m{m}[0m"
        print(f"{esc} {start}{name:<8}{end} {send_color('magenta', main)} {message}")

    def error(self, text):
        message = text
        main = "rive.error"
        start = "\033[91m"
        end = "\033[0m"
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        name = "ERROR"
        dt = datetime.now().strftime(dt_fmt)
        esc = f"\x1b[30;1m{dt}\x1b[0m"
        colors = {
            "grey": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37,
        }
        send_color = lambda n, m: f"[{colors[n]}m{m}[0m"
        print(" ")
        print(f"{esc} {start}{name:<8}{end} {send_color('magenta', main)} {message}")

class HTTP:
    def __init__(self, headers: Optional[dict] = None, proxy: bool = False) -> None:
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        self.get = self.json
        if proxy:self.proxy = lambda: random.choice(os.environ.get("PROXIES", "").split("||"))
        else:self.proxy = lambda: None
               
    async def post_json(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> dict:
        """Send a POST request and get the JSON response"""
        
        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.json()


    async def post_text(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> str:
        """Send a POST request and get the HTML response"""
        
        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                res = await response.text()


    async def async_post_bytes(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = None) -> bytes:
        """Send a POST request and get the response in bytes"""
        
        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session: 
            async with session.post(url, data=data, params=params, proxy=self.proxy(), ssl=ssl) as response:
                return await response.read()


    async def _dl(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
        
        total_size = 0
        data = b""

        async with aiohttp.ClientSession(headers=headers or self.headers, json_serialize=orjson.dumps) as session:
            async with session.get(url, params=params, proxy=self.proxy(), ssl=ssl) as response:
                while True:
                    chunk = await response.content.read(4*1024)
                    data += chunk
                    total_size += len(chunk)
                    if not chunk: break
                    if total_size > 500_000_000: return None
                return data
            
    async def text(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> str:
        """Send a GET request and get the HTML response"""
        
        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return data.decode("utf-8")   
        return data

    async def json(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> dict:
        """Send a GET request and get the JSON response"""
        
        data = await self._dl(url, headers, params, proxy, ssl)
        if data: return orjson.loads(data)
        return data

    async def read(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None, proxy: bool = False, ssl: Optional[bool] = False) -> bytes:
        """Send a GET request and get the response in bytes"""
        return await self._dl(url, headers, params, proxy, ssl)

class GoToModal(discord.ui.Modal, title="change the page"):
  page = discord.ui.TextInput(label="page", placeholder="change the page", max_length=3)

  async def on_submit(self, interaction: discord.Interaction) -> None:
   if int(self.page.value) > len(self.embeds): return await interaction.deny(interaction, f"You can only select a page **between** 1 and {len(self.embeds)}", ephemeral=True) 
   await interaction.response.edit_message(embed=self.embeds[int(self.page.value)-1]) 
  
  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
    await interaction.deny("Unable to change the page", ephemeral=True)

class PaginatorView(discord.ui.View): 
    def __init__(self, ctx: commands.Context, embeds: list): 
      super().__init__()  
      self.embeds = embeds
      self.ctx = ctx
      self.i = 0

    @discord.ui.button(emoji="<:left:1018156480991612999>", style=discord.ButtonStyle.blurple)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.deny(interaction, "You are not the author of this embed")          
      if self.i == 0: 
        await interaction.response.edit_message(embed=self.embeds[-1])
        self.i = len(self.embeds)-1
        return
      self.i = self.i-1
      return await interaction.response.edit_message(embed=self.embeds[self.i])

    @discord.ui.button(emoji="<:right:1018156484170883154>", style=discord.ButtonStyle.blurple)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.deny(interaction, "You are not the author of this embed")     
      if self.i == len(self.embeds)-1: 
        await interaction.response.edit_message(embed=self.embeds[0])
        self.i = 0
        return 
      self.i = self.i + 1  
      return await interaction.response.edit_message(embed=self.embeds[self.i])   
 
    @discord.ui.button(emoji="<:filter:1039235211789078628>")
    async def goto(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user.id != self.ctx.author.id: return await interaction.deny(interaction, "You are not the author of this embed")     
     modal = GoToModal()
     modal.embeds = self.embeds
     await interaction.response.send_modal(modal)
     await modal.wait()
     try:
      self.i = int(modal.page.value)-1
     except: pass 
    
    @discord.ui.button(emoji="<:stop:1018156487232720907>", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.deny(interaction, "You are not the author of this embed")     
      await interaction.message.delete()

class LaneInteraction(discord.Interaction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def approve(self, message, empheral: bool = False):
            emojis = {
            "check": "<:check:1232712864352047144>",
            "cross": "<:cross:1232721067995435059>"
            }
            await self.response.send_message(embed=discord.Embed(description=emojis["check"] + " " + self.user.mention + ": " + message, color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"), ephemeral=empheral)
    
    async def deny(self, message, empheral: bool = False):
        emojis = {
        "check": "<:check:1232712864352047144>",
        "cross": "<:cross:1232721067995435059>"
        }
        await self.response.send_message(embed=discord.Embed(description=emojis["cross"] + " " + self.user.mention + ": " + message, color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"), ephemeral=empheral)
    
class LaneContext(commands.Context):
    def __init__(self, *args, **kwargs):
        self.emojis = {
            "check": "<:check:1232712864352047144>",
            "cross": "<:cross:1232721067995435059>"
        }
        super().__init__(*args, **kwargs)

    async def approve(self, message):
        await self.send(embed=discord.Embed(description=self.emojis["check"] + " " + self.author.mention + ": " + message, color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"))
    
    async def deny(self, message):
        await self.send(embed=discord.Embed(description=self.emojis["cross"] + " " + self.author.mention + ": " + message, color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"))

    async def paginator(self, embeds: List[discord.Embed]):
        if len(embeds) == 1: return await self.send(embed=embeds[0]) 
        view = PaginatorView(self, embeds)
        view.message = await self.reply(embed=embeds[0], view=view) 
    
    async def send_group_help(self, group: commands.Group):
        embeds = []
        p = 0
        for cmd in group.commands:
            cmdname=(
                f"{str(cmd.parent)} {cmd.name}"
                if str(cmd.parent) != "None"
                else cmd.name
            )
            p+=1
            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **Getting information from client**")
            eembed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
            embeds.append(
                discord.Embed(color=0x2b2d31, title=cmdname, description=cmd.description)
                .set_author(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
                .add_field(
                    name="usage",
                    value=f"```{cmdname} {cmd.usage if cmd.usage else ''}```",
                    inline=False,
                )
                .set_footer(name=f"page: {p}/{len(group.commands)} • aliases: {cmd.aliases if cmd.aliases else ''} • category: {cmd.cog_name}")
            )

        return await self.paginator(embeds)
    
    async def create_pages(self):
       return await self.send_group_help(self.command)

class LaneClient(commands.Bot):
    def __init__(self):
        self.log = Logging()
        self.session = HTTP()
        self.color = 0x2b2d31
        self.pfps = {
            "female": {
                "pfps": open("/root/rive/utils/pics/female_pfps.txt").read().splitlines(),
                "gifs": open("/root/rive/utils/pics/female_gifs.txt").read().splitlines()
            },
            "male": {
                "pfps": open("/root/rive/utils/pics/male_pfps.txt").read().splitlines(),
                "gifs": open("/root/rive/utils/pics/male_gifs.txt").read().splitlines()
            },
            "anime": {
                "pfps": open("/root/rive/utils/pics/anime_pfps.txt").read().splitlines(),
                "gifs": open("/root/rive/utils/pics/anime_gifs.txt").read().splitlines()
            }
        }
        super().__init__( owner_ids=[1035497951591673917, 1140301345711206510],
            intents=discord.Intents.all(), allowed_mentions=discord.AllowedMentions(everyone=False),
            chunk_guilds_on_startup=False, command_prefix=commands.when_mentioned,
            case_insensitive=True, help_command=None
        )

    
    async def create_db_pool(self):
        self.db = await asyncpg.create_pool(host="aws-0-eu-central-1.pooler.supabase.com", user="postgres.wrutilsbdyehafklebno", database="postgres", port="5432", password="jjg60fnlA64LPYof")
        self.log.info("loaded the database")

    async def setup_hook(self):
        await self.create_db_pool()
        for file in os.listdir("/root/rive/cogs"):
            if file.endswith(".py"):
             try:
              await self.load_extension(f"cogs.{file[:-3]}")
              self.log.info(f"Loaded plugin {file[:-3]}".lower())
             except Exception as e: logging.error("lol", exc_info=e)
        for file in os.listdir("/root/rive/events"): 
         if file.endswith(".py"):
          try:
           await self.load_extension(f"events.{file[:-3]}")
           self.log.info(f"Loaded plugin {file[:-3]}".lower())
          except Exception as e: self.log.error(f"failed to load {file[:-3]} {e} ".lower())

    async def on_ready(self):
        self.log.info("successfully connected to discord servers.")
        interaction.load_patch(interaction=LaneInteraction, logger=self.log)
        await Utils.create_tables(self)
        await self.load_extension("jishaku")
        activity.start()

    async def close(self):
        await self.db.close()

    #async def on_error(self, event, error, *args, **kwargs):
    #    owo = self.get_channel(1244619020557353062)
    #    msg = await owo.send(f"\n{event}```\n{error}\n```")
    #    await msg.add_reaction("<:cross:1232721067995435059>")

    def get_code(self, length: int=6):
        characters = string.ascii_letters + string.digits
        key = ''.join(secrets.choice(characters) for _ in range(length))
        return key
    
    async def get_context(self, message, *, cls= LaneContext) -> LaneContext:
        return await super().get_context(message, cls=cls)

    async def on_message(self, msg: discord.Message):
        if msg.content == f"<@{self.user.id}>":
            await msg.reply(f"hai :3\nprefix: `@rive`")

        

        await self.process_commands(msg)

    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.process_commands(after) 

    async def on_command_error(self, ctx: LaneContext, exception: commands.CommandError):
        if isinstance(exception, commands.NotOwner): pass
        elif isinstance(exception, commands.CommandNotFound): return
        elif isinstance(exception, commands.MissingPermissions): return await ctx.deny(f"This command requires the `{exception.missing_permissions[0]}` permission.")
        elif isinstance(exception, commands.BotMissingPermissions): return await ctx.deny(f"I do not have enough **permissions** to do this.")
        elif isinstance(exception, commands.EmojiNotFound): return await ctx.deny(f"Unable to convert {exception.argument} into an **emoji**")
        elif isinstance(exception, commands.MemberNotFound): return await ctx.deny(f"Unable to find member **{exception.argument}**")
        elif isinstance(exception, commands.UserNotFound): return await ctx.deny(f"Unable to find user **{exception.argument}**")
        elif isinstance(exception, commands.RoleNotFound): return await ctx.deny(f"Couldn't find role **{exception.argument}**")
        elif isinstance(exception, commands.ChannelNotFound): return await ctx.deny(f"Couldn't find channel **{exception.argument}**")
        elif isinstance(exception, commands.UserConverter): return await ctx.deny(f"Couldn't convert that into an **user** ")
        elif isinstance(exception, commands.MemberConverter): return await ctx.deny("Couldn't convert that into a **member**")
        elif isinstance(exception, commands.MissingRequiredArgument): return await ctx.deny(f"**{exception.args[0]}** is a required argument which is missing")
        elif isinstance(exception, discord.HTTPException): return await ctx.deny("Couldn't run the command")
        else:
            code = self.get_code()
            error = str(exception)
            await self.db.execute("INSERT INTO errors (code, trace) VALUES ($1, $2)", code, error)
            await ctx.deny(f"A unexpected error occured while executing the command, Please report this code **`{code}`** in our support server.")

bot = LaneClient()

responses = ["The first oranges weren't orange.", "Sea otters hold hands while sleeping to keep from drifting apart.", "There are more fake flamingos in the world than real ones.", "A strawberry isn't an actual berry, but a banana is.", "The Titanic's swimming pool is still filled with water.", "A 'jiffy' is an actual unit of time: 1/100th of a second.", "A day on Venus is longer than a year on Venus.", "The fear of the number 13 is called triskaidekaphobia.", "Giraffes have the same number of neck vertebrae as humans.", "The scientific term for brain freeze is sphenopalatine ganglioneuralgia.", "The smell of freshly-cut grass is actually a plant distress call.", "The longest wedding veil was the same length as 63.5 football fields.", "The dot over the letter 'i' is called a tittle.", "A group of flamingos is called a flamboyance.", "A 'jiffy' is an actual unit of time: 1/100th of a second.", "A day on Venus is longer than a year on Venus.", "The fear of the number 13 is called triskaidekaphobia.", "Giraffes have the same number of neck vertebrae as humans.", "The scientific term for brain freeze is sphenopalatine ganglioneuralgia.", "The smell of freshly-cut grass is actually a plant distress call.", "The longest wedding veil was the same length as 63.5 football fields.", "The dot over the letter 'i' is called a tittle.", "Cows have best friends and can become stressed when they are separated.", "Bananas are berries, but strawberries aren't.", "A group of flamingos is called a flamboyance.", "The unicorn is the national animal of Scotland.", "The first oranges weren't orange.", "Sea otters hold hands while sleeping to keep from drifting apart.", "There are more fake flamingos in the world than real ones.", "A strawberry isn't an actual berry, but a banana is.", "The Titanic's swimming pool is still filled with water.", "A 'jiffy' is an actual unit of time: 1/100th of a second.", "A day on Venus is longer than a year on Venus.", "The fear of the number 13 is called triskaidekaphobia.", "Giraffes have the same number of neck vertebrae as humans.", "The scientific term for brain freeze is sphenopalatine ganglioneuralgia.", "The smell of freshly-cut grass is actually a plant distress call.", "The longest wedding veil was the same length as 63.5 football fields.", "The dot over the letter 'i' is called a tittle."]

#@tasks.loop(seconds=12)
#async def female_gifs():
#    rows = await bot.db.fetch("SELECT channel_id FROM female_gifs")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["female"]["gifs"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading gif**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)
#
#@tasks.loop(seconds=12)
#async def male_gifs():
#    rows = await bot.db.fetch("SELECT channel_id FROM male_gifs")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["male"]["gifs"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading gif**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)
#
#@tasks.loop(seconds=12)
#async def anime_pfps():
#    rows = await bot.db.fetch("SELECT channel_id FROM anime_pfps")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["anime"]["pfps"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading pfp**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)
#
#@tasks.loop(seconds=12)
#async def female_pfps():
#    rows = await bot.db.fetch("SELECT channel_id FROM female_pfps")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["female"]["pfps"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading pfp**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)
#
#@tasks.loop(seconds=12)
#async def male_pfps():
#    rows = await bot.db.fetch("SELECT channel_id FROM male_pfps")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["male"]["pfps"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading pfp**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)
#
#@tasks.loop(seconds=12)
#async def anime_pfps():
#    rows = await bot.db.fetch("SELECT channel_id FROM anime_pfps")
#    for row in rows:
#        channel = row[0]
#        slay = bot.get_channel(channel)
#        if slay:
#            fact = random.choice(responses)
#            pfp = random.choice(bot.pfps["anime"]["pfps"])
#            eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **loading pfp**")
#            eembed.set_footer(text=fact)
#            embed = discord.Embed(color=0x2b2d31)
#            embed.set_image(url=pfp)
#            invite = discord.ui.Button(label="invite", url="https://discord.com/api/oauth2/authorize?client_id=1008781747296665691&permissions=8&scope=bot")
#            support = discord.ui.Button(label="support", url="https://discord.gg/brat")
#            view = discord.ui.View()
#            view.add_item(invite)
#            view.add_item(support)
#            embed.set_footer(text="powered by rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
#            msg = await slay.send(embed=eembed)
#            await asyncio.sleep(5)
#            await msg.edit(embed=embed, view=view)

def get_genre(g: str):
   if g == "competing": return discord.ActivityType.competing
   elif g == "streaming": return discord.ActivityType.streaming
   elif g == "playing": return discord.ActivityType.playing 
   elif g == "watching": return discord.ActivityType.watching
   elif g == "listening": return discord.ActivityType.listening


@tasks.loop(seconds=16)
async def activity():
    list = [f"{len(bot.guilds)} servers", f"{round(bot.latency * 1000)}ms ping", f"{len(bot.users)} users"]
    activ = ["streaming"]
    for a in list:
        for b in activ:
            await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=get_genre(b), name=a, url="https://twitch.tv/rive"))
            await asyncio.sleep(16)

bot.run("MTEzOTkyOTI3MDAzMDk3OTE0Mg.GmI_Ak.QQExr7Ceis_qsSwNv8WuRX_ZGlh0houOy55CkI")