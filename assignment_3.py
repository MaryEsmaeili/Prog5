from sqlalchemy import create_engine, text
import xmltodict
import os

# Load credentials from the .my.cnf file
def load_mysql_credentials():
    creds = {}
    with open(os.path.expanduser("~/.my.cnf")) as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key.strip()] = value.strip()
    return creds

creds = load_mysql_credentials()

# Construct the connection string
connection_string = f"mysql+mysqldb://{creds['user']}:{creds['password']}@mariadb.bin.bioinf.nl/{creds['database']}"

# Connect to the database
engine = create_engine(connection_string)
conn = engine.connect()

def parse_pubmed_xml(file_path):
    with open(file_path, 'r') as xml_file:
        pubmed_dict = xmltodict.parse(xml_file.read())
    
    articles = pubmed_dict['PubmedArticleSet']['PubmedArticle']
    extracted_data = []
    
    for article in articles:
        article_metadata = {}
        article_metadata['pubmed_id'] = article['MedlineCitation']['PMID']
        article_metadata['title'] = article['MedlineCitation']['Article']['ArticleTitle']
        
        # Safely handle the 'AuthorList'
        authors_list = article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', [])

        if isinstance(authors_list, dict):  # if there is only one author
            authors_list = [authors_list]

        # Joining all Authors' name and family with ,
        authors = ', '.join([f"{author.get('LastName', '')} {author.get('ForeName', '')}" for author in authors_list])
        article_metadata['authors'] = authors
        
        # Handle Journal and Publication Date (Year)
        journal = article['MedlineCitation']['Article']['Journal']
        article_metadata['journal'] = journal['Title']
        
        # Safely extract publication year
        pub_date = journal['JournalIssue']['PubDate']
        year = pub_date.get('Year')
        if year is not None:
            year = int(year)
        else:
            year = None
        # if 'Year' in pub_date:
        #     article_metadata['year'] = pub_date['Year']
        # elif 'MedlineDate' in pub_date:
        #     # In case 'MedlineDate' is present instead of 'Year'
        #     article_metadata['year'] = pub_date['MedlineDate']
        # else:
        #     article_metadata['year'] = None  # No valid year or date found
        article_metadata['year'] = year
        # Extract keywords safely
        keywords_list = article['MedlineCitation'].get('KeywordList', {}).get('Keyword', [])

        if isinstance(keywords_list, list):
            # Extract the actual keyword from each dictionary in the list
            keywords = [kw.get('#text', kw) if isinstance(kw, dict) else kw for kw in keywords_list]
            article_metadata['keywords'] = ', '.join(keywords)
        elif isinstance(keywords_list, str):
            # If it's just a single string, set it directly
            article_metadata['keywords'] = keywords_list
        else:
            article_metadata['keywords'] = None  # No valid keywords found

        # Extract Pagination Info (Length)
        pages = article['MedlineCitation']['Article'].get('Pagination', {}).get('MedlinePgn', None)
        article_metadata['page_count'] = pages if pages else None
        
        # Extract Publisher (if available)
        article_metadata['publisher'] = article['MedlineCitation']['Article'].get('Publisher', {}).get('PublisherName', None)
        
        extracted_data.append(article_metadata)

    
    return extracted_data



def create_tables():
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
