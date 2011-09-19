
from google.appengine.ext import db

class Player(db.Model):
    user = db.UserProperty(auto_current_user_add=True)
    name = db.StringProperty(default="")
    capital = db.IntegerProperty()

class Land(db.Model):
    owner = db.ReferenceProperty(Player)
    x = db.IntegerProperty()
    y = db.IntegerProperty()
    value = db.IntegerProperty()

class ResourceType(db.Model):
    name = db.StringProperty(default="")
    valueHalfLife = db.IntegerProperty()

class Inventory(db.Model):
    player = db.ReferenceProperty(Player)
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()

#class Resource(db.Model):
#    land = db.ReferenceProperty(Land)
#    resourceType = db.ReferenceProperty(ResourceType)
#    quantity = db.IntegerProperty()
#    birthTimeStamp = db.DateTimeProperty()

class LandResources(db.Model):
    land = db.ReferenceProperty(Land)
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()
    growthRate = db.FloatProperty()
    exploitationRate = db.FloatProperty()
    maximumQuantity = db.IntegerProperty()

class LandType(db.Model):
    land = db.ReferenceProperty(Land)
    minGrowthRate = db.FloatProperty()
    maxGrowthRate = db.FloatProperty()
    minExploitationRate = db.FloatProperty()
    maxExploitationRate = db.IntegerProperty()
    maxMaximumQuantity = db.IntegerProperty()

class BuildingType(db.Model):
    name = db.StringProperty(default="")
    workDuration = db.IntegerProperty()
    constructionDuration = db.IntegerProperty()
    #upgradeableTo = db.ReferenceProperty(Building)

# This gives more information to a building type - 
# an input resource, output resource, how much it takes to make
class ResourceCombination(db.Model):
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()
    type = db.StringProperty() #input or output
    buildingType = db.ReferenceProperty(BuildingType)

class Building(db.Model):
    land = db.ReferenceProperty(Land)
    buildingType = db.ReferenceProperty(BuildingType)
    buildingState = db.StringProperty()
    lastEvent = db.DateTimeProperty()

# an offer to buy or sell a quantity at a price
class Offer(db.Model):
    player = db.ReferenceProperty(Player)
    transactionType = db.StringProperty() # buy/sell
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()
    offeredPrice = db.IntegerProperty()
    offerExpireTimestamp = db.DateTimeProperty()
    isDivisible = db.BooleanProperty()
    deliveryLand = db.ReferenceProperty(Land)

# A completed transaction
class Transaction(db.Model):
    offer = db.ReferenceProperty(Offer)
    otherParty = db.ReferenceProperty(Player)
    actualQuantity = db.IntegerProperty()
    actualPrice = db.IntegerProperty()
