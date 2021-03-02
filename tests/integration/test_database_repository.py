from datetime import date, datetime

import pytest

from adidas.adapters.database_repository import SqlAlchemyRepository
from adidas.domain.model import User, Product, Brand, Comment, make_comment
from adidas.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')

    assert user2 == user and user2 is user


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('tobin')
    assert user == User('tobin', 'cLQ^C#oFXloS')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_product_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_products = repo.get_number_of_products()

    # Check that the query returned 2625 Products.
    assert number_of_products == 2625


def test_repository_can_add_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = Product('EPIC SHOES', 'Very epic', 'www.google.com', 'www.google.com/image', '123', 12 , 2)
    repo.add_product(product)

    assert repo.get_product('123') == product


def test_repository_can_retrieve_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product('AH2430')

    # Check that the Product has the expected name.
    assert product.name == "Women's adidas Originals NMD_Racer Primeknit Shoes"

    # Check that the Product is commented as expected.
    comment_one = [comment for comment in product.comments if comment.comment == 'I really want this. Damn'][
        0]
    comment_two = [comment for comment in product.comments if comment.comment == 'Best product!'][0]

    assert comment_one.user.username == 'irem'
    assert comment_two.user.username == "tobin"

    # Check that the Product is branded as expected.
    assert product.is_branded_by(Brand('ORIGINALS'))


def test_repository_does_not_retrieve_a_non_existent_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(201)
    assert product is None


def test_repository_can_retrieve_products_by_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    products = repo.get_products_by_date(date(2020, 3, 1))

    # Check that the query returned 3 Products.
    assert len(products) == 3

    # these products are no jokes...
    products = repo.get_products_by_date(date(2020, 4, 1))

    # Check that the query returned 5 Products.
    assert len(products) == 5


def test_repository_does_not_retrieve_an_product_when_there_are_no_products_for_a_given_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    products = repo.get_products_by_date(date(2020, 3, 8))
    assert len(products) == 0


def test_repository_can_retrieve_tags(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tags = repo.get_tags()

    assert len(tags) == 10

    tag_one = [tag for tag in tags if tag.tag_name == 'New Zealand'][0]
    tag_two = [tag for tag in tags if tag.tag_name == 'Health'][0]
    tag_three = [tag for tag in tags if tag.tag_name == 'World'][0]
    tag_four = [tag for tag in tags if tag.tag_name == 'Politics'][0]

    assert tag_one.number_of_tagged_products == 53
    assert tag_two.number_of_tagged_products == 2
    assert tag_three.number_of_tagged_products == 64
    assert tag_four.number_of_tagged_products == 1


def test_repository_can_get_first_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_first_product()
    assert product.name == 'Coronavirus: First case of virus in New Zealand'


def test_repository_can_get_last_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_last_product()
    assert product.name == 'Covid 19 coronavirus: Kiwi mum on the heartbreak of losing her baby in lockdown'


def test_repository_can_get_products_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    products = repo.get_products_by_id([2, 5, 6])

    assert len(products) == 3
    assert products[
               0].name == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'
    assert products[1].name == "Australia's first coronavirus fatality as man dies in Perth"
    assert products[2].name == 'Coronavirus: Death confirmed as six more test positive in NSW'


def test_repository_does_not_retrieve_product_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    products = repo.get_products_by_id([2, 209])

    assert len(products) == 1
    assert products[
               0].name == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    products = repo.get_products_by_id([0, 199])

    assert len(products) == 0


def test_repository_returns_product_ids_for_existing_tag(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product_ids = repo.get_product_ids_for_tag('Health')

    assert product_ids == [1, 2]


def test_repository_returns_an_empty_list_for_non_existent_tag(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product_ids = repo.get_product_ids_for_tag('United States')

    assert len(product_ids) == 0


def test_repository_returns_date_of_previous_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(6)
    previous_date = repo.get_date_of_previous_product(product)

    assert previous_date.isoformat() == '2020-03-01'


def test_repository_returns_none_when_there_are_no_previous_products(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(1)
    previous_date = repo.get_date_of_previous_product(product)

    assert previous_date is None


def test_repository_returns_date_of_next_product(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(3)
    next_date = repo.get_date_of_next_product(product)

    assert next_date.isoformat() == '2020-03-05'


def test_repository_returns_none_when_there_are_no_subsequent_products(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(177)
    next_date = repo.get_date_of_next_product(product)

    assert next_date is None


def test_repository_can_add_a_tag(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    tag = Brand('Motoring')
    repo.add_tag(tag)

    assert tag in repo.get_tags()


def test_repository_can_add_a_comment(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    product = repo.get_product(2)
    comment = make_comment("Trump's onto it!", user, product)

    repo.add_comment(comment)

    assert comment in repo.get_comments()


def test_repository_does_not_add_a_comment_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    product = repo.get_product(2)
    comment = Comment(None, product, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        repo.add_comment(comment)


def test_repository_can_retrieve_comments(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_comments()) == 3


def make_product(new_product_date):
    product = Product(
        new_product_date,
        'Coronavirus travel restrictions: Self-isolation deadline pushed back to give airlines breathing room',
        'The self-isolation deadline has been pushed back',
        'https://www.nzherald.co.nz/business/news/product.cfm?c_id=3&objectid=12316800',
        'https://th.bing.com/th/id/OIP.0lCxLKfDnOyswQCF9rcv7AHaCz?w=344&h=132&c=7&o=5&pid=1.7'
    )
    return product


def test_can_retrieve_an_product_and_add_a_comment_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Product and User.
    product = repo.get_product(5)
    author = repo.get_user('thorke')

    # Create a new Comment, connecting it to the Product and User.
    comment = make_comment('First death in Australia', author, product)

    product_fetched = repo.get_product(5)
    author_fetched = repo.get_user('thorke')

    assert comment in product_fetched.comments
    assert comment in author_fetched.comments
