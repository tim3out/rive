from __future__ import annotations
import discord, os, sys, aiohttp, time, asyncio
from discord.ext import commands
from cogs.utilities.eval import AsyncCodeExecutor, ReplResponseReactor, AsyncSender
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from main import LaneClient, LaneContext

def restart_bot(): 
    os.execv(sys.executable, ['python3'] + sys.argv)

def text_creator(text: str, num: int = 1980, /, *, prefix: str = '', suffix: str = ''):
    return [
        prefix + (text[i : i + num]) + suffix
        for i in range(0, len(text), num)
    ]

async def handle_result(ctx: LaneContext, result: Any) -> Optional[discord.Message]:
    e = discord.Embed(description=f"**```{result}```**", color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
    if isinstance(result, discord.Message):
        pass
    if isinstance(result, discord.File):
        return await ctx.send(file=result)
    if isinstance(result, discord.Embed):
        return await ctx.send(embed=e)
    if isinstance(result, discord.Button):
        return await ctx.send(view=discord.ui.View().add_item(result))
    if not isinstance(result, str):
        result = repr(result)

    if len(result) <= 2000:
        if result.strip() == '':
            result = "\u200b"

        if ctx.bot.http.token:
            result = result.replace(ctx.bot.http.token, 'token')

        return await ctx.send(
            embed=e,
            allowed_mentions=discord.AllowedMentions.none()
        )
        
    paginator = text_creator(result, 1980, prefix='```py\n', suffix='```')
    return await ctx.paginator(paginator)

class dev(commands.Cog):
    def __init__(self, bot: LaneClient):
        self.bot = bot

    @commands.command(aliases=["servers"])
    @commands.is_owner()
    async def guilds(self, ctx: commands.Context):
            def key(s):
                return s.member_count
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            lis = [g for g in self.bot.guilds]
            lis.sort(reverse=True, key=key)
            for guild in lis:
              mes = f"{mes}`{k}` {guild.name} ({guild.id}) - {guild.member_count} - {guild.owner}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=0x2b2d31, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed(color=0x2b2d31, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&"))
            await ctx.paginator(number)  

    @commands.command(aliases=["reboot", "rs"], description="dev")
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        await ctx.send("rebooting")
        restart_bot()

    @commands.command(aliases=["rl"])
    @commands.is_owner()
    async def reload(self, ctx:commands.Context):
        cogs = []
        for c in set(self.bot.extensions):
                await self.bot.reload_extension(c)
                cog = c.replace("cogs.", '')
                cogs.append(f"reloaded {cog}")
        if cogs:
            embed = discord.Embed(
                description = "\n".join(cogs),
                color = 0x2b2d31)
            await ctx.send(embed=embed)

    @commands.command(aliases=["setav", "botav"], description="dev")
    @commands.is_owner()
    async def setpfp(self, ctx: commands.Context, url: str):
        try:
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        image_data = await response.read()
                        await self.bot.user.edit(avatar=image_data)
                        e = discord.Embed(
                        description=f"successfully changed {self.bot.user.name}'s avatar")
            await ctx.message.add_reaction("<a:loading:1232722929616162886>")
            time.sleep(2)
            await ctx.message.add_reaction("<:check:1232712864352047144>")
            await ctx.message.delete()
            await ctx.send(embed = e)
        except Exception as e:
            pass
    
    @commands.group(aliases=["traceback"])
    @commands.is_owner()
    async def error(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("meow meow meow")

    @error.command()
    @commands.is_owner()
    async def get(self, ctx: commands.Context, error):
        check = await self.bot.db.execute("SELECT * FROM errors WHERE code = $1", error)
        if check: await ctx.send(embed=discord.Embed(description="Exception:\n```\n{}\n```".format(check["trace"])))
        else: return await ctx.deny("No exception was found with that code")

    @error.command()
    @commands.is_owner()
    async def delete(self, ctx: commands.Context):
        await self.bot.db.execute("DELETE FROM errors")
        await ctx.approve("Successfully deleted the saved exceptions")

    @commands.command(
        name='eval',
        aliases=['py', 'evaluate', 'exec'],
    )
    @commands.is_owner()
    async def e(self, ctx: commands.Context, *, code: str):
        
        code = code.strip('```')  
        env = {
            'author': ctx.author,
            'bot': ctx.bot,
            'channel': ctx.channel,
            'ctx': ctx,
            'guild': ctx.guild,
            'me': ctx.me,
            'message': ctx.message,
            'msg': ctx.message,
        }

        async with ReplResponseReactor(ctx.message):
            execute = AsyncCodeExecutor(code, arg_dict=env)
            async for send, result in AsyncSender(execute):
                if result is None:
                    continue

                send(await handle_result(result=result, ctx=ctx))

                #e = discord.Embed(description=f"**```{r}```**", color=0x2b2d31).set_footer(text="rive", icon_url="https://cdn.discordapp.com/attachments/1208741351760461846/1234890090283667567/1203853126486990909.gif?ex=66326084&is=66310f04&hm=3c0bb03f86cb839aded3f573cf6ad5cd83de0fd5fefdae3ca62d7bcfaf8085d6&")
                #m = await ctx.send(embed=e)

async def setup(bot: LaneClient):
    await bot.add_cog(dev(bot))