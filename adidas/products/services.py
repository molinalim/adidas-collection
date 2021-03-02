from typing import List, Iterable

from adidas.adapters.repository import AbstractRepository
from adidas.domain.model import make_comment, Product, Comment, Brand


class NonExistentProductException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(product_id: str, comment_text: str, username: str, repo: AbstractRepository):
    # Check that the product exists.
    product = repo.get_product(product_id)
    if product is None:
        raise NonExistentProductException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    comment = make_comment(comment_text, user, product)

    # Upprice the repository.
    repo.add_comment(comment)


def get_product(product_id: str, repo: AbstractRepository):
    product = repo.get_product(product_id)

    if product is None:
        raise NonExistentProductException

    return product_to_dict(product)


def get_first_product(repo: AbstractRepository):
    product = repo.get_first_product()

    return product_to_dict(product)


def get_last_product(repo: AbstractRepository):
    product = repo.get_last_product()
    return product_to_dict(product)


def get_products_by_price(price, repo: AbstractRepository):
    # Returns products for the target price (empty if no matches), the price of the previous product (might be null), the price of the next product (might be null)

    products = repo.get_products_by_price(target_price=price)

    products_dto = list()
    prev_price = next_price = None

    if len(products) > 0:
        prev_price = repo.get_price_of_previous_product(products[0])
        next_price = repo.get_price_of_next_product(products[0])

        # Convert Products to dictionary form.
        products_dto = products_to_dict(products)

    return products_dto, prev_price, next_price


def get_product_ids_for_brand(brand_name, repo: AbstractRepository):
    product_ids = repo.get_product_ids_for_brand(brand_name)

    return product_ids


def get_product_ids_by_name(name, repo: AbstractRepository):
    product_ids = repo.get_product_ids_by_name(name)

    return product_ids


def get_products_by_id(id_list, repo: AbstractRepository):
    products = repo.get_products_by_id(id_list)

    # Convert Products to dictionary form.
    products_as_dict = products_to_dict(products)

    return products_as_dict


def get_comments_for_product(product_id, repo: AbstractRepository):
    product = repo.get_product(product_id)

    if product is None:
        raise NonExistentProductException

    return comments_to_dict(product.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def product_to_dict(product: Product):
    product_dict = {
        'id': product.id,
        'price': product.price,
        'name': product.name,
        'description': product.description,
        'hyperlink': product.hyperlink,
        'image_hyperlink': product.image_hyperlink,
        'comments': comments_to_dict(product.comments),
        'brand': brand_to_dict(product.brand)
    }
    return product_dict


def products_to_dict(products: Iterable[Product]):
    return [product_to_dict(product) for product in products]


def comment_to_dict(comment: Comment):
    comment_dict = {
        'username': comment.user.username,
        'product_id': comment.product.id,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Comment]):
    return [comment_to_dict(comment) for comment in comments]


def brand_to_dict(brand: Brand):
    brand_dict = {
        'name': brand.brand_name,
        'branded_products': [product.id for product in brand.branded_products]
    }
    return brand_dict


def brands_to_dict(brands: Iterable[Brand]):
    return [brand_to_dict(brand) for brand in brands]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_product(dict):
    product = Product(dict.id, dict.price, dict.name, dict.description, dict.image_hyperlink, dict.hyperlink)
    # Note there's no comments or brands.
    return product
