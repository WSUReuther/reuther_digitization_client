import os
import sqlite3
import sys

from reuther_digitization_utils.item_utils import ItemUtils


def create_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, "reuther_digitization_client", "db")
    db_file = os.path.join(db_dir, "digitization_client.sqlite")
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    return connection, cursor


def get_project(cursor, collection_id):
    sql_query = "SELECT id, project_dir FROM projects WHERE collection_id=:collection_id"
    results = cursor.execute(sql_query, {"collection_id": collection_id}).fetchall()
    if results:
        return results[0]
    else:
        sys.exit(f"No project found in database for collection_id {collection_id}")


def get_project_items(cursor, project_id):
    sql_query = "SELECT id, identifier FROM items WHERE project_id=:project_id"
    results = cursor.execute(sql_query, {"project_id": project_id}).fetchall()
    return results


def get_item_status(cursor, item_id):
    sql_query = "SELECT rename, derivatives, copy, complete FROM items WHERE id=:item_id"
    result = cursor.execute(sql_query, {"item_id": item_id}).fetchone()
    if result[0] and not result[1]:
        return True
    else:
        return False


def update_status(connection, cursor, item_id):
    sql_query = "UPDATE items SET derivatives=1 WHERE id=?"
    cursor.execute(sql_query, (item_id,))
    connection.commit()


def batch_generate_derivatives(collection_id):
    connection, cursor = create_connection()
    project_id, project_dir = get_project(cursor, collection_id)
    items = get_project_items(cursor, project_id)
    for item in items:
        item_id = item[0]
        item_identifier = item[1]
        generate_derivatives = get_item_status(cursor, item_id)
        if generate_derivatives:
            print(f"generating derivatives for {item_identifier}")
            try:
                item_util = ItemUtils(project_dir, item_identifier)
                item_util.generate_derivatives()
                update_status(connection, cursor, item_id)
                print(f"derivatives generated for {item_identifier}")
            except Exception as e:
                sys.exit(f"error: {str(e)}")
    connection.close()
