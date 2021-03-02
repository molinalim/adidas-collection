from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import adidas.adapters.repository as repo
import adidas.utilities.utilities as utilities
import adidas.products.services as services
import adidas.authentication.services as a_services
import adidas.authentication.authentication

from adidas.authentication.authentication import login_required


# Configure Blueprint.
products_blueprint = Blueprint(
    'products_bp', __name__)


@products_blueprint.route('/products_by_price', methods=['GET'])
def products_by_price():
    # Read query parameters.
    target_price = request.args.get('price')
    product_to_show_comments = request.args.get('view_comments_for')

    # Fetch the first and last products in the series.
    first_product = services.get_first_product(repo.repo_instance)
    last_product = services.get_last_product(repo.repo_instance)

    if target_price is None:
        # No price query parameter, so return products from day 1 of the series.
        target_price = first_product['price']

    if product_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent product id.
        product_to_show_comments = -1
    else:
        # Convert product_to_show_comments from string to int.
        product_to_show_comments = int(product_to_show_comments)

    # Fetch product(s) for the target price. This call also returns the previous and next prices for products immediately
    # before and after the target price.
    products, previous_price, next_price = services.get_products_by_price(target_price, repo.repo_instance)

    first_product_url = None
    last_product_url = None
    next_product_url = None
    prev_product_url = None

    if len(products) > 0:
        # There's at least one product for the target price.
        if previous_price is not None:
            # There are products on a previous price, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_product_url = url_for('products_bp.products_by_price', price=previous_price)
            first_product_url = url_for('products_bp.products_by_price', price=first_product['price'])

        # There are products on a subsequent price, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_price is not None:
            next_product_url = url_for('products_bp.products_by_price', price=next_price)
            last_product_url = url_for('products_bp.products_by_price', price=last_product['price'])

        # Construct urls for viewing product comments and adding comments.
        for product in products:
            product['view_comment_url'] = url_for('products_bp.products_by_price', price=target_price,
                                                  view_comments_for=product['id'])
            product['add_comment_url'] = url_for('products_bp.comment_on_product', product=product['id'])
            product['add_to_collection'] = url_for('home_bp.add_to_collection', product=product['id'])
            product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])

        # Generate the webpage to display the products.
        return render_template(
            'products/products.html',
            title='Product',
            products_title=target_price,
            products=products,
            selected_products=utilities.get_selected_products(len(products) * 2),
            brand_urls=utilities.get_brands_and_urls(),
            first_product_url=first_product_url,
            last_product_url=last_product_url,
            prev_product_url=prev_product_url,
            next_product_url=next_product_url,
            show_comments_for_product=product_to_show_comments
        )

    # No products to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@products_blueprint.route('/products_by_brand', methods=['GET'])
def products_by_brand():
    products_per_page = 3

    # Read query parameters.
    brand_name = request.args.get('brand')
    cursor = request.args.get('cursor')
    product_to_show_comments = request.args.get('view_comments_for')

    if product_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent product id.
        product_to_show_comments = -1

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve product ids for products that are branded with brand_name.
    product_ids = services.get_product_ids_for_brand(brand_name, repo.repo_instance)

    # Retrieve the batch of products to display on the Web page.
    products = services.get_products_by_id(product_ids[cursor:cursor + products_per_page], repo.repo_instance)

    first_product_url = None
    last_product_url = None
    next_product_url = None
    prev_product_url = None

    if cursor > 0:
        # There are preceding products, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_product_url = url_for('products_bp.products_by_brand', brand=brand_name, cursor=cursor - products_per_page)
        first_product_url = url_for('products_bp.products_by_brand', brand=brand_name)

    if cursor + products_per_page < len(product_ids):
        # There are further products, so generate URLs for the 'next' and 'last' navigation buttons.
        next_product_url = url_for('products_bp.products_by_brand', brand=brand_name, cursor=cursor + products_per_page)

        last_cursor = products_per_page * int(len(product_ids) / products_per_page)
        if len(product_ids) % products_per_page == 0:
            last_cursor -= products_per_page
        last_product_url = url_for('products_bp.products_by_brand', brand=brand_name, cursor=last_cursor)

    # Construct urls for viewing product comments and adding comments.
    for product in products:
        product['view_comment_url'] = url_for('products_bp.products_by_brand', brand=brand_name, cursor=cursor,
                                              view_comments_for=product['id'])
        product['add_comment_url'] = url_for('products_bp.comment_on_product', product=product['id'])
        product['add_to_collection'] = url_for('home_bp.add_to_collection', product=product['id'])
        product['remove_from_collection'] = url_for('home_bp.remove_from_collection', product=product['id'])

    # Generate the webpage to display the products.
    return render_template(
        'products/products.html',
        name='Product',
        products_title='Product branded by ' + brand_name,
        products=products,
        selected_products=utilities.get_selected_products(len(products) * 2),
        brand_urls=utilities.get_brands_and_urls(),
        first_product_url=first_product_url,
        last_product_url=last_product_url,
        prev_product_url=prev_product_url,
        next_product_url=next_product_url,
        show_comments_for_product=product_to_show_comments
    )


@products_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_product():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an product id, when subsequently called with a HTTP POST request, the product id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the product id, representing the commented product, from the form.
        product_id = form.product_id.data

        # Use the service layer to store the product comment.
        services.add_comment(product_id, form.comment.data, username, repo.repo_instance)

        # Retrieve the product in dict form.
        product = services.get_product(product_id, repo.repo_instance)

        # Cause the web browser to display the page of all products that have the same brand as the commented product,
        # and display all comments, including the product comment.

        # return redirect(url_for('products_bp.products_by_brand', brand=product['brand'], view_comments_for=product_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the product id, representing the product to comment, from a query parameter of the GET request.
        product_id = request.args.get('product')

        # Store the product id in the form.
        form.product_id.data = product_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the product id of the product being commented from the form.
        product_id = form.product_id.data

    # For a GET or an unsuccessful POST, retrieve the product to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    product = services.get_product(product_id, repo.repo_instance)
    return render_template(
        'products/comment_on_product.html',
        title='Edit product',
        product=product,
        form=form,
        handler_url=url_for('products_bp.comment_on_product'),
        selected_products=utilities.get_selected_products(),
        brand_urls=utilities.get_brands_and_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    product_id = HiddenField("Product id")
    submit = SubmitField('Submit')



