from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField
from wtforms.validators import ValidationError, DataRequired
from flask_babel import _, lazy_gettext as _l
import datetime

from .models.product_summary import ProductSummary
from .models.product_sellers import ProductSeller
from .models.product import Product
from .models.user import User
from .models.purchase import Purchase
from .models.generic_queries import *


from flask import Blueprint
bp = Blueprint('social', __name__)

class SellerReviewForm(FlaskForm):
    review = StringField(_l('Review'), validators = [DataRequired()])
    rating = SelectField(_l('Rating'), choices = [(1,1),(2,2),(3,3),(4,4),(5,5)],validators=[DataRequired()])
    submit2 = SubmitField(_l('Add Review'))

class UpdateSellerReviewForm(FlaskForm):
    review = StringField(_l('Review'), validators = [DataRequired()])
    rating = SelectField(_l('Rating'), choices = [(1,1),(2,2),(3,3),(4,4),(5,5)],validators=[DataRequired()])
    submit3 = SubmitField(_l('Update Review'))

class LookupByName(FlaskForm):
    firstname = StringField(_l('First Name'))
    lastname = StringField(_l('Last Name'))
    email = StringField(_l('Email'))
    submit = SubmitField(_l('Search'))
    

@bp.route('/social/<id>', methods=['GET', 'POST'])
def social(id):
    max_uid = User.max_user()
    if int(id) > int(max_uid) or int(id) < 1:
        flash('This user does not exist')
        return redirect(url_for('social.social', id=current_user.id))
    form = LookupByName()
    form2 = SellerReviewForm()
    form3 = UpdateSellerReviewForm()
    social = User.get(id)
    seller = User.is_seller(id)
    bought_from = False
    left_seller_review = False
    reviews = [0,1]
    products = None
    avg = 0
    if seller:
        reviews = get_seller_information(id)
        products = get_seller_products(id)
        sum = 0
        count = 0
        for rev in reviews:
            sum += rev.rating
            count += 1
        avg = sum/count
        if current_user.is_authenticated:
            purchases = Purchase.get_all_by_uid_since(
                current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
            for purchase in purchases:
                for seller in ProductSeller.get_all(purchase.pid):
                    if int(seller.id) == int(id):
                        bought_from = True
            for rev in reviews:
                if rev[0] == int(current_user.id):
                    left_seller_review = True
                    if request.method == 'GET':
                        form3 = UpdateSellerReviewForm(formdata = MultiDict({
                'review': i[3],
                'rating': i[2]
            }))
    
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        results = User.get_user_by_name(firstname, lastname, email)
        return render_template('social_search.html', firstname = firstname, lastname=lastname, email = email, results = results)
    
    if form2.submit2.data and form2.validate_on_submit():
        if add_seller_review(current_user.id,int(id), form2.review.data, int(form2.rating.data)):
            flash('You have successfully added a review for this product!')
        return redirect(url_for('social.social', id=current_user.id))
    if form3.submit3.data and form3.validate_on_submit():
        update_seller_review(current_user.id, int(id), form3.review.data, int(form3.rating.data))
        flash('You have successfully updated your review for this product!')
        return redirect(url_for('social.social', id=current_user.id))
    
    return render_template('social_page.html', 
    user=social, 
    is_seller=seller, 
    reviews=reviews, 
    seller=reviews[0], 
    products=products, 
    avg=avg, 
    form = form,
    form2 = form2,
    form3 = form3,
    bought_from = bought_from,
    left_review = left_seller_review)

