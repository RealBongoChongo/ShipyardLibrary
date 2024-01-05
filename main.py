import discord
import os

os.chdir("/home/bongo/Downloads/ShipyardLib")

from utility import jsonhandler
from utility import viewhandler
from utility import ranks
from utility import trello
from utility import trellosetup
from utility.communication import WebsocketClient
from discord.ext import commands, tasks
from threading import Thread
import webserver
import ast
import traceback
import sys
import json
import requests
import discordmongo
import motor.motor_asyncio
import datetime

def getConfig(key):
    with open("config.json", "r") as f:
        data = json.load(f)

    return data[key]

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
bot = discord.Bot(intents=intents)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def insert_returns(self,body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    @commands.slash_command(description="Instructions to use bot (real)")
    async def help(self, ctx):
        await ctx.respond("""To use the </requisition:1048023212002398278> command: 

Step 1. Choose the Ship Category and Ship Class that you want
Step 2. If your ship is eligible, choose what kind of registry you want (NCC or NX)
Step 3. If your ship is eligible, you will be given a prompt to enter your ship name and registry ***(DO NOT PUT USS OR NCC BEFORE THE NAME AND REGISTRY)***
Step 4. Your ship is sent to Ship Distributors and you will be dmed if your ship is ready to pick up or denied

To lookup ships:

Head to https://bank.federationfleet.xyz/ufp/library, authenticate with discord, and you can search ships and whatnot""")

    @commands.slash_command(description="Lookup ships/ship owner")
    async def lookup(self, ctx):
        await ctx.respond("Lookup command moved to <https://bank.federationfleet.xyz/ufp/library>")

    @commands.slash_command(description="Requisition a ship")
    async def requisition(self, ctx):
        await ctx.defer()
        view = viewhandler.ShipSelectorView(ctx.author)
        
        await ctx.respond("Choose a ship!", view=view)

    @commands.slash_command(description="Decommision a ship (Only for senior officers)")
    async def decommission(self, ctx, registry=None, member:discord.Member=None, shipclass=None):
        await ctx.respond("One second...")

        if registry:
            jsonhandler.deleteShip(registry)
        if shipclass:
            jsonhandler.deleteShipClass(member, shipclass)
        await ctx.respond("Done.")

    @commands.slash_command(description="Bot Owner use only")
    async def run(self,ctx, *, cmd):
        whitelist = [485513915548041239]
        if ctx.author.id not in whitelist:
            return
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        self.insert_returns(body)
        env = {
            'bot': self.bot,
            'guild': ctx.guild,
            'author': ctx.author,
            'channel': ctx.channel,
            'os': os,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__,
            'py': None
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
            if type(result) == discord.Message:
                return
            await ctx.respond(result)
        except Exception:
            await ctx.respond(traceback.format_exc(),delete_after=10)

    @commands.slash_command(description="Yes")
    async def ping(self, ctx):
        await ctx.respond("Ping")

    @commands.slash_command(description="restart")
    async def restart(self, ctx):
        if not ctx.author.id == 485513915548041239:
            return
        await ctx.defer()
        await ctx.respond("Restarting...")
        requests.get("http://localhost:6060/sydc")
        os.execv(sys.executable, ['python'] + sys.argv)


    @commands.slash_command(description="add ship to user")
    async def addship(self, ctx, member: discord.Member):
        view = viewhandler.ShipSelectorView(ctx.author, member)

        await ctx.respond("Choose a ship!", view=view)

    @commands.slash_command(description="Update your ship lists!")
    async def update(self, ctx):
        for rank in jsonhandler.getRanks().keys():
            jsonhandler.insertRankData(int(rank), ctx.guild.roles.index(discord.utils.get(ctx.guild.roles, id=int(rank))))
        await ctx.defer()
        res = await trello.syncShips()
        if type(res) == dict:
            return await ctx.respond(res["error"])
        await ctx.respond("Done!")

    @commands.slash_command(description="Toggle Notifications")
    async def notifications(self, ctx, val: bool):
        jsonhandler.setNotifs(ctx.author.id, val)
        await ctx.respond("Notifications turned {}".format("on" if val else "off"))

    @commands.slash_command(description="Setup the bot!")
    async def setup(self, ctx):
        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label="Insert Token", style=discord.ButtonStyle.success)
        modal = discord.ui.Modal(title="Insert Token", timeout=None)
        textinput = discord.ui.InputText(label="Trello Token")

        skip = discord.ui.Button(label="Skip")
        boardskip = discord.ui.Button(label="Skip")

        boardmodal = discord.ui.Modal(title="Insert Board ID", timeout=None)
        boardinput = discord.ui.InputText(label="Board ID")
        boardview = discord.ui.View(timeout=None)
        boardbutton = discord.ui.Button(label="Insert Board ID", style=discord.ButtonStyle.success)
        
        modal.add_item(textinput)
        boardmodal.add_item(boardinput)

        user = ctx.author

        async def validateToken(interaction: discord.Interaction):
            if interaction.user != user:
                return await interaction.response.send_message(content="This interaction is not for you", ephemeral=True)
            try:
                if modal.children[0].value:
                    valid = await trello.validate(modal.children[0].value)
                    if not valid:
                        return await interaction.response.edit_message(content="Token is invalid! Try Again.", view=view)

                    jsonhandler.insertCache("token", modal.children[0].value)
                await interaction.response.edit_message(content="Now choose the board ID containing all of your ship data\n\nHow to find Board ID: ", view=boardview, file=discord.File("img/boardid.png"))
            except Exception as e:
                await ctx.respond(e)

        async def validateBoard(interaction: discord.Interaction):
            if interaction.user != user:
                return await interaction.response.send_message(content="This interaction is not for you", ephemeral=True)
            try:
                await interaction.response.defer()
                if boardmodal.children[0].value:
                    valid = await trello.validateBoard(boardmodal.children[0].value)
                    if not valid:
                        return await interaction.response.edit_message(content="Board is invalid! Try Again.", view=boardview)

                    jsonhandler.insertCache("board", boardmodal.children[0].value)

                setup = trellosetup.Setup(interaction, user)
                await setup.initialize()
            except Exception as e:
                await ctx.respond(traceback.format_exc())

        modal.callback = validateToken
        boardmodal.callback = validateBoard

        skip.callback = validateToken
        boardskip.callback = validateBoard

        if jsonhandler.isInCache("token"):
            view.add_item(skip)

        if jsonhandler.isInCache("board"):
            boardview.add_item(boardskip)

        async def callback(interaction: discord.Interaction):
            if interaction.user != user:
                return await interaction.response.send_message(content="This interaction is not for you", ephemeral=True)
            try:
                await interaction.response.send_modal(modal)
            except Exception as e:
                await ctx.respond(e)

        async def boardcallback(interaction: discord.Interaction):
            if interaction.user != user:
                return await interaction.response.send_message(content="This interaction is not for you", ephemeral=True)
            try:
                await interaction.response.send_modal(boardmodal)
            except Exception as e:
                await ctx.respond(e)

        button.callback = callback
        view.add_item(button)

        boardbutton.callback = boardcallback
        boardview.add_item(boardbutton)

        await ctx.respond("Thank you for adding me into your server! First, in order to link my database into your ships, you must allow me to access reading (not writing) your trello boards.\n\nTo do so, you must use this link: https://trello.com/1/authorize?expiration=never&name=MyPersonalToken&scope=read&response_type=token&key=acf38fa17c781236965353f9e6e2b7c3\n\nAfter it shows you the token, please press the button below to enter your trello token.", view=view)

    @commands.slash_command(description="Purges request channel and reloads requests")
    async def reqrefresh(self,ctx):
        await ctx.defer()
        channel = discord.utils.get(ctx.guild.channels, id=1048401801843580970)
        def not_pinned(msg):
            return not msg.pinned
        await channel.purge(limit=100, check=not_pinned)
        for reqId, ship in jsonhandler.getRequests().items():
            with open("json/shippings.json", "r") as f:
                data = json.load(f)
            if "distributor" in ship:
                data[ship["class"]] = ship["distributor"]

                with open("json/shippings.json", "w") as f:
                    json.dump(data, f, indent=4)
            view = discord.ui.View(timeout=None)
            accept = discord.ui.Button(label="Ship Ready", custom_id="ready | {}".format(reqId), style=discord.ButtonStyle.success)
            deny = discord.ui.Button(label="Deny", custom_id="deny | {}".format(reqId), style=discord.ButtonStyle.danger)
            view.add_item(accept)
            view.add_item(deny)
            if ship["ready"]:
                claimed = discord.ui.Button(label="Claimed", custom_id="claimed | {}".format(reqId), style=discord.ButtonStyle.secondary, row=1)
                for child in view.children:
                    child.disabled = True
                view.add_item(claimed)

            embed = discord.Embed(
                title="Ship Info",
                description="Ship Class: {}\nShip Name: {}\nShip Registry: {}".format(ship["class"], "U.S.S. {}".format(ship["name"]), "{}-{}".format(ship["type"], ship["registry"])),
                color=0xff3300 
            )

            await channel.send("{}Request from: ".format("<@{}> ".format(data[ship["class"]] if ship["class"] in data else "<insert distributor here>") if not ship["ready"] else "") + ship["username"], embed=embed, view=view)
        await ctx.respond("Finished")

bot.add_cog(Commands(bot))

@bot.event
async def on_ready():

    guild = await bot.fetch_guild(878364507385233480)
    channel = await guild.fetch_channel(1051489091339956235)
    embed = discord.Embed(title="Library Status: Online", description="Shipyard Library now connected to discord", color=0xff3300)
    await channel.send("<@485513915548041239>", embed=embed)


@bot.event
async def on_presence_update(before, after):
    if before.status == discord.Status.offline and after.status != discord.Status.offline:
        if jsonhandler.checkRemind(before.id, datetime.datetime.now().timestamp()) and jsonhandler.notifsEnabled(before.id):
            jsonhandler.timestamp(before.id, datetime.datetime.now().timestamp())
        else:
            return
        guild = discord.utils.get(bot.guilds, id=878364507385233480)
        channel = discord.utils.get(guild.channels, id=1018566948759552010)

        ready = []
        cache = {}
        for reqId, ship in jsonhandler.getRequests().items():
            if ship["ready"] and ship["member"] == before.id:
                user = discord.utils.get(guild.members, id=ship["member"])
                
                ready.append(ship["class"])
                cache[ship["class"]] = await guild.fetch_member(ship["distributor"])
        if ready:
            await channel.send("{} don't forget to claim {}".format(before.mention,", ".join(["`{} (@{})`".format(ship, cache[ship].name) for ship in ready])))

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.is_component():
        try:
            await interaction.response.defer()
        except:
            pass
        try:
            if not len(interaction.custom_id.split(" | ")) == 2:
                return
            if not interaction.user.get_role(1012070243004321802):
                return await interaction.response.send_message(content="You aren't a ship distributor", ephemeral=True)
            typeButton, index = interaction.custom_id.split(" | ")[0], interaction.custom_id.split(" | ")[1]
            if not index in jsonhandler.getRequests():
                return await interaction.delete_original_response()
            ship = jsonhandler.getRequests()[index]
            user = interaction.guild.get_member(ship["member"])
            if not user: 
                await interaction.guild.fetch_member(ship["member"])
            
            if typeButton == "ready":
                try:
                    await user.send("Your `{}` ship is now ready! Report to {}".format(ship["class"], interaction.user.mention))
                except Exception as e:
                    channel = discord.utils.get(interaction.guild.channels, id=1018566948759552010)
                    await channel.send("{} Your `{}` ship is now ready! Report to {}".format(user.mention, ship["class"], interaction.user.mention))
                message = await interaction.original_response()
                claimed = discord.ui.Button(label="Claimed", custom_id="claimed | {}".format(index), style=discord.ButtonStyle.secondary, row=1)
                view = discord.ui.View.from_message(message)
                for child in view.children:
                    child.disabled = True
                view.add_item(claimed)
                await message.edit(content=message.content, embed=message.embeds[0], view=view)
                jsonhandler.setReady(index, interaction.user.id)
            elif typeButton == "deny":
                jsonhandler.delRequest(index)
                try:
                    await user.send("Your request for the `{}` ship has been denied by {}.".format(ship["class"], interaction.user.mention))
                    await interaction.delete_original_response()
                except Exception as e:
                    channel = discord.utils.get(interaction.guild.channels, id=1018566948759552010)
                    await channel.send("{} Your request for the `{}` ship has been denied by {}.".format(user.mention, ship["class"], interaction.user.mention))
                    await interaction.delete_original_response()
            elif typeButton == "claimed":
                jsonhandler.insertShip(user, ship)
                jsonhandler.delRequest(index)
                await interaction.delete_original_response()
        except Exception as e:
            error = discord.utils.get(interaction.guild.channels, id=1051489091339956235)
            await error.send(traceback.format_exc())
    else:
        await bot.process_application_commands(interaction)

@bot.event
async def on_member_update(before, after):
    guild = await bot.fetch_guild(878364507385233480)
    distributor = discord.utils.get(guild.roles, id=1012070243004321802)

    if before.roles != after.roles:
        if not distributor in before.roles and distributor in after.roles:
            channel = await guild.fetch_channel(1018566948759552010)
            await channel.send("{}\n\nhttps://docs.google.com/document/d/1ahdT_VAv0BkbzgjscKnPPMThGhJciK9DfVIhmkRB79I/edit?usp=sharing".format(before.mention))

bot.websiteSocket = WebsocketClient()
Thread(target=bot.websiteSocket.start).start()

Thread(target=webserver.run).start()
bot.run(getConfig("token"))