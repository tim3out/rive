import discord
from discord.ext import commands
class Permissions:
    @staticmethod
    def has_permission(**perms: bool) -> commands.check:
        invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
        if invalid:
            raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")
        def predicate(ctx: commands.Context) -> bool:
            permissions = ctx.permissions
            bot = ctx.guild.me.guild_permissions
            
            if discord.Permissions.administrator in permissions: return True
            if discord.Permissions.administrator not in bot and (missing := [perm for perm, value in perms.items() if getattr(bot, perm) != value]): raise commands.BotMissingPermissions(missing)
            if ctx.author.id in ctx.bot.owner_ids or not (missing := [perm for perm, value in perms.items() if getattr(permissions, perm) != value]): return True
            raise commands.MissingPermissions(missing)
        return commands.check(predicate)