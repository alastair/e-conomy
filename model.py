
from google.appendgine.ext import db

class Player(db.Model):
    user = db.UserPropert(auto_current_user_add=True)
    name = db.StringProperty(default="")
    capital = db.IntegerProperty()

class Land(db.Model):
    x = db.IntegerProperty()
    y = db.IntegerProperty()
    value = db.IntegerProperty()

class LandResources(db.Model):
    land = db.ReferenceProperty(Land)
    resource = db.ReferenceProperty(Resource)
    quantity = db.IntegerProperty()
    growthRate = db.FloatProperty()
    exploitationRate = db.FloatProperty()
    maximumQuantity = db.IntegerProperty()

class LandType(db.Model):
    resource = db.ReferenceProperty(Land)
    minGrowthRate = db.FloatProperty()
    maxGrowthRate = db.FloatProperty()
    minExploitationRate = db.FloatProperty()
    maxExploitationRate = db.IntegerProperty()
    maxMaximumQuantity = db.IntegerProperty()

class Building(db.Model):
    resource = db.ReferenceProperty(Land)
    buildingType = db.StringProperty()
    buildingState = db.StringProperty()
    lastEvent = db.DateTimeProperty()

class Resource(db.Model):
    land = db.ReferenceProperty(Land)
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()
    birthTimeStamp = db.DateTimeProperty()

class ResourceType(db.Model):
    name = db.StringProperty(default="")
    valueHalfLife = db.IntegerProperty()

class ResourceCombination(db.Model):
    resource = db.ReferenceType(Resource)
    quantity = db.IntegerProperty()

class BuildingType(db.Model):
    name = db.StringProperty(default="")
    inputResources = db.ListProperty(db.ReferenceType(ResourceCombination))
    outputResources = db.ListProperty(db.ReferenceType(ResourceCombination))
    workDuration = db.IntegerProperty()
    constructionDuration = db.IntegerProperty()
    upgradeableTo = db.ReferenceProperty(Building)

class OrderBook(db.Model):
    player = db.ReferenceProperty(Player)
    transactionType = db.StringProperty()
    resource = db.ReferenceProperty(Resource)
    quantity = db.IntegerProperty()
    offeredPrice = db.IntegerProperty()
    offerExpireTimestamp = db.DateTimeProperty()
    isDivisible = db.BooleanProperty()
