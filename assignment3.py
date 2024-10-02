"""
This script extracts metadata from PubMed XML files and inserts it into a MySQL database.
"""

import os
import mysql.connector
import xmltodict

# Read MySQL credentials from .my.cnf file
def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    """
    return mysql.connector.connect(
        host="mariadb.bin.bioinf.nl",
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )

# Create tables in the database
def create_tables(cursor):
    """
    Creates the necessary tables in the MySQL database.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        pubmed_id VARCHAR(255) PRIMARY KEY,
        title TEXT,
        length INT,
        publication_year INT,
        publisher VARCHAR(255),
        journal VARCHAR(255)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        article_pubmed_id VARCHAR(255),
        FOREIGN KEY (article_pubmed_id) REFERENCES articles(pubmed_id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keywords (
        id INT AUTO_INCREMENT PRIMARY KEY,
        keyword VARCHAR(255),
        article_pubmed_id VARCHAR(255),
        FOREIGN KEY (article_pubmed_id) REFERENCES articles(pubmed_id)
    )""")

# Parse the XML file and insert data into the database
def insert_article(cursor, article):
    pubmed_id = article['MedlineCitation']['PMID']['#text']
    title = article['MedlineCitation']['Article']['ArticleTitle']
    publication_year = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
    publisher = article['MedlineCitation']['Article']['Journal']['Title']
    journal = article['MedlineCitation']['Article']['Journal']['ISOAbbreviation']
    length = len(article['MedlineCitation']['Article']['Pagination']['MedlinePgn'])
    cursor.execute(
    "INSERT INTO articles (pubmed_id, title, length, publication_year, publisher, journal) "
    "VALUES (%s, %s, %s, %s, %s, %s)",
    (pubmed_id, title, length, publication_year, publisher, journal)
    )
    return pubmed_id

def insert_authors(cursor, authors, pubmed_id):
    """
    Inserts authors associated with a specific article into the database.
    Arguments:
    - cursor: Database cursor to execute SQL commands.
    - authors: List of author data extracted from the article.
    - pubmed_id: The PubMed ID of the article to associate with the authors.
    """
    for author in authors:
        name = author['LastName'] + ' ' + author['ForeName']
        cursor.execute("""
        INSERT INTO authors (name, article_pubmed_id)
        VALUES (%s, %s)
        """, (name, pubmed_id))

def insert_keywords(cursor, keywords, pubmed_id):
    """
    Inserts keywords associated with a specific article into the database.
    Arguments:
    - cursor: Database cursor to execute SQL commands.
    - keywords: List of keywords associated with the article.
    - pubmed_id: The PubMed ID of the article to associate with the keywords.
    """
    for keyword in keywords:
        cursor.execute("""
        INSERT INTO keywords (keyword, article_pubmed_id)
        VALUES (%s, %s)
        """, (keyword, pubmed_id))

def insert_data_from_xml(xml_file, cursor):
    with open(xml_file, 'r', encoding='utf-8') as file:
        data = xmltodict.parse(file.read())
    articles = data['PubmedArticleSet']['PubmedArticle']
    for article in articles:
        pubmed_id = insert_article(cursor, article)
        insert_authors(cursor, article['MedlineCitation']['Article']['AuthorList']['Author'], pubmed_id)
        insert_keywords(cursor, article['MedlineCitation']['KeywordList']['Keyword'], pubmed_id)

def main():
    """
    Main function that establishes the database connection, creates tables,
    and inserts data from the XML file into the database.
    """
    # Establish connection
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create tables
    create_tables(cursor)
    # Insert data from XML
    xml_file = 'pubmed0001.xml'  # Replace with your actual XML file
    insert_data_from_xml(xml_file, cursor)
    # Commit and close connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
