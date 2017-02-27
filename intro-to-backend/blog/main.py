# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import re
import string
import random

import webapp2
import jinja2

import hashlib

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Rot13(Handler):
    def get(self):
        self.render("rot13.html")

    def post(self):
        rot13 = ""
        text = self.request.get("text")
        if text:
            rot13 = text.encode('rot13')
        self.render("rot13.html", rotted = rot13)
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return EMAIL_RE.match(email)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Implement the function valid_pw() that returns True if a user's password 
# matches its hash. You will need to modify make_pw_hash.

def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s%s' % (h, salt)

def valid_pw(name, pw, h):
    hval = h[0:len(h)-5]
    salt = h[-5:]
    if hashlib.sha256(name + pw + salt).hexdigest() == hval:
        return True

def make_cookie_hash(value):
    salt = make_salt()
    h = hashlib.sha256(value + salt).hexdigest()
    return '%s%s' % (h, salt)

def valid_cookie(value, h): 
    hval = h[0:len(h)-5]
    salt = h[-5:]
    if hashlib.sha256(value + salt).hexdigest() == hval:
        return True

class SignUp(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        user = self.request.get("username")
        pword1 = self.request.get("password")
        pword2 = self.request.get("verify")
        email = self.request.get("email")

        user_error = ""
        pword1_error = ""
        pword2_error = ""
        email_error = ""

        if user:
            if valid_username(user):
                if db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % user).get():
                    user_error = "That username already exists!"
                    user = ""
            else:
                user_error = "That's not a valid username!"
        else:
            user_error = "Field can't be blank!"

        password = ""
        if pword1:
            if valid_password(pword1):
                if pword2:
                    if pword1 == pword2:
                        password = pword1
                    else:
                        pword2_error = "Passwords didn't match!"
                else:
                    pword2_error = "Field can't be blank!"
            else:
                pword1_error = "That wasn't a valid password!"
        else:
            pword1_error = "Field can't be blank!"

        if email:
            if not valid_email(email):
                email_error = "That's not a valid email!"

        if user_error or pword1_error or pword2_error or email_error:
            self.render("signup.html", username = user, password = password, email = email, user_error = user_error, pword1_error = pword1_error, pword2_error = pword2_error, email_error = email_error)
        else:
            new_user = Users(username = user, passhash = make_pw_hash(user, password))
            new_user.put()
            uid = str(new_user.key().id())
            self.response.headers.add_header('Set-Cookie', 'user_id=%s|%s; Path=/' % (uid, make_cookie_hash(uid)))
            self.redirect("/welcome")
            

class Login(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        user = self.request.get("username")
        password = self.request.get("password")

        if valid_username(user) and valid_password(password):
            user_details = db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % user).get()
            if user_details:
                if valid_pw(user, password, user_details.passhash):
                    uid = str(user_details.key().id())
                    self.response.headers.add_header('Set-Cookie', 'user_id=%s|%s; Path=/' % (uid, make_cookie_hash(uid)))
                    self.redirect("/welcome")
                else:
                    user = ""
                    password = ""
                    error = "Invalid login"
                    self.render("login.html", password = password, username = user, error = error)
            else:
                user = ""
                password = ""
                error = "Invalid login"
                self.render("login.html", password = password, username = user, error = error)
        else:
            user = ""
            password = ""
            error = "Invalid login"
            self.render("login.html", password = password, username = user, error = error)

class Logout(Handler):
    def get(self):
        self.response.delete_cookie("user_id")
        self.redirect("/signup")

class Welcome(Handler):
    def get(self):
        uid_cookie = self.request.cookies.get("user_id")
        if uid_cookie:
            uid_split = uid_cookie.split('|')
            if valid_cookie(uid_split[0], uid_split[1]):
                uid = int(uid_split[0])
                user = Users.get_by_id(uid)
                username = user.username
                self.render("welcome.html", username = username)
            else:
                self.redirect("/signup")
        else:
            self.redirect("/signup")

class Users(db.Model):
    username = db.StringProperty(required = True)
    passhash = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    email = db.StringProperty(required = False)

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        self.render("front.html", blogposts = blogposts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_new_post(self, title="", content="", error=""):
        self.render("newpost.html", title = title, content = content, error = error)

    def get(self):
        self.render_new_post()

    def post(self):
        title = self.request.get("post-title")
        content = self.request.get("post-content")

        if title and content:
            b = BlogPost(title = title, content = content)
            b.put()
            id = str(b.key().id())
            self.redirect("/"+id)

        else:
            render_new_post(title=title, content=content, error="Subject AND content please!")

class Permalink(Handler):
    def render_permapage(self, post_id):
        permapost = BlogPost.get_by_id(int(post_id))
        # # post_id = int(post_id)
        # if permapost:
        self.render("permapage.html", title = permapost.title, content = permapost.content, created = permapost.created, post_id = post_id)
        # else:
        #     self.response.out.write("Blog post not found!")

    def get(self, id):
        self.render_permapage(id)


urlrequests = [
    ('/', MainPage),
    ('/newpost', NewPost),
    (r'/(\d+)', Permalink),
    ('/signup', SignUp),
    ('/welcome', Welcome),
    ('/login', Login),
    ('/logout', Logout)
    ]

app = webapp2.WSGIApplication(urlrequests, debug=True)
