
from google.appengine.ext import db

class Player(db.Model):
    user = db.UserProperty(auto_current_user_add=True)
    name = db.StringProperty(default="")
    capital = db.IntegerProperty()

class Land(db.Model):
    x = db.IntegerProperty()
    y = db.IntegerProperty()
    value = db.IntegerProperty()

class ResourceType(db.Model):
    name = db.StringProperty(default="")
    valueHalfLife = db.IntegerProperty()

class Resource(db.Model):
    land = db.ReferenceProperty(Land)
    resourceType = db.ReferenceProperty(ResourceType)
    quantity = db.IntegerProperty()
    birthTimeStamp = db.DateTimeProperty()

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

class BuildingType(db.Model):
    name = db.StringProperty(default="")
    #inputResources = db.ListProperty(ResourceCombination)
    #outputResources = db.ListProperty(ResourceCombination)
    workDuration = db.IntegerProperty()
    constructionDuration = db.IntegerProperty()
    #upgradeableTo = db.ReferenceProperty(Building)

class ResourceType(db.Model):
    resource = db.ReferenceProperty(Resource)
    quantity = db.IntegerProperty()
    type = db.StringProperty() #input or output
    buildingType = db.ReferenceProperty(BuildingType)

class Building(db.Model):
    resource = db.ReferenceProperty(Land)
    buildingType = db.ReferenceProperty(BuildingType)
    buildingState = db.StringProperty()
    lastEvent = db.DateTimeProperty()

class OrderBook(db.Model):
    player = db.ReferenceProperty(Player)
    transactionType = db.StringProperty()
    resource = db.ReferenceProperty(Resource)
    quantity = db.IntegerProperty()
    offeredPrice = db.IntegerProperty()
    offerExpireTimestamp = db.DateTimeProperty()
    isDivisible = db.BooleanProperty()
