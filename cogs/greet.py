from __future__ import annotations
import discord, asyncio
from cogs.utilities.embeds import EmbedBuilder, send_embed
from utils.helpers.decorators.permissions import Permissions
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import LaneClient

class greet(commands.Cog):
    def __init__(self, bot: LaneClient):
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 4.0, commands.BucketType.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member): 
        res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", member.guild.id)
        if res: 
            bucket = self.cooldown.get_bucket(member)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                await asyncio.sleep(retry_after)
            
            channel = member.guild.get_channel(res['channel_id'])
            if channel is None: return
            try: 
                x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, res['message']))
            except: 
                x = {"content": EmbedBuilder.embed_replacement(member, res['message'])}
            if channel.permissions_for(member.guild.me).send_messages == True:
                await channel.send(**x)

    @commands.group(aliases=["welc", 
                             "greet"])
    async def welcome(self, ctx: commands.Context): 
        if not ctx.invoked_subcommand:
            await ctx.create_pages()

    @welcome.command(description="Return the variables for the welcome message")
    async def variables(self, ctx: commands.Context):
        await send_embed(ctx)

    @welcome.command(description="Returns stats of the welcome message")
    async def config(self, ctx: commands.Context):
        row = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
        if not row: return await ctx.deny("The welcome message is not **configured** for this server.")
        channel = f"{ctx.guild.get_channel(row['channel_id']).name}" if ctx.guild.get_channel(row["channel_id"]) else "None"
        e = row["message"] or "None"
        embed = discord.Embed(color=0x2b2d31, description=f"channel: {channel}\n```{e}```")
        await ctx.send(embed=embed)

    @welcome.command(description="Configure your welcome message")
    @Permissions.has_permission(manage_guild=True)
    async def message(self, ctx: commands.Context, *, code: str):
        row = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
        if row: await self.bot.db.execute("UPDATE welcome SET mes = $1 WHERE guild_id = $2", code, ctx.guild.id)
        else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, 0, code)
        await ctx.approve("Successfully configured the welcome message.")

    @welcome.command(description="Configure your welcome channel")
    @Permissions.has_permission(manage_guild=True)
    async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
        if channel is None:
            check = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
            if not check: return await ctx.deny("The welcome channel is not **configured**")
            await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.approve("Successfully removed the welcome **channel**")
        else:
            check2 = await self.bot.db.fetchrow("SELECT channel_id FROM welcome WHERE guild_id = $1", ctx.guild.id)
            if check2: await self.bot.db.execute("UPDATE welcome SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
            else: await self.bot.db.execute("INSERT INTO welcome VALUES ($1,$2,$3)", ctx.guild.id, channel.id, None)
            await ctx.approve(f"Successfully configured the channel to **{channel.mention}**")

    @welcome.command(description="Delete the welcome message")
    @Permissions.has_permission(manage_guild=True)
    async def delete(self, ctx: commands.Context): 
         check = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id) 
         if not check: return await ctx.deny("Welcome module is not configured") 
         await self.bot.db.execute("DELETE FROM welcome WHERE guild_id = $1", ctx.guild.id)
         await ctx.approve("Successfully removed your server's **welcome message**")

    @welcome.command(description="Test welcome module")
    @Permissions.has_permission(manage_guild=True)
    async def test(self, ctx: commands.Context): 
         res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", ctx.guild.id)
         if res: 
          channel = ctx.guild.get_channel(res['channel_id'])
          if channel is None: return await ctx.send_error("Channel **not** found")
          try: 
           x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, res['mes']))
           await channel.send(**x)
          except: await channel.send(EmbedBuilder.embed_replacement(ctx.author, res['mes'])) 
          await ctx.approve("Sent the **welcome** message to {}".format(channel.mention))

async def setup(bot: LaneClient):
    await bot.add_cog(greet(bot))