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
    def makeOffer(self, transactType, player, item, unitprice, quantity):
        o = Offer()
        o.player = player
        o.transactionType = transactType
        o.resourceType = ResourceType.get_by_id(item)
        o.quantity = quantity
        o.offeredPrice = unitprice
        # XXX: expiry, isDivisible
        o.put()

    def matchOffer(self, transactType, player, item, unitprice, quantity):
        resType = ResourceType.get_by_id(item)
        matchType = '';

        if transactType == "buy":
            matchType = 'sell'
	else:
            matchType = 'buy'

        # We want to look for any corresponding "sell" offers
        q = db.GqlQuery("SELECT * FROM Offer WHERE resourceType = :1 AND transactionType = :2 AND quantity >= :3", resType, matchType, quantity)
        r = q.get()

        if not r:
	    return False
        
        # FIXME: I have no idea how AppEngine works --gdpe, 4:09am 
	r.filter('user !=', player)

        if matchType == 'sell':
            # We've found a seller who will sell to us. Check the price is less than or equal to our offer.
            r.filter('offeredPrice <=', unitprice)
        else:
            r.filter('offeredPrice >=', unitprice)

	if r:
	    self.redirect("/existing-offer/" + str(r))
	else:
	    return False

    def post(self):
        player = self.getPlayer()
        orderType = cgi.escape(self.request.get("order"))
        if orderType == "place offer":
            # sell
            quantity = cgi.escape(self.request.get("sell_quantity"))
            unitprice = cgi.escape(self.request.get("sell_unitprice"))
            item = cgi.escape(self.request.get("sell_item"))
	    self.matchOffer("sell", player, int(item), int(unitprice), int(quantity))
            self.makeOffer("sell", player, int(item), int(unitprice), int(quantity))
        elif orderType == "place order":
            # buy
            quantity = cgi.escape(self.request.get("buy_quantity"))
            unitprice = cgi.escape(self.request.get("buy_unitprice"))
            item = cgi.escape(self.request.get("buy_item"))
	    self.matchOffer("buy", player, int(item), int(unitprice), int(quantity))
            self.makeOffer("buy", player, int(item), int(unitprice), int(quantity))
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
        ob = OrderBook()
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
