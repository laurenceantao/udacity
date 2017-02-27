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

from string import letters
import re

import webapp2
import jinja2

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


class SignUp(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
    	user = self.request.get("username")
    	pword1 = self.request.get("pword1")
    	pword2 = self.request.get("pword2")
    	email = self.request.get("email")

    	if user:
	    	if valid_username(user):
	    		username_valid = user
	    	else:
	    		username_invalid = True
	    else:
	    	no_username = True
	    username = user

	    password = ""
    	if pword1:
    		if valid_password(pword1):
    			if pword2:
	    			if pword1 == pword2:
	    				password_valid = True
	    				password = pword1
	    			else:
	    				password_diff = True
	    		else:
	    			no_password2 = True
    		else:
    			password_invalid = True
    	else:
    		no_password1 = True

    	if email:
    		if not valid_email(email):
    			email_invalid = True

    	if username_valid and password_valid and not email_invalid:
    		self.redirect("/welcome?username="+username_valid)
    	else:
    		self.render("signup.html", username = username, username_invalid = username_invalid, no_username = no_username, password_diff = password_diff, password = password, password_invalid = password_invalid, no_password1 = no_password1, no_password2 = no_password2, email_valid = email_valid, email_invalid = email_invalid)

class Welcome(Handler):
    def get(self):
    	user = self.request.get("username")
        self.render("welcome.html", username = user)
        
app = webapp2.WSGIApplication([
    ('/rot13', Rot13), ('/signup', SignUp), ('/welcome', Welcome)], debug=True)
