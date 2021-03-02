from datetime import date

from adidas.domain.model import User, Product, Brand, make_comment, make_brand_association, ModelException

import pytest


@pytest.fixture()
def product():
    return Product('EPIC SHOES', 'Very epic', 'www.google.com', 'www.google.com/image', '123', 12 , 2)


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def brand():
    return Brand('New Zealand')


def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'

    for comment in user.comments:
        # User should have an empty list of Comments after construction.
        assert False


def test_product_construction(product):
    assert product.id is "123"
    assert product.name == 'EPIC SHOES'
    assert product.description == 'Very epic'
    assert product.hyperlink == 'www.google.com'
    assert product.image_hyperlink == 'www.google.com/image'

    assert product.number_of_comments == 0

    assert repr(
        product) == '<Product EPIC SHOES 12>'


def test_product_less_than_operator():
    product_1 = Product(
        'EPIC', None, None, None, '2', None, None
    )

    product_2 = Product(
        'Epic', None, None, None, '3', None, None
    )

    assert product_1 < product_2


def test_brand_construction(brand):
    assert brand.brand_name == 'New Zealand'

    for product in brand.branded_products:
        assert False

    assert not brand.is_applied_to(Product(None, None, None, None, None, None, None))


def test_make_comment_establishes_relationships(product, user):
    comment_text = 'ADIDASSSS!'
    comment = make_comment(comment_text, user, product)

    # Check that the User object knows about the Comment.
    assert comment in user.comments

    # Check that the Comment knows about the User.
    assert comment.user is user

    # Check that Product knows about the Comment.
    assert comment in product.comments

    # Check that the Comment knows about the Product.
    assert comment.product is product


def test_make_brand_associations(product, brand):
    make_brand_association(product, brand)

    # Check that the product knows about the brand.
    assert product.is_branded()
    assert product.is_branded_by(brand)

    # check that the brand knows about the product.
    assert brand.is_applied_to(product)
    assert product in brand.branded_products


def test_make_brand_associations_with_product_already_branded(product, brand):
    make_brand_association(product, brand)

    with pytest.raises(ModelException):
        make_brand_association(product, brand)
