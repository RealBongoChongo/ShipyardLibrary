from . import ranks

fighter = [
    {
        "class": "Peregrine Class",
        "requirement": ranks.ensign
    }, 
    {
        "class": "Vanguard Interceptor",
        "requirement": ranks.ensign
    }, 
    {
        "class": "Class F Shuttle",
        "requirement": ranks.lieutenantJrGrade
    }
]

corvettesGunships = [
    {
        "class": "Hammer Class",
        "requirement": ranks.ensign
    },
    {
        "class": "Filo Class",
        "requirement": ranks.lieutenantJrGrade
    },
    {
        "class": "Hawk Class",
        "requirement": ranks.lieutenantJrGrade
    }
]

frigates = [
    {
        "class": "Resistance Class",
        "requirement": ranks.ensign
    }, 
    {
        "class": "Defiant Class",
        "requirement": ranks.lieutenantJrGrade
    }
]

cruisers = [
    {
        "class": "Cheyenne Refit",
        "requirement": ranks.lieutenantJrGrade
    },
    {
        "class": "Solar Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Ignis Class Battlecruiser",
        "requirement": ranks.lieutenant
    }, 
    {
        "class": "Thuraman Class",
        "requirement": ranks.lieutenantCommander
    },
    {
        "class": "Excelsior Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Dreadnought Excelsior Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Constitution Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Constitution Class Refit",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Yorktown Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Marksman Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Luna Class",
        "requirement": ranks.ensign
    },
    {
        "class": "Galaxy Class",
        "requirement": ranks.captain
    }
]

battleshipsCruisers = [
    {
        "class": "Kentaurus Class",
        "requirement": ranks.viceAdmiral
    },
    {
        "class": "Typhoon Class Battleship",
        "requirement": ranks.captain
    },
    {
        "class": "Nexus Class",
        "requirement": ranks.commander
    },
    {
        "class": "Inquiry Class Battlecruiser",
        "requirement": ranks.lieutenantCommander
    },
    {
        "class": "Kentucky Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Blasphemer Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Arrowhead Class",
        "requirement": ranks.lieutenantJrGrade
    },
    {
        "class": "Spearhead Class",
        "requirement": ranks.commander
    }
]

groundVehicles = [
    {
        "class": "Theseus Class",
        "requirement": ranks.ensign
    }, 
    {
        "class": "Skystrike Class",
        "requirement": ranks.lieutenant
    }, 
    {
        "class": "Sleipnir APC",
        "requirement": ranks.lieutenantJrGrade
    }, 
    {
        "class": "Vedala Class",
        "requirement": ranks.lieutenantJrGrade
    }
]

misc = [
    {
        "class": "Stallwart Class",
        "requirement": ranks.commander
    }, 
    {
        "class": "Deep Space K-7",
        "requirement": ranks.captain
    }, 
    {
        "class": "Drydock",
        "requirement": ranks.commander
    }, 
    {
        "class": "Intrepid Class",
        "requirement": ranks.lieutenant
    }, 
    {
        "class": "Worker Bee",
        "requirement": ranks.ensign
    },
    {
        "class": "Deep Space 9",
        "requirement": ranks.rearAdmiralLH
    }, 
    {
        "class": "Eternity Class",
        "requirement": ranks.lieutenant
    },
    {
        "class": "Huey Class",
        "requirement": ranks.lieutenant
    }
]


def getShipFromName(name, lst):
	for ship in lst:
		if ship["class"] == name:
			return ship