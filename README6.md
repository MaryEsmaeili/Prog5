# Assignment 6: Analysis of the dbNSFP Database with Spark and MySQL

This project aims to analyze functional prediction data for non-synonymous single-nucleotide variants (nsSNVs) from the dbNSFP database, focusing on extracting and processing predictions from various classifiers, creating unique identifiers for genome positions, and storing results in a normalized MySQL database. 

## Dataset
The dataset used here is the `dbNSFP4.9a.txt.gz`, which contains predictions for the effects of ~85 million single-nucleotide variants (SNVs) on human health from over 40 functional prediction tools (classifiers). This file can be accessed on the BIN network at `/data/datasets/dbNSFP/snpEff/data/dbNSFP4.9a.txt.gz`.

### Codebook
The dataset has numerous columns corresponding to different classifiers. For detailed information on the columns and data types, refer to the codebook located at `/data/datasets/dbNSFP/snpEff/data/dbNSFP4.3c.txt.gz.data_types`.

## Objective
The main tasks in this analysis are:
1. Determining the number of predictions made by each of the 43 classifiers.
2. Selecting the top five classifiers based on the number of predictions, discarding the rest.
3. Merging chromosome (`chr`) and position (`pos`) columns to create a unique identifier for each genome position.
4. Identifying the genome position with the most associated predictions.
5. Identifying the Ensembl protein ID with the most predictions.
6. Storing the processed data in a MySQL database with efficient, normalized storage (third normal form).

## Project Structure
- **`assignment6.py`**: The main script that performs the data analysis and saves results to MySQL.
- **`assignment6.md`**: A markdown file detailing the results of each analysis step.
- **SLURM Batch File**: A file for scheduling the Spark job under SLURM.

## Code Walkthrough

### Setup
The script begins by loading MySQL credentials from the `.my.cnf` file and establishing a connection to the MySQL server. The Spark session is then configured with sufficient memory, the MySQL JDBC driver, and error handling to ensure smooth operation.

### Data Loading and Sampling
The `dbNSFP4.9a.txt.gz` file is loaded directly as a gzipped file into a Spark DataFrame. For efficient testing and memory management, only the first 1,000 rows are initially loaded.

### Analysis Steps
1. **Counting Predictions by Classifier**: The script calculates the number of non-null predictions made by each classifier, storing the counts in a dictionary. 
2. **Top Five Classifiers**: The top five classifiers are selected based on the highest prediction counts, and only their columns are retained in the DataFrame.
3. **Genome Position Identifier**: A unique identifier, `genome_position_id`, is created by merging the `chr` and `pos` columns.
4. **Position with Most Predictions**: Using groupBy and orderBy operations, the script finds the genome position with the highest count of predictions.
5. **Protein with Most Predictions**: The `Ensembl_proteinid` with the highest count of predictions is identified using similar methods.

### Saving Results to MySQL
The modified DataFrame is saved to a MySQL table named `nsf_predictions` with overwrite mode. The JDBC URL and properties ensure secure and efficient data transfer between Spark and MySQL.

### Output Results
The results from the analysis are displayed in the console for easy reference:
1. Number of predictions for each classifier.
2. Top five classifiers selected.
3. Unique genome position identifier (`genome_position_id`).
4. Genome position with the most predictions.
5. Protein ID with the most predictions.

#### Example Output:
```plaintext
1. Number of predictions each classifier makes:
{'SIFT_score': 96, 'Polyphen2_HDIV_score': 96, 'MutationTaster_score': 96, 'FATHMM_score': 96, 'PROVEAN_score': 96}

2. Top five classifiers by prediction count:
['SIFT_score', 'Polyphen2_HDIV_score', 'MutationTaster_score', 'FATHMM_score', 'PROVEAN_score']

3. Unique genome position identifier created: 'genome_position_id' column

4. Position with the most predictions:
Position: 1:69055, Count: 2

5. Protein (Ensembl_proteinid) with the most predictions:
Protein: ENSP00000493376;ENSP00000334393, Count: 76
```

## Usage
To run the analysis:
1. Ensure MySQL credentials are saved in `.my.cnf`.
2. Ensure Spark is properly installed, and the MySQL JDBC driver (`mysql-connector-java.jar`) is available.
3. Execute the script as a SLURM job using the provided SLURM batch file. Adjust SLURM resource parameters (`--partition`, `--mem`, `--cpus-per-task`, etc.) as necessary.

## MySQL Table Normalization
The results are stored in a MySQL table following the third normal form (3NF) to eliminate redundancy. Data is deduplicated by separating repeated attributes into different tables where necessary, allowing for efficient storage and easy query optimization.

## Insights on Cassandra
**Advantages over a Single SQL Server Setup**:
- Cassandra provides distributed, fault-tolerant storage with scalability across multiple nodes, which is particularly useful for large datasets like dbNSFP.
- It allows for high-availability applications, where data is replicated across multiple nodes to ensure durability and resilience to node failures.

**Disadvantages of Cassandra**:
- Complexity of setup and maintenance compared to a single SQL server.
- It does not fully support ACID transactions, which can limit its utility for applications needing strict transactional guarantees.

**Downside of Using JSON in Cassandra**:
- JSON data lacks rigid schema enforcement, which can lead to inconsistent data structures and complicate data retrieval.
- JSON can be less efficient in terms of storage and querying, as compared to structured storage with normalized tables in traditional SQL.

## Conclusion
This analysis demonstrates the use of Spark and MySQL for big data processing and storage, offering insights into the most predictive classifiers, protein associations, and highly affected genome positions in the dbNSFP dataset.

