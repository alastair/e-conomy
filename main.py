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
    def render(self, templatefile, data):
        path = os.path.join(os.path.dirname(__file__), "templates", templatefile)
        self.response.out.write(template.render(path, data))

class MainHandler(RenderedHandler):
    def get(self):
        user = users.get_current_user()

        n = ""
        if user:
            q = db.GqlQuery("SELECT * FROM Player WHERE user = :1", user)
            thisuser = q.get()
            if not thisuser:
                thisuser = Player()
                thisuser.put()
            if not thisuser.name:
                n = user
            else:
                n = thisuser.name
        data = {"money": 100,
                "username": n,
                "login_url": users.create_login_url(self.request.uri),
                "logout_url": users.create_logout_url(self.request.uri),
                "user": user
                }
        self.render("index.html", data)

# Handler to get name change information, store it, and redirect back to the homepage
class UserHandler(RenderedHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            logging.debug("redirect")
            self.redirect(users.create_login_url(self.request.uri))
        user = users.get_current_user()
        playerlist = Player.all()
        playerlist.filter("user =", user)
        thisplayer = playerlist.get()
        thisplayer.name = cgi.escape(self.request.get("username"))
        logging.debug("playername: %s", thisplayer.name)
        thisplayer.put()
        self.redirect("/")

def main():
    handlers = [
        ("/user", UserHandler),
        ("/", MainHandler)
    ]
    application = webapp.WSGIApplication(handlers,
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
