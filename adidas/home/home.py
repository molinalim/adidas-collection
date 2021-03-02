from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import adidas.adapters.repository as repo
import adidas.utilities.utilities as utilities
import adidas.products.services as services
import adidas.authentication.services as a_services
import adidas.authentication.authentication
import adidas.products.services as p_services

from adidas.authentication.authentication import login_required

home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return products_by_name(form)
    return render_template(
        'home/home.html',
        selected_products=utilities.get_selected_products(),
        product_urls=utilities.get_names_and_urls(),
        form=form
    )


@home_blueprint.route('/products_by_name', methods=['GET', 'POST'])
def products_by_name(form):
    name = form.name.data
    products_per_page = 3

    # Read query parameters.
    cursor = request.args.get('cursor')
    product_to_show_comments = request.args.get('view_comments_for')

    if product_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent product id.
        product_to_show_comments = -1
    else:
        # Convert product_to_show_comments from string to int.
        product_to_show_comments = int(product_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve product ids for product with genre_name.
    product_ids = services.get_product_ids_by_name(name, repo.repo_instance)

    # Retrieve the batch of products to display on the Web page.
    products = services.get_products_by_id(product_ids[cursor:cursor + products_per_page], repo.repo_instance)

    first_product_url = None
    last_product_url = None
    next_product_url = None
    prev_product_url = None

    if cursor > 0:
        # There are preceding products, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_product_url = url_for('home_bp.products_by_name', name=name, cursor=cursor - products_per_page)
        first_product_url = url_for('home_bp.products_by_name', name=name)

    if cursor + products_per_page < len(product_ids):
        # There are further products, so generate URLs for the 'next' and 'last' navigation buttons.
        next_product_url = url_for('home_bp.products_by_name', name=name, cursor=cursor + products_per_page)

        last_cursor = products_per_page * int(len(product_ids) / products_per_page)
        if len(product_ids) % products_per_page == 0:
            last_cursor -= products_per_page
        last_product_url = url_for('home_bp.products_by_name', name=name, cursor=last_cursor)

    # Construct urls for viewing product comments and adding comments.
    for product in products:
        product['view_comment_url'] = url_for('home_bp.products_by_name', name=name, cursor=cursor,
                                              view_comments_for=product['id'])
        product['add_comment_url'] = url_for('products_bp.comment_on_product', product=product['id'])
        product['add_to_collection'] = url_for('home_bp.add_to_collection', product=product['id'])
        product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])

    # Generate the webpage to display the products.
    return render_template(
        'products/products.html',
        title='Products',
        products=products,
        form=form,
        products_title='Product name: ' + name,
        selected_products=utilities.get_selected_products(len(products) * 2),
        handler_url=url_for('home_bp.products_by_name'),
        name_urls=utilities.get_names_and_urls(),
        brand_urls=utilities.get_brands_and_urls(),
        first_product_url=first_product_url,
        last_product_url=last_product_url,
        prev_product_url=prev_product_url,
        next_product_url=next_product_url,
        show_comments_for_product=product_to_show_comments,
    )


@home_blueprint.route('/collection', methods=['GET', 'POST'])
@login_required
def collection():
    # Obtain the username of the currently logged in user.
    username = session['username']
    user = a_services.get_user(username, repo.repo_instance)
    products = user['collection']
    for product in products:
        product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])

    return render_template(
        'products/collection.html',
        title='Collection of ' + username,
        collection=user['collection'],
        handler_url=url_for('products_bp.comment_on_product'),
        selected_products=utilities.get_selected_products(),
        brand_urls=utilities.get_brands_and_urls(),
        user=user
    )


@home_blueprint.route('/collection/added', methods=['GET', 'POST'])
@login_required
def add_to_collection():
    # Obtain the username of the currently logged in user.
    username = session['username']
    user = a_services.get_user(username, repo.repo_instance)
    product_id = request.args.get('product')
    product = p_services.get_product(product_id, repo.repo_instance)
    product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])
    if product not in user['collection']:
        user['collection'].append(product)

    return render_template(
        'products/collection.html',
        title='Collection of ' + username,
        collection=user['collection'],
        handler_url=url_for('products_bp.comment_on_product'),
        selected_products=utilities.get_selected_products(),
        brand_urls=utilities.get_brands_and_urls(),
        user=user
    )


@home_blueprint.route('/collection/removed', methods=['GET', 'POST'])
@login_required
def remove_from_collection():
    # Obtain the username of the currently logged in user.
    username = session['username']
    user = a_services.get_user(username, repo.repo_instance)
    product_id = request.args.get('product')
    product = p_services.get_product(product_id, repo.repo_instance)
    product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])
    if product in user['collection']:
        user['collection'].remove(product)
    return render_template(
        'products/collection.html',
        title='Collection of ' + username,
        collection=user['collection'],
        handler_url=url_for('products_bp.comment_on_product'),
        selected_products=utilities.get_selected_products(),
        brand_urls=utilities.get_brands_and_urls(),
        user=user
    )


class SearchForm(FlaskForm):
    name = StringField('Name', [
        DataRequired()])
    submit = SubmitField('Search')
