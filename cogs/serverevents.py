import discord
from discord.ext import commands,tasks
import asyncio
import random
import re
import traceback
import datetime
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import datetime
from random import choice

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d||))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400,"":1}

async def gawedit(msg,data,bc,edit = None):
    author = await bc.fetch_user(data["authorid"])
    started = data['startedat']
    whendone = data['startedat'] + relativedelta(seconds=data['duration'])
    timeleft = whendone - datetime.datetime.now()
    seconds = timeleft.total_seconds()
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if int(d) == 0 and int(h) == 0 and int(m) == 0:
        duration = f"{int(s)} seconds"
    elif int(d) == 0 and int(h) == 0:
        duration = f"{int(m)} minutes {int(s)} seconds"
    elif int(d) == 0 and int(m) != 0:
        duration = f"{int(h)} hours, {int(m)} minutes and {int(s)} seconds"
    elif int(d) != 0 and int(h) != 0 and int(m) != 0:
        duration = f"{int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds"
    else:
        duration = f"{int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds"
    if not edit:
        em = discord.Embed(
            title = "Giveaway Time!",
            description = f"Giveaway By: {author.mention}\n**ENDED**\n\nReward: `{data['reward']}`",
            color=0xff0000,
            timestamp=data['startedat']
        )
    else:
        em = discord.Embed(
            title = "Giveaway Time!",
            description = f"Giveaway By: {author.mention}\nEnds **<t:{int(whendone.timestamp())}:R>**\n\nReward: `{data['reward']}`",
            color=0xD711FF,
            timestamp=data['startedat']
        )
    em.set_footer(text=f'{data["winners"]} winners')
    await msg.edit(embed=em)

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)

