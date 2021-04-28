import os

from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def create_connection():
    connection = QSqlDatabase.addDatabase("QSQLITE")
    this_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(this_dir, "db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db_path = os.path.join(db_dir, "digitization_client.sqlite")
    connection.setDatabaseName(db_path)
    connection.open()

    query = QSqlQuery()

    query.exec_("PRAGMA foreign_keys = ON")

    projects_table_query = """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id VARCHAR(10),
            name VARCHAR(40),
            project_dir VARCHAR(255)
        )
        """

    items_table_query = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(500),
            dates VARCHAR(500),
            box VARCHAR(20),
            folder VARCHAR(20),
            identifier VARCHAR(40),
            uri VARCHAR(50),
            rename BOOLEAN DEFAULT 0,
            derivatives BOOLEAN DEFAULT 0,
            copy BOOLEAN DEFAULT 0,
            complete BOOLEAN DEFAULT 0,
            page_count INT DEFAULT 0,
            project_id INTEGER NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """

    query.exec_(projects_table_query)
    query.exec_(items_table_query)
    return True


def get_projects():
    projects = []
    sql_query = """
        SELECT
            projects.id,
            projects.collection_id,
            projects.name,
            projects.project_dir,
            COUNT(items.id) item_total,
            SUM(CASE WHEN items.complete=1 THEN 1 ELSE 0 END),
            SUM(items.page_count)
        FROM projects
        LEFT OUTER JOIN items on items.project_id=projects.id
        GROUP BY projects.id
        HAVING item_total > 0
        """
    query = QSqlQuery(sql_query)
    while query.next():
        project = {}
        project["id"] = query.value(0)
        project["collection_id"] = query.value(1)
        project["name"] = query.value(2)
        project["project_dir"] = query.value(3)
        project["total_items"] = query.value(4)
        project["completed_items"] = query.value(5)
        project["total_scans"] = query.value(6)
        projects.append(project)
    return projects


def create_project(collection_id, project_name, project_dir):
    query = QSqlQuery()
    query.prepare("""
    INSERT INTO projects
        (collection_id, name, project_dir)
    VALUES
        (:collection_id, :project_name, :project_dir)
    """)
    query.bindValue(":collection_id", collection_id)
    query.bindValue(":project_name", project_name)
    query.bindValue(":project_dir", project_dir)
    query.exec_()
    project_id = query.lastInsertId()
    return project_id


def get_project_items(project_id):
    items = []
    query = QSqlQuery()
    query.prepare("""
    SELECT
        title,
        dates,
        box,
        folder,
        identifier,
        rename,
        derivatives,
        copy,
        complete,
        id
    FROM items
    WHERE project_id=:project_id
    """)
    query.bindValue(":project_id", project_id)
    query.exec_()
    while query.next():
        item = {}
        item_title = query.value(0)
        item_dates = query.value(1)
        if item_title and item_dates:
            display_string = f"{item_title}, {item_dates}"
        elif item_title:
            display_string = item_title
        else:
            display_string = item_dates
        item["display_string"] = display_string
        item["box"] = query.value(2)
        item["folder"] = query.value(3)
        item["identifier"] = query.value(4)
        item["rename"] = query.value(5)
        item["derivatives"] = query.value(6)
        item["copy"] = query.value(7)
        item["complete"] = query.value(8)
        item["id"] = query.value(9)
        items.append(item)
    return items


def create_item(item, project_id):
    identifier = item["item_identifier"]
    title = item["title"]
    dates = item["dates"]
    box = item["box"]
    folder = item["folder"]
    uri = item["uri"]
    query = QSqlQuery()
    query.prepare("""
    INSERT INTO items
        (title, dates, box, folder, identifier, uri, project_id) 
    VALUES
        (:title, :dates, :box, :folder, :identifier, :uri, :project_id)
    """)
    query.bindValue(":title", title)
    query.bindValue(":dates", dates)
    query.bindValue(":box", box)
    query.bindValue(":folder", folder)
    query.bindValue(":identifier", identifier)
    query.bindValue(":uri", uri)
    query.bindValue(":project_id", project_id)
    query.exec_()


def get_item_progress(item_id):
    query = QSqlQuery()
    query.prepare("SELECT rename, derivatives, copy, complete FROM items WHERE id=:item_id")
    query.bindValue(":item_id", item_id)
    query.exec_()
    query.first()
    progress = {
        "rename": query.value(0),
        "derivatives": query.value(1),
        "copy": query.value(2),
        "complete": query.value(3)
    }
    return progress


def update_item_progress(item_id, task):
    query = QSqlQuery()
    query.prepare("UPDATE items SET %s=1 WHERE id=:id" % task)
    query.bindValue(":id", item_id)
    query.exec_()


def update_item_page_count(item_id, page_count):
    query = QSqlQuery()
    query.prepare("UPDATE items SET page_count=:page_count WHERE id=:item_id")
    query.bindValue(":page_count", page_count)
    query.bindValue(":item_id", item_id)
    query.exec_()
