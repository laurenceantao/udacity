from flask import Flask, render_template, url_for, flash, request, redirect, jsonify
app = Flask(__name__)

import bleach

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
# items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
# item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

@app.route('/restaurants/JSON')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	for restaurant in restaurants:
		return jsonify(Restaurants=restaurant.serialize)

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurant/new', methods = ['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		new_restaurant = Restaurant(name = request.form['restaurant_name'])
		session.add(new_restaurant)
		session.commit()
		flash(u'New restaurant created!', 'success')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	if request.method == 'POST':
		if request.form['restaurant_name']:
			restaurant.name = request.form['restaurant_name']
			session.add(restaurant)
			session.commit()
			flash(u'Restaurant Edited!', 'success')
		else:
			flash(u'No changes made to restaurant', 'warning')
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editRestaurant.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	if request.method == "POST":
		session.delete(restaurant)
		session.commit()
		flash(u'Restaurant deleted', 'success')
		return redirect(url_for('showRestaurants'))
	else:
		flash(u'Once confirmed, action cannot be undone!', 'danger')
		return render_template('deleteRestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

	appetizers = []
	entrees = []
	desserts = []
	beverages = []
	other_courses = []

	for i in items:
		course = i.course
		if course=='Appetizer':
			appetizers.append(i)
		elif course=='Entree':
			entrees.append(i)
		elif course=='Dessert':
			desserts.append(i)
		elif course=='Beverage':
			beverages.append(i)
		else:
			other_courses.append(i)
	return render_template('menu.html', restaurant=restaurant, appetizers=appetizers, entrees=entrees, desserts=desserts, beverages=beverages, other_courses=other_courses)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	if request.method == 'POST':
		new_menu_item = MenuItem(name = request.form['dish_name'], course = request.form['dish_course'], description = request.form['dish_description'], price = request.form['dish_price'], restaurant_id = restaurant_id)
		session.add(new_menu_item)
		session.commit()
		flash(u'New menu item created!', 'success')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newMenuItem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	item = session.query(MenuItem).get(menu_id)
	edited = False
	if request.method == 'POST':
		if request.form['dish_name']:
			item.name = request.form['dish_name']
			edited = True
		if request.form['dish_price']:
			item.price = request.form['dish_price']
			edited = True
		if request.form['dish_course']:
			item.course = request.form['dish_course']
			edited = True
		if request.form['dish_description']:
			item.description = request.form['dish_description']
			edited = True

		if edited:
			session.add(item)
			session.commit()
			flash(u'Menu Item edited', 'success')
		else:
			flash(u'No changes made to Menu Item', 'warning')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editMenuItem.html', restaurant=restaurant, item=item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).get(restaurant_id)
	item = session.query(MenuItem).get(menu_id)
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash(u'Menu Item deleted', 'success')
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		flash(u'Once confirmed, action cannot be undone!', 'danger')
		return render_template('deleteMenuItem.html', restaurant=restaurant, item=item)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)