class ServerEvents(commands.Cog):
    def __init__(self,bc):
        self.bc = bc
        self.GAWtask = self.checkGAW.start()

    def cog_unload(self):
        self.GAWtask.cancel()

    @tasks.loop(seconds=15)
    async def checkGAW(self):
        heist = deepcopy(self.bc.GAWdata)
        for key, value in heist.items():
            member = value["authorid"]
            member = self.bc.get_user(member)
            msg = value["_id"]
            winners = value["winners"]
            reward = value['reward']
            currentTime = datetime.datetime.now()
            try:
                guild = self.bc.get_guild(value['guildId'])
            except:
                await self.bc.giveaways.delete(msg)
                try:
                    self.bc.GAWdata.pop(msg)
                except KeyError:
                    pass
            channel = self.bc.get_channel(value['channelId'])
            if not guild:
                continue
            ctx = discord.utils.get(guild.text_channels, id=value['channelId'])
            try:
                new_msg = await channel.fetch_message(msg)
            except:
                continue
            unmuteTime = value['startedat'] + relativedelta(seconds=value['duration'])
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.bc.user))
            if currentTime >= unmuteTime:
                if len(users) == 0:
                    await self.bc.giveaways.delete(msg)
                    try:
                        self.bc.GAWdata.pop(msg)
                    except KeyError:
                        pass
                    return await ctx.send("A winner could not be determined.")
                ppl = []
                for _ in range(winners):
                    winner = random.choice(users)
                    users.remove(winner)
                    ppl.append(winner)
                    if len(users) == 0:
                        break

                await ctx.send("The people who won the giveaway for **{}** were: {}\nMessage link: https://discord.com/channels/{}/{}/{}".format(reward,", ".join([user.mention for user in ppl]),guild.id,channel.id,new_msg.id))
                await gawedit(new_msg,value,self.bc)
                await self.bc.giveaways.delete(msg)
                try:
                    self.bc.GAWdata.pop(msg)
                except KeyError:
                    pass

    @checkGAW.before_loop
    async def before_checkGAW(self):
        await self.bc.wait_until_ready()

    @commands.command(description="ask something with this",usage="<question>")
    async def poll(self,ctx, *,question):
            em = discord.Embed(
                title="Poll",
                color=random.choice(self.bc.color_list),
                description=question
            )
            em.set_footer(text=f"Poll by {ctx.author}", icon_url=ctx.author.avatar)
            msg = await ctx.send(embed=em)
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
    
    @commands.group(
        aliases=['gaw'], usage="", invoke_without_command=True,description="give something away in your server",
    )
    @commands.guild_only()
    async def giveaway(self, ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="giveaway")

    @giveaway.command(name="start", description="Start a giveaway")
    async def gaw_start(self,ctx,channel:discord.TextChannel,winners:int,time: TimeConverter,*, reward):
        if not channel:
            await ctx.invoke(self.bc.get_command("help"),entity="giveaway")
            return
        em = discord.Embed(
            title="Giveaway Time!",
            description=f"Giveaway By: {ctx.author.mention}\nEnds **<t:{time + int(datetime.datetime.utcnow().timestamp())}:R> **\n\nReward: `{reward}`",
            color=0xD711FF,
            timestamp=datetime.datetime.utcnow()
        )
        em.set_footer(text="{} winners".format(winners))
        msg = await channel.send(embed=em)
        await msg.add_reaction("🎉")
        data = {
            "_id": msg.id,
            'duration': time,
            'startedat': datetime.datetime.now(),
            'channelId': msg.channel.id,
            'authorid': ctx.author.id,
            'guildId': ctx.guild.id,
            'winners': winners,
            'reward': reward
        }
        await self.bc.giveaways.upsert(data)
        self.bc.GAWdata[msg.id] = data

    @giveaway.command(name="reroll", description="Reroll a new winner")
    @commands.has_role("Giveaway")
    async def gaw_reroll(self,ctx,channel:discord.TextChannel,msgid,winners:int):
        try:
            await ctx.send("Rerolling...")
            new_msg = await channel.fetch_message(msgid)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.bc.user))
            ppl = [random.choice(users) for _ in range(winners)]
            await ctx.send("The new people who won the giveaway were: {}\nMessage link: https://discord.com/channels/{}/{}/{}".format(", ".join([user.mention for user in ppl]),ctx.guild.id,channel.id,new_msg.id))
        except Exception:
            #await ctx.send(traceback.format_exc())
            return
    
    @giveaway.command(name="end", description="End a giveaway early")
    @commands.has_role("Giveaway")
    async def gaw_end(self,ctx,channel:discord.TextChannel,msgid):
        try:
            data = await self.bc.giveaways.find_by_id(int(msgid))
            winners = data["winners"]
            await ctx.send("Ending Giveaway...")
            new_msg = await channel.fetch_message(msgid)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.bc.user))
            if len(users) == 0:
                await self.bc.giveaways.delete(new_msg.id)
                try:
                    self.bc.GAWdata.pop(new_msg)
                except KeyError:
                    pass
                return await ctx.send("A winner could not be determined.")
            ppl = [random.choice(users) for _ in range(winners)]
            await ctx.send("The people who won the giveaway for **{}** were: {}\nMessage link: https://discord.com/channels/{}/{}/{}".format(data["reward"],", ".join([user.nmention for user in ppl]),ctx.guild.id,channel.id,new_msg.id))
            await gawedit(new_msg,data,self.bc)
            await self.bc.giveaways.delete(msgid)
            try:
                self.bc.GAWdata.pop(msgid)
            except KeyError:
                pass
        except IndexError:
            await ctx.send("No one is in this giveaway for me to pick!")
            return

    @commands.command(
        description="Suggest something you wanna add in your server",
        usage="<suggestion>"
    )
    async def suggest(self,ctx,*,suggestion=None):
        if not suggestion:
            await ctx.send("Please specify someting to suggest")
            return
        data = await self.bc.suggestions.find(ctx.guild.id)
        if not data or "channel" not in data:
            await ctx.send("please set up a suggestions channel")    
            return
        else:
            channel = discord.utils.get(ctx.guild.text_channels, id=data["channel"])
            em = discord.Embed(
                title="Suggestion #{}".format(data["numbers"] + 1),
                color=random.choice(self.bc.color_list),
                description=suggestion,
                timestamp=datetime.datetime.utcnow()
            )
            em.set_footer(text="Suggestion By {}".format(ctx.author), icon_url=ctx.author.avatar)
            suggest = await channel.send(embed=em)
            await suggest.add_reaction('👍')
            await suggest.add_reaction('👎')
            await ctx.send("Suggestion has been submitted")
            data["suggestions"].append({"messageid":suggest.id,"suggestion#":data["numbers"] + 1, "content":suggestion})
            data["numbers"] += 1
            await self.bc.suggestions.upsert(data)
    
    @commands.command(
        description="deny a suggestion",
        usage="<suggestion #>"
    )
    @commands.has_permissions(manage_messages=True)
    async def deny(self,ctx,suggestion:int, *,reason="No Reason"):
        data = await self.bc.suggestions.find(ctx.guild.id)
        channel = discord.utils.get(ctx.guild.text_channels, id=data["channel"])
        for i in data["suggestions"]:
            if i["suggestion#"] == suggestion:
                msg = await channel.fetch_message(i["messageid"])
                em = discord.Embed(
                    title="Suggestion #{}".format(suggestion),
                    description="{}\n\n**Denied by {}:**\n{}".format(i["content"],ctx.author.name,reason),
                    color=0xff0000,
                    timestamp=datetime.datetime.utcnow()
                )
                em.set_footer(text="Denied By {}".format(ctx.author), icon_url=ctx.author.avatar)
                await msg.edit(embed=em)
                await ctx.send("Suggestion {} has been denied with the reason: {}".format(suggestion,reason))
                break
            else:
                continue

    @commands.command(
        description="approve a suggestion",
        usage="<suggestion #>"
    )
    @commands.has_permissions(manage_messages=True)
    async def approve(self,ctx,suggestion:int, *,reason="No Reason"):
        data = await self.bc.suggestions.find(ctx.guild.id)
        channel = discord.utils.get(ctx.guild.text_channels, id=data["channel"])
        for i in data["suggestions"]:
            if i["suggestion#"] == suggestion:
                msg = await channel.fetch_message(i["messageid"])
                em = discord.Embed(
                    title="Suggestion #{}".format(suggestion),
                    description="{}\n\n**Approved by {}:**\n{}".format(i["content"],ctx.author.name,reason),
                    color=0x00ff00,
                    timestamp=datetime.datetime.utcnow()
                )
                em.set_footer(text="Approved By {}".format(ctx.author), icon_url=ctx.author.avatar)
                await msg.edit(embed=em)
                await ctx.send("Suggestion {} has been approved with the reason: {}".format(suggestion,reason))
                break
            else:
                continue
            
    @commands.command(
        description="consider a suggestion",
        usage="<suggestion #>"
    )
    @commands.has_permissions(manage_messages=True)
    async def consider(self,ctx,suggestion:int, *,reason="No Reason"):
        data = await self.bc.suggestions.find(ctx.guild.id)
        channel = discord.utils.get(ctx.guild.text_channels, id=data["channel"])
        for i in data["suggestions"]:
            if i["suggestion#"] == suggestion:
                msg = await channel.fetch_message(i["messageid"])
                em = discord.Embed(
                    title="Suggestion #{}".format(suggestion),
                    description="{}\n\n**Considered by {}:**\n{}".format(i["content"],ctx.author.name,reason),
                    color=0xffff00,
                    timestamp=datetime.datetime.utcnow()
                )
                em.set_footer(text="Considered By {}".format(ctx.author), icon_url=ctx.author.avatar)
                await msg.edit(embed=em)
                await ctx.send("Suggestion {} has been considered with the reason: {}".format(suggestion,reason))
                break
            else:
                continue


def setup(bc):
    bc.add_cog(ServerEvents(bc))