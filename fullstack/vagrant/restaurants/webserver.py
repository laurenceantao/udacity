from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

engine = create_engine('sqlite:///restaurants.db')

Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"
                output += "<p><a href='/restaurants/new'>Make a New Restaurant Here</a></p>"

                restos = session.query(Restaurant).all()
                for resto in restos:
                    output += "<article>"
                    output += "<p>%s</p>" % resto.name
                    output += "<p><a href='/restaurants/%s/edit'>edit</a></p>" % resto.id
                    output += "<p><a href='restaurants/%s/delete'>delete</a></p>" % resto.id
                    output += "</article>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                start = self.path.index("/restaurants/") + 13
                end = self.path.index("/edit")
                resto_id = int(self.path[start:end])
                resto = session.query(Restaurant).filter_by(id = resto_id).one()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>%s</h1>" % resto.name
                output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/'''
                output += str(resto_id)
                output += '''/edit"><input placeholder="'''
                output += resto.name
                output += '''" name="restaurant_rename" type="text" ><input type="submit" value="Rename"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/delete"):
                start = self.path.index("/restaurants/") + 13
                end = self.path.index("/delete")
                resto_id = int(self.path[start:end])
                resto = session.query(Restaurant).filter_by(id = resto_id).one()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?</h1>" % resto.name
                output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/'''
                output += str(resto_id)
                output += '''/delete"><input type="submit" value="Delete"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/new"><input placeholder="New Restaurant Name" name="restaurant_name" type="text" ><input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                fieldcontent = fields.get('restaurant_name')
                new_resto = Restaurant(name = fieldcontent[0])
                session.add(new_resto)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith("/edit"):
                start = self.path.index("/restaurants/") + 13
                end = self.path.index("/edit")
                resto_id = int(self.path[start:end])
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                fieldcontent = fields.get('restaurant_rename')
                restaurantQuery = session.query(Restaurant).filter_by(id = resto_id).one()
                restaurantQuery.name = fieldcontent[0]
                session.add(restaurantQuery)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith("/delete"):
                start = self.path.index("/restaurants/") + 13
                end = self.path.index("/delete")
                resto_id = int(self.path[start:end])
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                restaurant_to_delete = session.query(Restaurant).filter_by(id = resto_id).one()
                session.delete(restaurant_to_delete)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

        except:
            pass

# ## Test Case Populator
# for i in range(10):
#     new_restaurant = Restaurant(name = "Restaurant Number " + str(i))
#     session.add(new_restaurant)
#     session.commit()

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()