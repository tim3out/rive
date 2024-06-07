import discord
from discord.ext import commands

class EmbedBuilder:
 def ordinal(self, num: int) -> str:
   """Convert from number to ordinal (10 - 10th)""" 
   numb = str(num) 
   if numb.startswith("0"): numb = numb.strip('0')
   if numb in ["11", "12", "13"]: return numb + "th"
   if numb.endswith("1"): return numb + "st"
   elif numb.endswith("2"):  return numb + "nd"
   elif numb.endswith("3"): return numb + "rd"
   else: return numb + "th"    

 def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

 def embed_replacement(user: discord.Member, params: str=None):
    if params is None: return None
    if '{user}' in params:
        params=params.replace('{user}', str(user.name) + "#" + str(user.discriminator))
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', str(user.display_avatar.url))
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', EmbedBuilder.ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', EmbedBuilder.ordinal(user.guild.premium_subscription_count))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', EmbedBuilder.ordinal(len(user.guild.premium_subscribers)))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.vanity}' in params: 
        params=params.replace('{guild.vanity}', "/" + user.guild.vanity_url_code or "none")         
    if '{invisible}' in params: 
        params=params.replace('{invisible}', '2b2d31') 
    if '{botcolor}' in params: 
        params=params.replace('{botcolor}', '2b2d31')       
    if '{guild.icon}' in params:
      if user.guild.icon:
        params=params.replace('{guild.icon}', user.guild.icon.url)
      else: 
        params=params.replace('{guild.icon}', "https://none.none")        

    return params

 async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in EmbedBuilder.get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]

        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].replace("#", ""), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('image:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            disabled=True
            style=discord.ButtonStyle.gray
            emoji=None 
            label=None 
            url=None
            for m in z:
             if "label:" in m: label=m.replace("label:", "")
             if "url:" in m: 
                url=m.replace("url:", "").strip()
                disabled=False
             if "emoji:" in m: emoji=m.replace("emoji:", "").strip()
             if "disabled" in m: disabled=True     
             if "style:" in m: 
               if m.replace("style:", "").strip() == "red": style=discord.ButtonStyle.red 
               elif m.replace("style:", "").strip() == "green": style=discord.ButtonStyle.green 
               elif m.replace("style:", "").strip() == "gray": style=discord.ButtonStyle.gray 
               elif m.replace("style:", "").strip() == "blue": style=discord.ButtonStyle.blurple   

            view.add_item(discord.ui.Button(style=style, label=label, emoji=emoji, url=url, disabled=disabled))
            
    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view 

class EmbedScript(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument: str):
   x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, argument))
   if x[0] or x[1]: return {"content": x[0], "embed": x[1], "view": x[2]} 
   return {"content": EmbedBuilder.embed_replacement(ctx.author, argument)}
  
async def send_embed(ctx: commands.Context):
     embed1 = discord.Embed(color=0x2b2d31, title="user related variables")
     embed1.description = """
    >>> {user} - returns user full name
{user.name} - returns user's username
{user.mention} - mentions user
{user.avatar} - return user's avatar
{user.joined_at} returns the relative date the user joined the server
{user.created_at} returns the relative time the user created the account
{user.discriminator} - returns the user's discriminator
    """

     embed2 = discord.Embed(color=0x2b2d31, title="guild related variables")
     embed2.description = """
    >>> {guild.name} - returns the server's name
 {guild.count} - returns the server's member count
 {guild.count.format} - returns the server's member count in ordinal format
 {guild.icon} - returns the server's icon
 {guild.id} - returns the server's id
 {guild.vanity} - returns the server's vanity, if any 
 {guild.created_at} - returns the relative time the server was created
 {guild.boost_count} - returns the number of server's boosts
 {guild.booster_count} - returns the number of boosters
 {guild.boost_count.format} - returns the number of boosts in ordinal format
 {guild.booster_count.format} - returns the number of boosters in ordinal format
 {guild.boost_tier} - returns the server's boost level
   """
    
     embed3 = discord.Embed(color=discord.Embed, title="invoke command only variables")
     embed3.description = """
    >>> {member} - returns member's name and discriminator
    {member.name} - returns member's name
    {member.mention} - returns member mention
    {member.discriminator} - returns member's discriminator
    {member.id} - return member's id
    {member.avatar} - returns member's avatar
    {reason} - returns action reason, if any
    """
     
     embed4 = discord.Embed(color=0x2b2d31, title="last.fm variables")
     embed4.description = """
    >>> {scrobbles} - returns all song play count
    {trackplays} - returns the track total plays
    {artistplays} - returns the artist total plays
    {albumplays} - returns the album total plays
    {track} - returns the track name
    {trackurl} - returns the track url
    {trackimage} - returns the track image
    {artist} - returns the artist name
    {artisturl} - returns the artist profile url
    {album} - returns the album name 
    {albumurl} - returns the album url
    {username} - returns your username
    {useravatar} - returns user's profile picture"""
     
     embed5 = discord.Embed(color=0x2b2d31, title="other variables")
     embed5.description = """
    >>> {invisible} - returns the invisible embed color
    """