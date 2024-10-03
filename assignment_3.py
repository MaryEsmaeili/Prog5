import os
from sqlalchemy import create_engine, text
import xmltodict
import sys

# Load credentials from the .my.cnf file
def load_mysql_credentials():
    """
    Load MySQL credentials from the .my.cnf file.
    """
    credentials = {}
    with open(os.path.expanduser("~/.my.cnf"), encoding='utf-8') as config_file:
        for line in config_file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                credentials[key.strip()] = value.strip()
    return credentials

creds = load_mysql_credentials()
# Construct the connection string
connection_string = (f"mysql+mysqldb://{creds['user']}:{creds['password']}@"
                     f"mariadb.bin.bioinf.nl/{creds['database']}")
# Connect to the database
engine = create_engine(connection_string)
conn = engine.connect()

def parse_pubmed_xml(file_path):
    """
    Parse PubMed XML file and extract relevant article data.
    """
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        pubmed_dict = xmltodict.parse(xml_file.read())
    articles = pubmed_dict['PubmedArticleSet']['PubmedArticle']
    extracted_data = []
    for article in articles:
        article_metadata = {}
        article_metadata['pubmed_id'] = article['MedlineCitation']['PMID']
        article_metadata['title'] = article['MedlineCitation']['Article']['ArticleTitle']
        # Authors
        authors_list = article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', [])
        if isinstance(authors_list, dict):
            authors_list = [authors_list]
        authors = [f"{author.get('LastName', '')} {author.get('ForeName', '')}" for author in authors_list]
        article_metadata['authors'] = authors
        # Journal
        journal = article['MedlineCitation']['Article']['Journal']
        article_metadata['journal'] = journal['Title']
        # Year
        pub_date = journal['JournalIssue']['PubDate']
        year = None
        if 'Year' in pub_date:
            year = pub_date['Year']
        elif 'MedlineDate' in pub_date:
            year = pub_date['MedlineDate'][:4]
        try:
            article_metadata['year'] = int(year)
        except (ValueError, TypeError):
            article_metadata['year'] = None
        # Keywords
        keywords_list = article['MedlineCitation'].get('KeywordList', {}).get('Keyword', [])
        if isinstance(keywords_list, list):
            keywords = [kw.get('#text', kw) if isinstance(kw, dict) else kw for kw in keywords_list]
            article_metadata['keywords'] = keywords
        elif isinstance(keywords_list, str):
            article_metadata['keywords'] = [keywords_list]
        else:
            article_metadata['keywords'] = []
        # Pages
        pages = article['MedlineCitation']['Article'].get('Pagination', {}).get('MedlinePgn', None)
        article_metadata['page_count'] = pages if pages else None    
        # Publisher
        article_metadata['publisher'] = article['MedlineCitation']['Article'].get('Publisher', {}).get('PublisherName', None)
        extracted_data.append(article_metadata)
    return extracted_data

def create_tables():
    # Create Publishers table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Publishers (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL
        );
    """))
    # Create Journals table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Journals (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            title TEXT NOT NULL
        );
    """))
    # Create Authors table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Authors (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL
        );
    """))
    # Create Articles table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Articles (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            pubmed_id TEXT NOT NULL,
            title TEXT NOT NULL,
            journal_id INTEGER,
            year INTEGER,
            page_count TEXT,
            publisher_id INTEGER,
            FOREIGN KEY (journal_id) REFERENCES Journals(id),
            FOREIGN KEY (publisher_id) REFERENCES Publishers(id)
        );
    """))
    # Create Keywords table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Keywords (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            article_id INTEGER,
            keyword TEXT NOT NULL,
            FOREIGN KEY (article_id) REFERENCES Articles(id)
        );
    """))
    # Create ArticleAuthors table (many-to-many relationship)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ArticleAuthors (
            article_id INTEGER,
            author_id INTEGER,
            FOREIGN KEY (article_id) REFERENCES Articles(id),
            FOREIGN KEY (author_id) REFERENCES Authors(id)
        );
    """))

def get_or_create_id(table, column, value):
    """
    Get the ID from the table if it exists, otherwise create it and return the new ID.
    """
    select_query = text(f"SELECT id FROM {table} WHERE {column} = :value LIMIT 1")
    insert_query = text(f"INSERT INTO {table} ({column}) VALUES (:value)")
    result = conn.execute(select_query, {'value': value}).mappings().fetchone()
    if result:
        return result['id']  # Access as a dictionary
    else:
        result = conn.execute(insert_query, {'value': value})
        conn.commit()
        return result.lastrowid

def insert_article_data(article_data):
    """
    Insert parsed article data into the relevant tables.
    """
    for article in article_data:
        # Insert or get publisher ID
        if article['publisher']:
            publisher_id = get_or_create_id('Publishers', 'name', article['publisher'])
        else:
            publisher_id = None
        # Insert or get journal ID
        journal_id = get_or_create_id('Journals', 'title', article['journal'])
        # Insert article into Articles table
        query = text("""
            INSERT INTO Articles (pubmed_id, title, journal_id, year, page_count, publisher_id)
            VALUES (:pubmed_id, :title, :journal_id, :year, :page_count, :publisher_id)
        """)
        result = conn.execute(query, {
            'pubmed_id': article['pubmed_id'],
            'title': article['title'],
            'journal_id': journal_id,
            'year': article['year'],
            'page_count': article['page_count'],
            'publisher_id': publisher_id
        })
        article_id = result.lastrowid
        # Insert authors and their relation to the article
        for author in article['authors']:
            author_id = get_or_create_id('Authors', 'name', author)
            conn.execute(text("""
                INSERT INTO ArticleAuthors (article_id, author_id)
                VALUES (:article_id, :author_id)
            """), {'article_id': article_id, 'author_id': author_id})
        # Insert keywords
        for keyword in article['keywords']:
            conn.execute(text("""
                INSERT INTO Keywords (article_id, keyword)
                VALUES (:article_id, :keyword)
            """), {'article_id': article_id, 'keyword': keyword})
        conn.commit()
# Main execution
if __name__ == "__main__":    
    create_tables()
    articles = parse_pubmed_xml("/data/datasets/NCBI/PubMed/pubmed21n0562.xml")
    insert_article_data(articles)
