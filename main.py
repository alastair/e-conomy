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

        data = {"money": player.capital,
                "username": player.name,
                "login_url": users.create_login_url(self.request.uri),
                "logout_url": users.create_logout_url(self.request.uri),
                "user": user,
                "numberLand": numLand,
                "land": landList,
                "buildings": buildingList,
		        "resources": resourceList
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
    def post(self):
        player = self.getPlayer()
        orderType = cgi.escape(self.request.get("order"))
        quantity = cgi.escape(self.request.get("quantity"))
        unitprice = cgi.escape(self.request.get("unitprice"))
        item = cgi.escape(self.request.get("item"))
        if orderType == "place offer":
            pass
        elif orderType == "place order":
            pass

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
