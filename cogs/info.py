from __future__ import annotations
import discord, platform, time, random, glob, os, datetime
from discord.ext import commands
from pathlib import Path
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import LaneClient

class Statistics(BaseModel):
    files: str
    imports: str
    lines: str
    classes: str
    functions: str
    coroutines: str

async def get_statistics(bot):
    p = Path("/root/rive/")
    imp = cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob("*.py"):
        if str(f).startswith("venv"):
            continue
        if str(f).startswith("discord"):
            continue
        fc += 1
        with f.open(encoding='utf-8') as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith("class"):
                    cl += 1
                if l.startswith("def"):
                    fn += 1
                if l.startswith("import"):
                    imp += 1
                if l.startswith("from"):
                    imp += 1
                if l.startswith("async def"):
                    cr += 1
                if "#" in l:
                    cm += 1
                ls += 1
    data = Statistics(**{
        "files": f"{fc:,}",
        "imports": f"{imp:,}",
        "lines": f"{ls:,}",
        "classes": f"{cl:,}",
        "functions": f"{fn:,}",
        "coroutines": f"{cr:,}",
    })
    return data

class info(commands.Cog):
    def __init__(self, bot: LaneClient):
        self.bot = bot
        global startTime
        startTime = time.time()

    @commands.command(
        aliases=["bi", "bot", "info", "about"],
        description="Show's various categories of information about the bot."
    )
    async def botinfo(self, ctx: commands.Context):
        commands = []
        for command in set(self.bot.walk_commands()):
            commands.append(command)
        stats = await get_statistics(self.bot)
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
        desc = [
            "### __**General**__",
            "> **Developers**: [q1lla](https://discordid.netlify.app/?id=1035497951591673917)",
            f"> **Latency**: {round(self.bot.latency * 1000)}ms",
            f"> **Uptime**: {uptime}",
            f"> **Guilds**: {len(self.bot.guilds)}",
            f"> **Users**: {len(self.bot.users)}",
            f"> **Commands**: {len(commands)}",
            f"> **Cogs**: {len(self.bot.cogs)}",
            "### __**Links**__",
            "> **Invite**: [Click here](https://discord.com/oauth2/authorize?client_id=1008781747296665691)",
            "> **Support Server**: [Click here](https://discord.gg/received)",
            "### __**Versions**__",
            f"> **Python**: {platform.python_version()}",
            f"> **discord.py**: {discord.__version__}",
            "### __**Code information**__",
            f"> **Total Lines**: {stats.lines}",
            f"> **Total Imports**: {stats.imports}",
            f"> **Total Functions**: {stats.functions}",
            f"> **Total Classes**: {stats.classes}",
            f"> **Total Files**: {stats.files}",
            f"> **Total Coroutines**: {stats.coroutines}",
        ]

        lines = "\n".join(desc)
        eembed = discord.Embed(description="<a:loading:1232722929616162886> **Getting information from client**", color=0x2b2d31)
        eembed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif")

        embed = discord.Embed(description=lines, color=0x2b2d31)
        embed.set_footer(text=f"thanks for using rive • requested by {ctx.author.name}", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif")
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)

        msg = await ctx.send(embed=eembed)
        time.sleep(1) 
        await msg.edit(embed=embed)

    @commands.command(description="Show the bots latency")
    async def ping(self, ctx: commands.Context):
        responses = ["discord.com", "discord's servers", "north korea", "no one", "minecraft servers", "your lost dad", "your wifi", "horny asian women around your area", "911"]
        eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **Getting information from client**")
        eembed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
        embed = discord.Embed(color=0x2b2d31, description=f"it took **{round(self.bot.latency * 1000)}ms** to ping **{random.choice(responses)}**")
        embed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
        msg = await ctx.send(embed=eembed)
        time.sleep(1)
        await msg.edit(embed=embed)

    @commands.command(aliases=["h", "cmds", "commands"], description="Show's the bots commands under various categories")
    async def help(self, ctx: commands.Context, cmd=None):
        if cmd is not None:
            try:
                c = self.bot.get_command(cmd)
                if c.usage is not None:
                    u = c.usage
                else:
                    u = ''
                e = discord.Embed(color=0x2b2d31, description=cmd)
                e.add_field(name="description", value=c.description if c.description else '', inline=False)
                e.add_field(name="category", value=c.cog_name, inline=True)
                e.add_field(name="aliases", value=f"{c.aliases}", inline=True)
                e.add_field(name= "usage", value="```{}```".format(u), inline=False)
                e.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif")
                await ctx.send(embed=e)
            except commands.CommandNotFound:
                await ctx.deny("The command **{}** has not been found")
        options = [
            discord.SelectOption(label="home", description="homepage of the help embed", emoji="<:bow_:1231573068694949908>"),
            discord.SelectOption(label="info", description="info cmds", emoji="<:butterf:1231573064395919360>"),
            discord.SelectOption(label="greet", description="greet cmds", emoji="<:heart:1231573059811676230>"),
            discord.SelectOption(label="fun", description="fun cmds", emoji="<a:aa:1242179551388241940>"),
        ]

        eembed = discord.Embed(color=0x2b2d31, description="<a:loading:1232722929616162886> **Getting information from client**")
        eembed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
        embed = discord.Embed(color=0x2b2d31, description=f"")
        embed.set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
        select = discord.ui.Select(placeholder="select category", options=options)

        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id: return await interaction.deny(message="You are not the author of the embed", empheral=True)
            if select.values[0] == "home": await interaction.response.edit_message(embed=embed)
            else:
                cmds = []
                for cmd in set(self.bot.walk_commands()):
                    if cmd.cog_name == select.values[0]:
                        if cmd.parent is not None: cmds.append("{} {}".format(str(cmd.parent), cmd.name))
                        else: cmds.append(cmd.name)

                eeembed = discord.Embed(color=0x2b2d31, description=f"**`{len(self.bot.cogs)}`** cogs\n**`{len(set(self.bot.walk_commands()))}`** commands\n\n**{select.values[0]} commands**\n```{', '.join(cmds)}```")
                await interaction.response.edit_message(embed=eeembed)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)

        msg = await ctx.send(embed=eembed)
        time.sleep(1)
        await msg.edit(embed=embed, view=view)

async def setup(bot: 
                LaneClient):
    await bot.add_cog(info(bot))
