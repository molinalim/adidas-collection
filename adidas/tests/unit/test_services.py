from datetime import date

import pytest

from adidas.authentication.services import AuthenticationException
from adidas.products import services as products_services
from adidas.authentication import services as auth_services
from adidas.products.services import NonExistentProductException


def test_can_add_user(in_memory_repo):
    product_username = 'jz'
    product_password = 'abcd1A23'

    auth_services.add_user(product_username, product_password, in_memory_repo)

    user_as_dict = auth_services.get_user(product_username, in_memory_repo)
    assert user_as_dict['username'] == product_username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    username = 'tobin'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(username, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    product_username = 'pmccartney'
    product_password = 'abcd1A23'

    auth_services.add_user(product_username, product_password, in_memory_repo)

    try:
        auth_services.authenticate_user(product_username, product_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    product_username = 'pmccartney'
    product_password = 'abcd1A23'

    auth_services.add_user(product_username, product_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(product_username, '0987654321', in_memory_repo)


def test_can_add_comment(in_memory_repo):
    product_id = 'AH2430'
    comment_text = 'AAAAAAAAAA!'
    username = 'tobin'

    # Call the service layer to add the comment.
    products_services.add_comment(product_id, comment_text, username, in_memory_repo)

    # Retrieve the comments for the product from the repository.
    comments_as_dict = products_services.get_comments_for_product(product_id, in_memory_repo)

    # Check that the comments include a comment with the product comment text.
    assert next(
        (dictionary['comment_text'] for dictionary in comments_as_dict if dictionary['comment_text'] == comment_text),
        None) is not None


def test_cannot_add_comment_for_non_existent_product(in_memory_repo):
    product_id = 'AH24'
    comment_text = "what's that?"
    username = 'tobin'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(products_services.NonExistentProductException):
        products_services.add_comment(product_id, comment_text, username, in_memory_repo)


def test_cannot_add_comment_by_unknown_user(in_memory_repo):
    product_id = 'AH2430'
    comment_text = 'AAAAAAA'
    username = 'jin'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(products_services.UnknownUserException):
        products_services.add_comment(product_id, comment_text, username, in_memory_repo)


def test_can_get_product(in_memory_repo):
    product_id = 'AH2430'

    product_as_dict = products_services.get_product(product_id, in_memory_repo)

    assert product_as_dict['id'] == product_id
    assert product_as_dict['name'] == 'Women\'s adidas Originals NMD_Racer Primeknit Shoes'
    assert product_as_dict['description'] == "Channeling the streamlined look of an '80s racer, these shoes are updated with modern features. The foot-hugging adidas Primeknit upper offers a soft, breathable feel. The Boost midsole provides responsive comfort accented with a contrast-color EVA heel plug. Embroidered details add a distinctive finish."
    assert product_as_dict['hyperlink'] == 'https://shop.adidas.co.in/#!product/AH2430_nmd_racerpkw'
    assert product_as_dict['image_hyperlink'] == 'https://content.adidas.co.in/static/Product-AH2430/WOMEN_Originals_SHOES_LOW_AH2430_1.jpg'
    assert len(product_as_dict['comments']) == 3
    brand_name = product_as_dict['brand']['name']
    assert 'ORIGINALS' == brand_name


def test_cannot_get_product_with_non_existent_id(in_memory_repo):
    product_id = "B4"

    # Call the service layer to attempt to retrieve the Product.
    with pytest.raises(products_services.NonExistentProductException):
        products_services.get_product(product_id, in_memory_repo)


def test_get_first_product(in_memory_repo):
    product_as_dict = products_services.get_first_product(in_memory_repo)

    assert product_as_dict['id'] == '280648'


def test_get_last_product(in_memory_repo):
    product_as_dict = products_services.get_last_product(in_memory_repo)

    assert product_as_dict['id'] == 'S82260'


def test_get_products_by_price_with_one_price(in_memory_repo):
    target_price = 2999

    products_as_dict, prev_price, next_price = products_services.get_products_by_price(target_price, in_memory_repo)

    assert len(products_as_dict) == 2
    assert products_as_dict[0]['id'] == '280648'

    assert prev_price is None
    assert next_price == 4999


def test_get_products_by_price_with_non_existent_price(in_memory_repo):
    target_price = 2020

    products_as_dict, prev_price, next_price = products_services.get_products_by_price(target_price, in_memory_repo)

    # Check that there are no products priced 2020.
    assert len(products_as_dict) == 0


def test_get_products_by_id(in_memory_repo):
    target_product_ids = ["AH2430", "B44832"]
    products_as_dict = products_services.get_products_by_id(target_product_ids, in_memory_repo)

    # Check that 2 products were returned from the query.
    assert len(products_as_dict) == 2

    # Check that the product ids returned were "AH2430" and "B44832".
    product_ids = [product['id'] for product in products_as_dict]

    assert set(["AH2430", "B44832"]).issubset(product_ids)


def test_get_comments_for_product(in_memory_repo):
    comments_as_dict = products_services.get_comments_for_product("AH2430", in_memory_repo)

    # Check that 2 comments were returned for product with id "AH2430".
    assert len(comments_as_dict) == 3

    # Check that the comments relate to the product whose id is "AH2430".
    product_ids = [comment['product_id'] for comment in comments_as_dict]
    product_ids = set(product_ids)
    assert "AH2430" in product_ids and len(product_ids) == 1


def test_get_comments_for_non_existent_product(in_memory_repo):
    with pytest.raises(NonExistentProductException):
        comments_as_dict = products_services.get_comments_for_product("7", in_memory_repo)


def test_get_comments_for_product_without_comments(in_memory_repo):
    comments_as_dict = products_services.get_comments_for_product("B44832", in_memory_repo)
    assert len(comments_as_dict) == 0

