import json

def lookup(memberId):
    with open("json/library.json", "r") as f:
        data = json.load(f)
    try:
        return data[str(memberId)]
    except KeyError:
        return None

def lookupclass(shipClass):
    with open("json/library.json", "r") as f:
        data = json.load(f)

    final = []

    for user, lib in data.items():
        for ship in lib["ships"]:
            if ship["class"].lower().startswith(shipClass.lower()):
                shipdata = ship
                shipdata["owner"] = lib["username"]

                final.append(shipdata)

    return final

def reverseLookup(registry):
    with open("json/library.json", "r") as f:
        data = json.load(f)

    for user, lib in data.items():
        for ship in lib["ships"]:
            if ship["registry"] == registry:
                return ship, lib["username"]

    return None, None

def isInCache(memberId):
    with open("json/cache.json", "r") as f:
        data = json.load(f)
    try:
        return data[str(memberId)]
    except KeyError:
        return None

def insertCache(memberId, username):
    with open("json/cache.json", "r") as f:
        data = json.load(f)
        
    data[str(memberId)] = username

    with open("json/cache.json", "w") as f:
        json.dump(data, f, indent=4)

def getRequests():
    with open("json/requests.json", "r") as f:
        data = json.load(f)
    
    return data["requests"]

def genID():
    with open("json/requests.json", "r") as f:
        data = json.load(f)

    return max(list(map(int, data["requests"].keys()))) + 1

def makeRequest(req, reqId):
    with open("json/requests.json", "r") as f:
        data = json.load(f)
    
    data["requests"][str(reqId)] = req

    with open("json/requests.json", "w") as f:
        json.dump(data, f, indent=4)

def delRequest(reqId):
    with open("json/requests.json", "r") as f:
        data = json.load(f)
    
    data["requests"].pop(reqId)

    with open("json/requests.json", "w") as f:
        json.dump(data, f, indent=4)

def setReady(reqId, distributorId):
    with open("json/requests.json", "r") as f:
        data = json.load(f)
    
    data["requests"][reqId]["ready"] = True
    data["requests"][reqId]["distributor"] = distributorId

    with open("json/requests.json", "w") as f:
        json.dump(data, f, indent=4)

def requestedClass(member, shipClass):
    for reqId, ship in getRequests().items():
        if ship["class"] == shipClass and ship["member"] == member.id:
            return True

    return False

def insertShip(member, ship):
    with open("json/library.json", "r") as f:
        data = json.load(f)
    
    if str(member.id) not in data:
        data[str(member.id)] = {}
        data[str(member.id)]["username"] = ship["username"]
        data[str(member.id)]["ships"] = []

    data[str(member.id)]["ships"].append({"registry": ship["registry"], "name": ship["name"], "class": ship["class"], "type": ship["type"]})

    with open("json/library.json", "w") as f:
        json.dump(data, f, indent=4)

def deleteShip(registry):
    with open("json/library.json", "r") as f:
        data = json.load(f)

    for user, lib in data.items():
        for ship in lib["ships"]:
            if ship["registry"] == registry:
                data[user]["ships"].remove(ship)

    with open("json/library.json", "w") as f:
        json.dump(data, f, indent=4)

def deleteShipClass(member, shipClass):
    with open("json/library.json", "r") as f:
        data = json.load(f)
        
    for ship in data[str(member.id)]["ships"]:
        if ship["class"].lower().startswith(shipClass.lower()):
            data[str(member.id)]["ships"].remove(ship)
            break

    with open("json/library.json", "w") as f:
        json.dump(data, f, indent=4)

def addShipList(name, labelid):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    data[name] = {}
    data[name]["label"] = labelid
    data[name]["ships"] = []

    with open("json/ships.json", "w") as f:
        json.dump(data, f, indent=4)

def clearShipList():
    with open("json/ships.json", "r") as f:
        data = json.load(f)
    
    data = {}

    with open("json/ships.json", "w") as f:
        json.dump(data, f, indent=4)

def clearUnwanted(accepted):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    for category in data.keys():
        if category not in accepted:
            data.pop(category)

    with open("json/ships.json", "w") as f:
        json.dump(data, f, indent=4)

def clearShipList():
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    data = {}

    with open("json/ships.json", "w") as f:
        json.dump(data, f, indent=4)

def shipsInList():
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    if data:
        return True
    return False

def getCategoryData():
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    return data

def getCategories():
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    return data.keys()

def insertRankData(rankId, hierarchy):
    with open("json/ranks.json", "r") as f:
        data = json.load(f)

    data[str(rankId)] = hierarchy

    with open("json/ranks.json", "w") as f:
        json.dump(data, f, indent=4)

def clearRankData():
    with open("json/ranks.json", "w") as f:
        json.dump({}, f, indent=4)

def getRanks():
    with open("json/ranks.json", "r") as f:
        data = json.load(f)

    return data

def insertLabelData(labelId, rankId):
    with open("json/labels.json", "r") as f:
        data = json.load(f)

    data[labelId] = rankId

    with open("json/labels.json", "w") as f:
        json.dump(data, f, indent=4)

def getLabels():
    with open("json/labels.json", "r") as f:
        data = json.load(f)

    return data

def setShips(listName, ships):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    data[listName]["ships"] = ships

    with open("json/ships.json", "w") as f:
        json.dump(data, f, indent=4)

def getCategoryId(name):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    return data[name]["label"]

def getShips(listName):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    return data[listName]["ships"]

def getShipNames(listName):
    with open("json/ships.json", "r") as f:
        data = json.load(f)

    names = []

    for ship in data[listName]["ships"]:
        names.append(ship["name"])

    return names

def getRequirementFromName(shipName, shipList):
    for ship in shipList:
        if ship["name"] == shipName:
            return ship["rankReq"]

def getRequirementRoleFromName(shipName, shipList):
    for ship in shipList:
        if ship["name"] == shipName:
            for role, req in getRanks().items():
                if req == ship["rankReq"]:
                    return role

def getShipFromName(shipName, shipList):
    for ship in shipList:
        if ship["name"] == shipName:
            return ship

    return None

def checkRemind(member, now):
    with open("json/reminders.json", "r") as f:
        data = json.load(f)
    
    if str(member) not in data:
        timestamp(member, now)
        return True

    elif now >= data[str(member)] + (86400 * 1):
        timestamp(member, now + (86400 * 1))
        return True

    return False

def timestamp(member, timestamp):
    with open("json/reminders.json", "r") as f:
        data = json.load(f)

    data[str(member)] = timestamp

    with open("json/reminders.json", "w") as f:
        json.dump(data, f, indent=4)

def setNotifs(member, val):
    with open("json/settings.json", "r") as f:
        data = json.load(f)

    data[str(member)] = val

    with open("json/settings.json", "w") as f:
        json.dump(data, f, indent=4)

def notifsEnabled(member):
    with open("json/settings.json", "r") as f:
        data = json.load(f)

    if str(member) in data:
        if data[str(member)]:
            return True
        return False
    return True