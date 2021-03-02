import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from adidas.domain.model import User, Product, Comment, Brand, make_comment, make_brand_association

product_price = 7499


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_product(empty_session):
    empty_session.execute(
        'INSERT INTO products (name, description, brand, hyperlink, image_hyperlink, id, price, discount) VALUES '
        '("EPIC SHOES", "Very epic", "ORIGINALS", "www.google.com", "www.google.com/image", "123", 7499, 2)'
    )
    row = empty_session.execute('SELECT id from products').fetchone()

    return row[0]


def insert_brand(empty_session):
    empty_session.execute(
        'INSERT INTO brands (name) VALUES ("ORIGINALS")'
    )
    rows = list(empty_session.execute('SELECT id from brands'))
    keys = tuple(row[0] for row in rows)

    return keys[0]


def insert_product_brand_associations(empty_session, product_key, brand_key):
    stmt = 'INSERT INTO product_brands (product_id, brand_id) VALUES (:product_id, :brand_id)'

    empty_session.execute(stmt, {'product_id': product_key, 'brand_id': brand_key})


def insert_commented_product(empty_session):
    product_key = insert_product(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO comments (user_id, product_id, comment, timestamp) VALUES '
        '(:user_id, :product_id, "Comment 1", :timestamp_1),'
        '(:user_id, :product_id, "Comment 2", :timestamp_2)',
        {'user_id': user_key, 'product_id': product_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT id from products').fetchone()
    return row[0]


def make_product():
    product = Product('EPIC SHOES', 'Very epic', 'www.google.com', 'www.google.com/image', '123', product_price, 2)

    return product


def make_user():
    user = User("Andrew", "111")
    return user


def make_brand():
    brand = Brand("ORIGINALS")
    return brand


def test_loading_of_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("Andrew", "1234"),
        User("Cindy", "999")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("Andrew", "111")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_product(empty_session):
    product_key = insert_product(empty_session)

    expected_product = make_product()
    fetched_product = empty_session.query(Product).one()

    assert expected_product == fetched_product
    assert product_key == fetched_product.id


def test_loading_of_branded_product(empty_session):
    product_key = insert_product(empty_session)
    brand_key = insert_brand(empty_session)
    insert_product_brand_associations(empty_session, product_key, brand_key)

    product = empty_session.query(Product).get(product_key)
    brand = empty_session.query(Brand).get(brand_key)

    assert brand.brand_name == product.brand


def test_loading_of_commented_product(empty_session):
    insert_commented_product(empty_session)

    rows = empty_session.query(Product).all()
    product = rows[0]

    assert len(product._comments) == 2

    for comment in product._comments:
        assert comment._product is product


def test_saving_of_comment(empty_session):
    product_key = insert_product(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234"))

    rows = empty_session.query(Product).all()
    product = rows[0]
    user = empty_session.query(User).filter(User._username == "Andrew").one()

    # Create a new Comment that is bidirectionally linked with the User and Product.
    comment_text = "Some comment text."
    comment = make_comment(comment_text, user, product)

    # Note: if the bidirectional links between the new Comment and the User and
    # Product objects hadn't been established in memory, they would exist following
    # committing the addition of the Comment to the database.
    empty_session.add(comment)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, product_id, comment FROM comments'))

    assert rows == [(user_key, product_key, comment_text)]


def test_saving_of_product(empty_session):
    product = make_product()
    empty_session.add(product)
    empty_session.commit()

    rows = list(
        empty_session.execute('SELECT name, description, hyperlink, image_hyperlink, id, price, discount FROM products'))
    price = product_price
    assert rows == [('EPIC SHOES', 'Very epic', 'www.google.com', 'www.google.com/image', '123', price, 2)]


def test_saving_branded_product(empty_session):

    product_key = insert_product(empty_session)
    brand_key = insert_brand(empty_session)

    # Establish the bidirectional relationship between the Product and the Brand.
    insert_product_brand_associations(empty_session, product_key, brand_key)

    # Test test_saving_of_product() checks for insertion into the products table.
    rows = list(empty_session.execute('SELECT id FROM products'))
    product_key = rows[0][0]

    # Check that the brands table has a new record.
    rows = list(empty_session.execute('SELECT id, name FROM brands'))

    brand_key = rows[0][0]
    assert rows[0][1] == "ORIGINALS"

    # Check that the product_brands table has a new record.
    rows = list(empty_session.execute('SELECT product_id, brand_id from product_brands'))
    product_foreign_key = rows[0][0]
    brand_foreign_key = rows[0][1]

    assert product_key == product_foreign_key
    assert brand_key == brand_foreign_key


def test_save_commented_product(empty_session):
    # Create Product User objects.
    product = make_product()
    user = make_user()

    # Create a new Comment that is bidirectionally linked with the User and Product.
    comment_text = "Some comment text."
    comment = make_comment(comment_text, user, product)

    # Save the new Product.
    empty_session.add(product)
    empty_session.commit()

    # Test test_saving_of_product() checks for insertion into the products table.
    rows = list(empty_session.execute('SELECT id FROM products'))
    product_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the comments table has a new record that links to the products and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, product_id, comment FROM comments'))
    assert rows == [(user_key, product_key, comment_text)]
