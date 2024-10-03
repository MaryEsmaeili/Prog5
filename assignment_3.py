import os
from sqlalchemy import create_engine, text
import xmltodict

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
        authors_list = article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', [])
        if isinstance(authors_list, dict):
            authors_list = [authors_list]
        authors = ', '.join([f"{author.get('LastName', '')} {author.get('ForeName', '')}" for author in authors_list])
        article_metadata['authors'] = authors
        journal = article['MedlineCitation']['Article']['Journal']
        article_metadata['journal'] = journal['Title']
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
        keywords_list = article['MedlineCitation'].get('KeywordList', {}).get('Keyword', [])
        if isinstance(keywords_list, list):
            keywords = [kw.get('#text', kw) if isinstance(kw, dict) else kw for kw in keywords_list]
            article_metadata['keywords'] = ', '.join(keywords)
        elif isinstance(keywords_list, str):
            article_metadata['keywords'] = keywords_list
        else:
            article_metadata['keywords'] = None
        pages = article['MedlineCitation']['Article'].get('Pagination', {}).get('MedlinePgn', None)
        article_metadata['page_count'] = pages if pages else None    
        article_metadata['publisher'] = article['MedlineCitation']['Article'].get('Publisher', {}).get('PublisherName', None)
        extracted_data.append(article_metadata)

    return extracted_data

def create_tables():
    """
    Create the Articles table if it does not exist.
    """
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Articles (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            pubmed_id TEXT NOT NULL,
            title TEXT NOT NULL,
            authors TEXT,
            journal TEXT,
            year INTEGER,
            keywords TEXT,
            page_count TEXT,
            publisher TEXT
        );  
    """))

def insert_article_data(article_data):
    """
    Insert parsed article data into the Articles table.
    """
    query = text("""
        INSERT INTO Articles (pubmed_id, title, authors, journal, year, keywords, page_count, publisher)
        VALUES (:pubmed_id, :title, :authors, :journal, :year, :keywords, :page_count, :publisher)
    """)
    for article in article_data:
        conn.execute(query, article)
        conn.commit()

# Main execution
if __name__ == "__main__":
    create_tables()
    articles = parse_pubmed_xml("/data/datasets/NCBI/PubMed/pubmed21n0562.xml")
    insert_article_data(articles)
