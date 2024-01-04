import discord
import asyncio
import traceback
from . import trello
from . import jsonhandler

class RoleHierarchy(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__()

    async def initialize(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Add in any extra rank roles: \n\n" + "\n".join(["<@&{}>".format(rank[0]) for rank in sorted(jsonhandler.getRanks().items(), key=lambda x: x[1])]), view=self)

    @discord.ui.role_select()
    async def selectrole(self, select: discord.ui.Select, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        jsonhandler.insertRankData(select.values[0].id, interaction.guild.roles.index(discord.utils.get(interaction.guild.roles, id=select.values[0].id)))
        await interaction.response.edit_message(content="Add in any extra rank roles: \n\n" + "\n".join(["<@&{}>".format(rank[0]) for rank in sorted(jsonhandler.getRanks().items(), key=lambda x: x[1])]), view=self)

    @discord.ui.button(label="Confirm")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        
        view = RequisitionSelect(self.author)
        await interaction.response.edit_message(content="Choose which channel you want requests to go to", view=view)

class RankRoles(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__()
        self.index = 0

    async def initialize(self, interaction: discord.Interaction, labels):
        self.labels = labels
        jsonhandler.clearRankData()
        await interaction.response.edit_message(content="Choose the roles to the corresponding label you want it to go to.\n\n{}".format(self.labels[self.index]["name"]), view=self)

    @discord.ui.role_select()
    async def selectrank(self, select: discord.ui.Select, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        
        if select.values[0].id in jsonhandler.getLabels().keys():
            await interaction.response.send_message(content="You cannot have the same role for a different label", ephemeral=True)
            return await interaction.response.edit_message(content="Choose the roles to the corresponding label you want it to go to.\n\n{}".format(self.labels[self.index]["name"]), view=self)

        jsonhandler.insertLabelData(self.labels[self.index]["id"], select.values[0].id)
        jsonhandler.insertRankData(select.values[0].id, interaction.guild.roles.index(discord.utils.get(interaction.guild.roles, id=select.values[0].id)))

        self.index += 1

        if self.index == len(self.labels):
            view = RoleHierarchy(self.author)
            await view.initialize(interaction)
            return

        await interaction.response.edit_message(content="Choose the roles to the corresponding label you want it to go to.\n\n{}".format(self.labels[self.index]["name"]), view=self)

class RankLabels(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__()
        self.index = 0
        self.ranklabels = []

    async def initialize(self, interaction: discord.Interaction):
        self.labels = [label for label in await trello.getLabels()]
        await interaction.edit_original_response(content="Choose which labels are rank requirements.\n\n{}".format(self.labels[self.index]["name"]), view=self)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        self.ranklabels.append(self.labels[self.index])
        self.index += 1
        if self.index == len(self.labels):
            view = RankRoles(self.author)
            await view.initialize(interaction, self.ranklabels)
        await interaction.response.edit_message(content="Choose which labels are rank requirements.\n\n{}".format(self.labels[self.index]["name"]), view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        self.index += 1
        if self.index == len(self.labels):
            view = RankRoles(self.author)
            await view.initialize(interaction, self.ranklabels)
            return 
        await interaction.response.edit_message(content="Choose which labels are rank requirements.\n\n{}".format(self.labels[self.index]["name"]), view=self)

class RequisitionSelect(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__(timeout=None)
        if jsonhandler.isInCache("requisitions"):
            button = discord.ui.Button(label="Skip")
            async def callback(interaction: discord.Interaction):
                if interaction.user != self.author:
                    return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
                modal = discord.ui.Modal(title="Namable Indicators")
                namable = discord.ui.InputText(label="Name of Namable Label Indicator")
                unnamable = discord.ui.InputText(label="Name of Unnamable Label Indicator")

                modal.add_item(namable)
                modal.add_item(unnamable)

                async def callback(interaction: discord.Interaction):
                    jsonhandler.insertCache("namable", modal.children[0].value)
                    jsonhandler.insertCache("unnamable", modal.children[1].value)
                    res = await trello.syncShips()
                    if type(res) == dict:
                        return await interaction.response.send_message(content=res["error"] + "\n\nDon't worry! You don't have to redo this process all you need to do is run /update.")
                    return await interaction.response.send_message(content="Thats it! To update your ships run /update.")

                modal.callback = callback
                await interaction.response.send_modal(modal)
            button.callback = callback
            self.add_item(button)

    @discord.ui.channel_select(channel_types=[discord.ChannelType.text])
    async def select_requisitions(self, select: discord.ui.Select, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        jsonhandler.insertCache("requisitions", select.values[0].id)
        modal = discord.ui.Modal(title="Namable Indicators")
        namable = discord.ui.InputText(label="Name of Namable Label Indicator")
        unnamable = discord.ui.InputText(label="Name of Unnamable Label Indicator")

        modal.add_item(namable)
        modal.add_item(unnamable)

        async def callback(interaction: discord.Interaction):
            jsonhandler.insertCache("namable", modal.children[0].value)
            jsonhandler.insertCache("unnamable", modal.children[1].value)
            res = await trello.syncShips()
            if type(res) == dict:
                return await interaction.response.send_message(content=res["error"] + "\n\nDon't worry! You don't have to redo this process all you need to do is run /update.")
            return await interaction.response.send_message(content="Thats it! To update your ships run /update.")

        modal.callback = callback
        await interaction.response.send_modal(modal)

class Setup(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, author):
        self.author = author
        super().__init__(timeout=None)
        self.index = 0
        self.interaction = interaction
        self.reset = False

    async def initialize(self):
        self.lists = await trello.getLists()
        self.accepted = []
        if jsonhandler.shipsInList():
            button = discord.ui.Button(label="Skip", row=1)
            async def callback(interaction: discord.Interaction):
                if interaction.user != self.author:
                    return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
                view = RankLabels(self.author)
                await view.initialize(interaction)
            button.callback = callback
            self.add_item(button)
        await self.interaction.followup.send(content="Choose which lists contain requisitionable ships.\n\n{}".format(self.lists[self.index]["name"]), view=self)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self.reset:
            self.reset = True
            jsonhandler.clearShipList()
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        jsonhandler.addShipList(self.lists[self.index]["name"], self.lists[self.index]["id"])
        self.accepted.append(self.lists[self.index]["name"])
        self.index += 1
        if self.index == len(self.lists):
            view = RankLabels(self.author)
            await view.initialize(interaction)
            jsonhandler.clearUnwanted(self.accepted)
        await interaction.response.edit_message(content="Choose which lists contain requisitionable ships.\n\n{}".format(self.lists[self.index]["name"]), view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self.reset:
            self.reset = True
            jsonhandler.clearShipList()
        if interaction.user != self.author:
            return await interaction.response.send_message("This interaction is not for you", ephemeral=True)
        self.index += 1
        if self.index == len(self.lists):
            view = RankLabels(self.author)
            await view.initialize(interaction)
        await interaction.response.edit_message(content="Choose which lists contain requisitionable ships.\n\n{}".format(self.lists[self.index]["name"]), view=self)