from sqlalchemy import select, inspect

from adidas.adapters.orm import metadata

def test_database_populate_inspect_table_names(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['product_brands', 'products', 'comments', 'brands', 'users']

def test_database_populate_select_all_brands(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_brands_table = inspector.get_table_names()[3]

    with database_engine.connect() as connection:
        # query for records in table brands
        select_statement = select([metadata.tables[name_of_brands_table]])
        result = connection.execute(select_statement)

        all_brand_names = []
        for row in result:
            all_brand_names.append(row['name'])

        assert all_brand_names == ['ORIGINALS', 'CORE / NEO', 'SPORT PERFORMANCE']

def test_database_populate_select_all_users(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['tobin', 'irem', 'archie']

def test_database_populate_select_all_comments(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_comments_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table comments
        select_statement = select([metadata.tables[name_of_comments_table]])
        result = connection.execute(select_statement)

        all_comments = []
        for row in result:
            all_comments.append((row['id'], row['user_id'], row['product_id'], row['comment']))

        assert all_comments == [(1, 2, "AH2430", "I really want this. Damn"),
                                (2, 1, "AH2430", "Best product!"),
                                (3, 3, "AH2430", "Wow my favorite colour!")]

def test_database_populate_select_all_products(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_products_table = inspector.get_table_names()[1]

    with database_engine.connect() as connection:
        # query for records in table products
        select_statement = select([metadata.tables[name_of_products_table]])
        result = connection.execute(select_statement)

        all_products = []
        for row in result:
            all_products.append((row['id'], row['name']))

        nr_products = len(all_products)

        assert all_products[0] == (1, 'Coronavirus: First case of virus in New Zealand')
        assert all_products[nr_products//2] == (89, 'Covid 19 coronavirus: Queen to make speech urging Britain to rise to the unprecedented challenges of pandemic')
        assert all_products[nr_products-1] == (177, 'Covid 19 coronavirus: Kiwi mum on the heartbreak of losing her baby in lockdown')