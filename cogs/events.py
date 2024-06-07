from __future__ import annotations
import discord
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import LaneClient

        
async def sendmsgg(self, ctx, content, embed, view, file, allowed_mentions, delete_after): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False, delete_after=delete_after)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, delete_after=delete_after) 
        
async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=True)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions) 


class Events(commands.Cog):
    def __init__(self, bot: LaneClient):
        self.bot = bot 
        
    #@commands.Cog.listener("on_guild_add")
    #async def hi(self, guild: discord.Guild):
    #    channel = guild.text_channels[0]
    #    embed = discord.Embed(color=0x2b2d31, description=f"ty for inviting rive. rive is a bot which has...")
    #    embed.add_field(name="hot cmds", )
async def setup(bot):
    await bot.add_cog(Events(bot))  