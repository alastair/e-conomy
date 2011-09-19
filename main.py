#!/usr/bin/env python
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from google.appengine.api import users
import cgi
import logging

import os
import os.path

from model import *

class RenderedHandler(webapp.RequestHandler):
    def getPlayer(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        q = db.GqlQuery("SELECT * FROM Player WHERE user = :1", user)
        return q.get()

    def render(self, templatefile, data):
        path = os.path.join(os.path.dirname(__file__), "templates", templatefile)
        self.response.out.write(template.render(path, data))

class MainHandler(RenderedHandler):
    def getDefaultCapital(self):
        return 1000

    def get(self):
        user = users.get_current_user()
        if not user:
            data = {
                "login_url": users.create_login_url(self.request.uri)
            }
            self.render("index.html", data)
            return

        numLand = 0
        landList = []
        buildingList = []

        player = self.getPlayer()
        if not player:
            player = Player()
            player.name = user.nickname()
            player.capital = self.getDefaultCapital()
            player.put()

        landList = Land.all()
        landList.filter("owner =", player)
        numLand = landList.count()
        for l in landList:
            bld = Building.all()
            bld.filter("land =",l)
            for b in bld:
                buildingList.append(b)
        
        resourceList = []
        for l in landList:
            res = Resource.all()
            res.filter("land =",l)
            for r in res:
                resourceList.append(r)

        resourceTypeList = ResourceType.all()
        resourceTypeList = sorted(resourceTypeList, key=lambda r: r.name)

        offers = Offer.all()
	offers.filter('quantity >', 0)

        data = {"money": player.capital,
                "username": player.name,
                "login_url": users.create_login_url(self.request.uri),
                "logout_url": users.create_logout_url(self.request.uri),
                "user": user,
                "numberLand": numLand,
                "land": landList,
                "buildings": buildingList,
                "resources": resourceList,
                "resourceTypes": resourceTypeList,
                "offers": offers
                }
 
        self.render("index.html", data)

class BuyHandler(RenderedHandler):
    def getValueOfLand(self, land):
        return 100

    def buyLand(self, player, value):
        if player.capital < value:
            return
        l = Land()
        l.value = value
        l.owner = player
        l.put()
        player.capital -= value
        player.put()

    def post(self):
        player = self.getPlayer()
        self.buyLand(player, self.getValueOfLand(1))
        self.redirect("/")

# Handler to get name change information, store it, and redirect back to the homepage
class UserHandler(RenderedHandler):
    def post(self):
        player = self.getPlayer()
        player.name = cgi.escape(self.request.get("username"))
        player.put()
        self.redirect("/")

class OrderHandler(RenderedHandler):
    def makeOffer(self, transactType, player, item, unitprice, quantity, delivery):
        o = Offer()
        o.player = player
        o.transactionType = transactType
        o.resourceType = ResourceType.get_by_id(item)
        o.quantity = quantity
        o.offeredPrice = unitprice
	o.deliveryLand = Land.get_by_id(delivery)
        # XXX: expiry, isDivisible
        o.put()

    def matchOffer(self, transactType, player, item, unitprice, quantity, delivery=None):
	user = users.get_current_user()
        resType = ResourceType.get_by_id(item)
        matchType = ''
	transDirection = 1 # Currency is always deducted from 'player' and added to 'otherParty'

	r = Offer.all()
        if transactType == "buy":
            matchType = 'sell'
	    r.order('offeredPrice')
	else:
            matchType = 'buy'
	    r.order('-offeredPrice')
	    transDirection = -1

        r.filter('resourceType =', resType)
        r.filter('transactionType =', matchType)

	offers = []
	for of in r:
	    if of.player.key() == player.key():
		continue
	    offers.append(of)

	toFulfill = quantity
	for o in offers:
	    if toFulfill == 0:
		break

	    if transactType == 'buy' and o.offeredPrice > unitprice:
		break

	    if transactType == 'sell' and o.offeredPrice < unitprice:
		break

	    # We have an acceptable offer. Now grab as many as we can up to
	    # quantity, reducing the quantity available in the offer.
	    if o.quantity == 0:
		continue

	    nFilled = 0

	    if toFulfill >= o.quantity:
		toFulfill = toFulfill - o.quantity
		q = o.quantity
		nFilled = q
		o.quantity = 0
		o.put()
		t = Transaction()
		t.offer = o
		t.otherParty = o.player
		t.actualQuantity = q
		t.actualPrice = o.offeredPrice
		t.put()

	    if toFulfill < o.quantity:
		o.quantity = o.quantity - toFulfill
		o.put()
		nFilled = toFulfill
		t = Transaction()
		t.offer = o
		t.otherParty = o.player
		t.actualQuantity = toFulfill
		t.actualPrice = o.offeredPrice
		t.put()
		toFulfill = 0

	    if transactType == 'sell':
		self.doCurrencyTransfer(nFilled * o.offeredPrice, o.player, player)
	    else:
		self.doCurrencyTransfer(nFilled * o.offeredPrice, player, o.player)

	return toFulfill

    def doResourceTransfer(self,resource,quantity,destination):
	if resource.quantity <= quantity:
	    resource.land = destination
	    resource.put()
	else:
	    # We need to split the resource
	    newres = Resource()
	    newres.land = destination
	    newres.quantity = quantity
	    newres.birthTimeStamp = resource.birthTimeStamp
	    newres.resourceType = resource.resourceType
	    resource.quantity = resource.quantity - quantity
	    newres.put()
	    resource.put()

    def doCurrencyTransfer(self,amount,src,target):
	src.capital = src.capital - amount
	target.capital = target.capital + amount
	src.put()
	target.put()	   
 
    def post(self):
        player = self.getPlayer()
        orderType = cgi.escape(self.request.get("order"))
        if orderType == "place offer":
            # sell
            quantity = cgi.escape(self.request.get("sell_quantity"))
            unitprice = cgi.escape(self.request.get("sell_unitprice"))
            item = cgi.escape(self.request.get("sell_item"))
	    f = self.matchOffer("sell", player, int(item), int(unitprice), int(quantity), int(delivery))
	    if f > 0:
		self.makeOffer("sell", player, int(item), int(unitprice), f)
        elif orderType == "place order":
            # buy
            quantity = cgi.escape(self.request.get("buy_quantity"))
            unitprice = cgi.escape(self.request.get("buy_unitprice"))
            item = cgi.escape(self.request.get("buy_item"))
	    delivery = cgi.escape(self.request.get("delivery_loc"))
	    f = self.matchOffer("buy", player, int(item), int(unitprice), int(quantity), int(delivery))
	    if f > 0:
		self.makeOffer("buy", player, int(item), int(unitprice), f, int(delivery))
        self.redirect("/")

class CreateHandler(RenderedHandler):
    def get(self):
        l = Land()
        l.put()
        rt = ResourceType()
        rt.put()
        r = Resource()
        r.put()
        lr = LandResources()
        lr.put()
        lt = LandType()
        lt.put()
        bt = BuildingType()
        bt.put()
        rc = ResourceCombination()
        rc.put()
        b = Building()
        b.put()
        ob = Transaction()
        ob.put()

def main():
    handlers = [
        ("/user", UserHandler),
        ("/", MainHandler),
        ("/make", CreateHandler),
        ("/buy", BuyHandler),
        ("/order", OrderHandler)
    ]
    application = webapp.WSGIApplication(handlers,
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
