from datetime import date, datetime
from typing import List

import pytest

from adidas.domain.model import User, Product, Brand, Comment, make_comment
from adidas.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('tobin')
    assert user == User('tobin', 'cLQ^C#oFXloS')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_product_count(in_memory_repo):
    number_of_products = in_memory_repo.get_number_of_products()

    # Check that the query returned 6 Articles.
    assert number_of_products == 2625


def test_repository_can_add_product(in_memory_repo):
    product = Product('EPIC SHOES', 'Very epic', 'www.google.com', 'www.google.com/image', '123', 12 , 2)
    in_memory_repo.add_product(product)

    assert in_memory_repo.get_product('123') is product


def test_repository_can_retrieve_product(in_memory_repo):
    product = in_memory_repo.get_product('AH2430')

    # Check that the Product has the expected name.
    assert product.name == 'Women\'s adidas Originals NMD_Racer Primeknit Shoes'

    # Check that the Product is commented as expected.
    comment_one = [comment for comment in product.comments if comment.comment == 'I really want this. Damn'][
        0]
    comment_two = [comment for comment in product.comments if comment.comment == 'Best product!'][0]

    assert comment_one.user.username == 'irem'
    assert comment_two.user.username == "tobin"

    # Check that the Product is branded as expected.
    assert product.is_branded_by(Brand('ORIGINALS'))


def test_repository_does_not_retrieve_a_non_existent_product(in_memory_repo):
    product = in_memory_repo.get_product(101)
    assert product is None


def test_repository_can_retrieve_products_by_price(in_memory_repo):
    products = in_memory_repo.get_products_by_price(2999)

    # Check that the query returned 3 Products.
    assert len(products) == 2


def test_repository_does_not_retrieve_an_product_when_there_are_no_products_for_a_given_price(in_memory_repo):
    products = in_memory_repo.get_products_by_price(0)
    assert len(products) == 0


def test_repository_can_retrieve_brands(in_memory_repo):
    brands: List[Brand] = in_memory_repo.get_brands()

    assert len(brands) == 3

    brand_one = [brand for brand in brands if brand.brand_name == 'ORIGINALS'][0]
    brand_two = [brand for brand in brands if brand.brand_name == 'CORE / NEO'][0]
    brand_three = [brand for brand in brands if brand.brand_name == 'SPORT PERFORMANCE'][0]

    assert brand_one.number_of_branded_products == 908
    assert brand_two.number_of_branded_products == 1111
    assert brand_three.number_of_branded_products == 606


def test_repository_can_get_first_product(in_memory_repo):
    product = in_memory_repo.get_first_product()
    assert product.name == 'Men\'s Originals Summer Adilette Slippers'


def test_repository_can_get_last_product(in_memory_repo):
    product = in_memory_repo.get_last_product()
    assert product.name == "Women's adidas ORIGINALS SUPERSTAR BOUNCE PK  Low Shoes"


def test_repository_can_get_products_by_ids(in_memory_repo):
    products = in_memory_repo.get_products_by_id(['EF9924', 'BC0980', 'CM6008'])

    assert len(products) == 3
    assert products[
               0].name == 'Men\'s adidas Basketball Harden Vol. 4 Shoes'
    assert products[1].name == "Unisex adidas Outdoor Terrex Daroga Water Shoes"
    assert products[2].name == 'Men\'s Cricket Cri Hase Shoes'


def test_repository_does_not_retrieve_product_for_non_existent_id(in_memory_repo):
    products = in_memory_repo.get_products_by_id([2, 9])

    assert len(products) == 2
    assert products[0] == None


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    products = in_memory_repo.get_products_by_id([0, 9])

    assert len(products) == 2
    assert products == [None, None]


def test_repository_returns_product_ids_for_existing_brand(in_memory_repo):
    product_ids = in_memory_repo.get_product_ids_for_brand('ORIGINALS')

    assert ['AH2430', 'G27341', 'D98205'] <= product_ids


def test_repository_returns_an_empty_list_for_non_existent_brand(in_memory_repo):
    product_ids = in_memory_repo.get_product_ids_for_brand('United States')

    assert len(product_ids) == 0


def test_repository_returns_price_of_previous_product(in_memory_repo):
    product = in_memory_repo.get_product('CM6008')
    previous_product = in_memory_repo.get_price_of_previous_product(product)

    assert previous_product == 3599


def test_repository_returns_none_when_there_are_no_previous_products(in_memory_repo):
    product = in_memory_repo.get_product('280648')
    previous_product = in_memory_repo.get_price_of_previous_product(product)

    assert previous_product is None


def test_repository_returns_price_of_next_product(in_memory_repo):
    product = in_memory_repo.get_product('280648')
    next_product = in_memory_repo.get_price_of_next_product(product)

    assert next_product == 4999


def test_repository_returns_none_when_there_are_no_subsequent_products(in_memory_repo):
    product = in_memory_repo.get_product('S82260')
    next_product = in_memory_repo.get_price_of_next_product(product)

    assert next_product is None


def test_repository_can_add_a_brand(in_memory_repo):
    brand = Brand('Motoring')
    in_memory_repo.add_brand(brand)

    assert brand in in_memory_repo.get_brands()


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('tobin')
    product = in_memory_repo.get_product('EF3505')
    comment = make_comment("WOOOOOOOW", user, product)

    in_memory_repo.add_comment(comment)

    assert comment in in_memory_repo.get_comments()


def test_repository_does_not_add_a_comment_without_a_user(in_memory_repo):
    product = in_memory_repo.get_product('EF3505')
    comment = Comment(None, product, "WOOOOOOOW", datetime.today())

    with pytest.raises(RepositoryException):
        in_memory_repo.add_comment(comment)


def test_repository_does_not_add_a_comment_without_an_product_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('tobin')
    product = in_memory_repo.get_product('EF3505')
    comment = Comment(None, product, "WOOOOOOOW", datetime.today())

    user.add_comment(comment)

    with pytest.raises(RepositoryException):
        # Exception expected because the Article doesn't refer to the Comment.
        in_memory_repo.add_comment(comment)


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_comments()) == 3



