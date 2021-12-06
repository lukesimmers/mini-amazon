from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.generic_queries import *

class FullfillProductForm(FlaskForm):
    submit = SubmitField(_l('Fullfill The Adjustment'))

from flask import Blueprint
seller_inventory_bp = Blueprint('seller_inventory', __name__)
seller_orders_bp = Blueprint('seller_orders', __name__)
seller_order_details_bp = Blueprint('seller_order_details', __name__)
seller_page_bp = Blueprint('seller', __name__)
seller_product_fulfillment_bp = Blueprint('seller_product_fulfillment', __name__)

@seller_inventory_bp.route('/seller_inventory')
def seller_inventory():
   inventory = User.get_products(current_user.id) 
   return render_template('seller_inventory.html', inventory=inventory)

@seller_orders_bp.route('/seller_orders')
def seller_orders():
   orders = get_sellers_orders()
   fulfillDict = {}
   orders.sort(key = lambda x:x[1], reverse = True)

   for order in orders:
      purchases = get_sellers_order_details(order.oid)
      totalPrice = sum([purchase.price * purchase.quantity for purchase in purchases])
      Quant = sum([purchase.quantity for purchase in purchases])
      if seller_order_fulfilled(order.oid):
         fulfillDict[order.oid] = ('Fulfilled', totalPrice, Quant)
      else:
         fulfillDict[order.oid] = ('Not Fulfilled', totalPrice, Quant)
   

   return render_template('seller_orders.html', orders=orders, fulfillDict = fulfillDict)

@seller_order_details_bp.route('/seller_order_details/<oid>')
def seller_order_details(oid):
   order_id = oid
   orderer_info = get_order_purchase_details(oid)
   purchases = get_sellers_order_details(oid)
   print(purchases[-1][-1])
   print(type(purchases[-1][-1]))

   return render_template('seller_order_details.html', purchases=purchases, orderer_info= orderer_info, oid=order_id)


@seller_product_fulfillment_bp.route("/seller_product_fulfillment/<oid>/<pid>", methods=['GET', 'POST'])
def seller_product_fulfillment(oid, pid):
      fulfillProduct(oid,pid, "Fulfilled")
      return redirect(url_for('seller_order_details.seller_order_details', oid = oid))

@seller_page_bp.route("/seller/<id>")
def seller(id):
   reviews = get_seller_information(id)
   products = get_seller_products(id)
   return render_template('seller_page.html', reviews=reviews, seller=reviews[0], products=products)
