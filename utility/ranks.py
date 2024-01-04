import discord
from . import jsonhandler

ranks = [
    878368140759797850, 
    914732053789040660,
    878367994009505833,
    914732221611515904,
    878367891559448589,
    878367800937304146,
    940456287496470578,
    1022239558093512825,
    940456210799411220,
    878367592706887761,
    940455959858413658
]

pips = [
    "<:pip1:1048963012960206878>",
    "<:pip2:1048963014214299668><:pip1:1048963012960206878>",
    "<:pip1:1048963012960206878><:pip1:1048963012960206878>",
    "<:pip2:1048963014214299668><:pip1:1048963012960206878><:pip1:1048963012960206878>",
    "<:pip1:1048963012960206878><:pip1:1048963012960206878><:pip1:1048963012960206878>",
    "<:pip1:1048963012960206878><:pip1:1048963012960206878><:pip1:1048963012960206878><:pip1:1048963012960206878>",
    "<:ralh1:1048965587725983834><:ralh2:1048965588833284106><:ralh3:1048965590007681045>",
    "<:rauh1:1048966466948567130><:rauh2:1048966467837775963><:rauh3:1048966469393842196>",
    "<:va1:1048968459767263353><:va2:1048968461168169001><:va3:1048968641955233792>",
    "<:ad1:1048970029460377640><:ad2:1048970030697697411><:ad3:1048970032127934554><:ad4:1048970033264611389>",
    "<:fa1:1048970520256839751><:fa2:1048970521473196072><:fa3:1048970522551144558><:fa4:1048970523834581035><:fa5:1048970525709451424>"
]

"""

ranks = [
    1048050341033279518,
    929152915933892658,
    929152900310118420,
    1048050460851974204,
    1048050551532830861,
    1048050610546692157,
    1048050737659265106,
    1048050881142214716,
    1048050921969561600,
    1048050878470438933
]
"""
ensign = ranks[0]
lieutenantJrGrade = ranks[1]
lieutenant = ranks[2]
lieutenantCommander = ranks[3]
commander = ranks[4]
captain = ranks[5]
rearAdmiralLH = ranks[6]
rearAdmiralUH = ranks[7]
viceAdmiral = ranks[8]
admiral = ranks[9]
fleetAdmiral = ranks[10]

def checkRank(member, guild, requirement):
    roles = member.roles
    for role in roles:
        if str(role.id) in jsonhandler.getRanks():
            if guild.roles.index(discord.utils.get(guild.roles, id=role.id)) >= requirement:
                return True

    return False

def checkIfFull(member):
    roles = member.roles
    for role in roles:
        if str(role.id) in jsonhandler.getRanks():
            return ((jsonhandler.getRanks()[str(role.id)] - min(jsonhandler.getRanks().values())) + 1) * 2

def getPips(member):
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            return pips[ranks.index(role.id)]

    return False