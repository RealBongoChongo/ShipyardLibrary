import aiohttp
from . import jsonhandler

base_url = "https://api.trello.com/1"

async def validate(token):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + "/members/me/boards", params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": token}) as r:
            return True if r.status == 200 else False

async def validateBoard(boardId):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + "/boards/{}".format(boardId), params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": jsonhandler.isInCache("token")}) as r:
            return True if r.status == 200 else False

async def getLists():
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + "/boards/{}/lists".format(jsonhandler.isInCache("board")), params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": jsonhandler.isInCache("token")}) as r:
            return await r.json()

async def getLabels():
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + "/boards/{}/labels".format(jsonhandler.isInCache("board")), params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": jsonhandler.isInCache("token")}) as r:
            return await r.json()

async def getShips(listId):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + "/lists/{}/cards".format(listId), params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": jsonhandler.isInCache("token")}) as r:
            return [ship["name"] for ship in await r.json()]

async def syncShips():
    async with aiohttp.ClientSession() as session:
        for category in jsonhandler.getCategories():
            async with session.get(base_url + "/lists/{}/cards".format(jsonhandler.getCategoryData()[category]["label"]), params={"key": "acf38fa17c781236965353f9e6e2b7c3", "token": jsonhandler.isInCache("token")}) as r:
                print(await r.read())
                cardData = await r.json()

                final = []

                for card in cardData:
                    hierarchy = None
                    unnamable = None
                    for label in card["labels"]:
                        if label["id"] in jsonhandler.getLabels():
                            role = jsonhandler.getLabels()[label["id"]]

                            hierarchy = jsonhandler.getRanks()[str(role)]

                        if label["name"] == jsonhandler.isInCache("unnamable"):
                            unnamable = True
                        elif label["name"] == jsonhandler.isInCache("namable"):
                            unnamable = False

                    if unnamable == None or hierarchy == None:
                        return {"error": card["name"] + " has no indicating labels for requirements" if not hierarchy else card["name"] + " has no indicating labels for being namable"}

                    shipdata = {"rankReq": hierarchy, "name": card["name"], "unnamable": unnamable}

                    final.append(shipdata)

                final = sorted(final, key=lambda ship: ship["rankReq"])

                jsonhandler.setShips(category, final)
    return True

def getRankFromLabel(label):
    labels = jsonhandler.getLabels()

    try:
        role = labels[label]
        hierarchy = jsonhandler.getRanks()[str(role)]
    except:
        hierarchy = None

    return hierarchy