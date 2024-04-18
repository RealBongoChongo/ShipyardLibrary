import discord
import traceback
from . import ships
from . import ranks
from . import jsonhandler
import json

class ShipSelectorView(discord.ui.View):
    def __init__(self, author, member=None):
        super().__init__(timeout=None)

        self.author = author
        self.member = member
        self.shipSelector = ShipSelector(author, member)
        self.shipClassSelector = ShipClassSelector(author, self.shipSelector)
        self.add_item(self.shipClassSelector)
        self.add_item(self.shipSelector)

class ShipClassSelector(discord.ui.Select):
    def __init__(self, author, shipSelector):
        super().__init__(placeholder="Ship Category", options=[discord.SelectOption(label="yesnt")])
        self.shipSelector = shipSelector
        self.author = author
        self.options = [discord.SelectOption(label=listName) for listName in jsonhandler.getCategories()]

    async def callback(self, interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message("You cannot requisition a ship for this person!", ephemeral=True)
        self.shipSelector.load(self.values[0])
        if self.shipSelector.button:
            self.view.remove_item(self.shipSelector.button)
            self.shipSelector.button = None
        elif self.shipSelector.shipType:
            self.view.remove_item(self.shipSelector.shipType)
            self.shipSelector.shipType = None
        embed = discord.Embed(title=self.values[0] + " Requirements", description="\n".join(["{} - {}".format(ship["name"], "<@&{}>".format(jsonhandler.getRequirementRoleFromName(ship["name"], jsonhandler.getShips(self.values[0])))) for ship in jsonhandler.getShips(self.values[0])]), color=0xff3300)
        await interaction.response.edit_message(content="Choose a ship!", embed=embed, view=self.view)

class ShipSelector(discord.ui.Select):
    def __init__(self, author, member=None):
        self.lst = []
        self.option = None
        self.author = author
        self.member = member
        self.button = None
        self.shipType = None
        super().__init__(placeholder="Ship Class", disabled=True, options=[discord.SelectOption(label="yesnt")])

        self.ship = {"registry": None, "name": None, "class": None, "type": None}

    def load(self, option):
        self.option = option
        self.disabled = False

        self.lst = jsonhandler.getShips(option)
        self.options = [discord.SelectOption(label=ship) for ship in jsonhandler.getShipNames(option)]


    async def callback(self, interaction: discord.Interaction):
        member = self.member or interaction.user
        try:
            if not interaction.user == self.author:
                return await interaction.response.send_message("You cannot requisition a ship for this person!", ephemeral=True)
            canReq = ranks.checkRank(interaction.user, interaction.guild, jsonhandler.getRequirementFromName(self.values[0], self.lst))
            if not canReq:
                await interaction.response.send_message("You do not have the rank to requisition this ship!", ephemeral=True)
            else:
                if jsonhandler.requestedClass(member, self.values[0]):
                    return await interaction.response.send_message("You already requested a ship with this class!", ephemeral=True)
                self.ship["class"] = self.values[0]
                if not jsonhandler.getShipFromName(self.values[0], self.lst)["unnamable"]:
                    shipType = discord.ui.Select(placeholder="Ship Registry Type", options=[discord.SelectOption(label="NCC"), discord.SelectOption(label="NX")])
    
                    async def callback(interaction: discord.Interaction):
                        self.ship["type"] = self.shipType.values[0]
    
                        modal = discord.ui.Modal(title="Name Ship (do not put USS or NCC)", timeout=None)
                        shipName = discord.ui.InputText(label="Ship Name (No USS)", max_length=100)
                        shipRegistry = discord.ui.InputText(label="Ship Registry (No NCC/NX)", max_length=20)
                        
                        modal.add_item(shipName)
                        modal.add_item(shipRegistry)
    
                        if not jsonhandler.isInCache(member.id):
                            username = discord.ui.InputText(label="ROBLOX Username")
                            modal.add_item(username)
    
                        async def callback(interaction: discord.Interaction):
                            if jsonhandler.reverseLookup(modal.children[1].value)[0]:
                                for child in self.view.children:
                                    child.disabled = True
                                await interaction.response.edit_message(content="Choose a ship!", view=self.view)
                                await interaction.followup.send("A ship with that registry already exists!",ephemeral=True)
                                modal.failed = True
                            else:
                                if not interaction.user == self.author:
                                    return await interaction.response.send_message("You cannot requisition a ship for this person!", ephemeral=True)
                                for child in self.view.children:
                                    child.disabled = True
                                await interaction.response.edit_message(content="Choose a ship!", view=self.view)
                                await interaction.channel.send("Your ship is now being built and you will be dmed when it is ready!")
                                modal.failed = False
    
                        modal.callback = callback
                        await interaction.response.send_modal(modal)
    
                        await modal.wait()
                        
                        if modal.failed:
                            return

                        self.ship["name"] = modal.children[0].value
                        self.ship["registry"] = modal.children[1].value
                        self.ship["username"] = modal.children[2].value if not jsonhandler.isInCache(member.id) else jsonhandler.isInCache(member.id)
                        self.ship["member"] = member.id
                        self.ship["ready"] = False
    
                        if not jsonhandler.isInCache(member.id):
                            jsonhandler.insertCache(member.id, modal.children[2].value)
                        if not self.member:
                            view = discord.ui.View(timeout=None)
                            reqId = jsonhandler.genID()

                            accept = discord.ui.Button(label="Ship Ready", custom_id="ready | {}".format(reqId), style=discord.ButtonStyle.success)
                            deny = discord.ui.Button(label="Deny", custom_id="deny | {}".format(reqId), style=discord.ButtonStyle.danger)
                            jsonhandler.makeRequest(self.ship, reqId)
                            view.add_item(accept)
                            view.add_item(deny)
                            
                            embed = discord.Embed(
                                title="Ship Info",
                                description="Ship Class: {}\nShip Name: {}\nShip Registry: {}".format(self.values[0], "U.S.S. {}".format(self.ship["name"]) if self.ship["name"] else self.ship["name"], "{}-{}".format(self.ship["type"], self.ship["registry"])),
                                color=0xff3300
                            )

                            channel = discord.utils.get(interaction.guild.channels, id=jsonhandler.isInCache("requisitions"))
                            with open("json/shippings.json", "r") as f:
                                data = json.load(f)
                            await channel.send("{}Request from: ".format("<@{}> ".format(data[self.ship["class"]] if self.ship["class"] in data else "<insert distributor here>")) + jsonhandler.isInCache(member.id), embed=embed, view=view)
                        else:
                            jsonhandler.insertShip(member, self.ship)

                    if not self.shipType:
                        if self.button:
                            self.view.remove_item(self.button)
                            self.button = None
                        shipType.callback = callback
                        self.view.add_item(shipType)
                        self.shipType = shipType

                    await interaction.response.edit_message(content="Choose a ship!", view=self.view)
                else:
                    async def callback(interaction: discord.Interaction):
                        if not interaction.user == self.author:
                            return await interaction.response.send_message("You cannot requisition a ship for this person!", ephemeral=True)
                        for child in self.view.children:
                            child.disabled = True

                        if not jsonhandler.isInCache(member.id):
                            modal = discord.ui.Modal(title="Give Roblox Username", timeout=None)
                            username = discord.ui.InputText(label="ROBLOX Username")
                            modal.add_item(username)
    
                            async def callback(interaction: discord.Interaction):
                                await interaction.response.edit_message(content="Choose a ship!\n\nSelected Ship: {}".format(self.values[0]), view=self.view)
                                
                            modal.callback = callback
    
                            await interaction.response.send_modal(modal)
    
                            await modal.wait()
    
                            if not jsonhandler.isInCache(member.id):
                                jsonhandler.insertCache(member.id, modal.children[0].value)
                        else:
                            await interaction.response.edit_message(content="Choose a ship!\n\nSelected Ship: {}".format(self.values[0]), view=self.view)
    
                        self.ship["username"] = jsonhandler.isInCache(member.id)
                        self.ship["member"] = member.id
                        self.ship["ready"] = False
                        await interaction.channel.send(content="Your ship is now being built and you will be dmed when it is ready!")
                        if not self.member:
                            view = discord.ui.View(timeout=None)
                            reqId = jsonhandler.genID()

                            accept = discord.ui.Button(label="Ship Ready", custom_id="ready | {}".format(reqId), style=discord.ButtonStyle.success)
                            deny = discord.ui.Button(label="Deny", custom_id="deny | {}".format(reqId), style=discord.ButtonStyle.danger)
                            jsonhandler.makeRequest(self.ship, reqId)
                            view.add_item(accept)
                            view.add_item(deny)
        
                            embed = discord.Embed(
                                title="Ship Info",
                                description="Ship Class: {}\nShip Name: {}\nShip Registry: {}".format(self.values[0], "U.S.S. {}".format(self.ship["name"]), "{}-{}".format(self.ship["type"], self.ship["registry"])),
                                color=0xff3300
                            )
        
                            channel = discord.utils.get(interaction.guild.channels, id=jsonhandler.isInCache("requisitions"))
                            with open("json/shippings.json", "r") as f:
                                data = json.load(f)
                            await channel.send("{}Request from: ".format("<@{}> ".format(data[self.ship["class"]] if self.ship["class"] in data else "<insert distributor here>")) + jsonhandler.isInCache(member.id), embed=embed, view=view)
                        else:
                            jsonhandler.insertShip(member, self.ship)

                    if not self.button:
                        if self.shipType:
                            self.view.remove_item(self.shipType)
                            self.shipType = None
                        self.button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success)
                        self.button.callback = callback
                        self.view.add_item(self.button)
    
                    embed = discord.Embed(title=self.option + " Requirements", description="\n".join(["{} - {}".format(ship, "<@&{}>".format(jsonhandler.getRequirementRoleFromName(ship["name"], self.lst))) for ship in self.lst]), color=0xff3300)
                    await interaction.response.edit_message(content="Choose a ship!\n\nSelected Ship: {}".format(self.values[0]), view=self.view)
        except Exception as e:
            await interaction.channel.send(traceback.format_exc())
