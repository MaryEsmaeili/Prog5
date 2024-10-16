# Assignment 4: Analysis of PubMed Data with PySpark

## Overview

This assignment involves analyzing a set of PubMed XML files using PySpark. The goal is to explore relationships between authors, citations, and keywords in published papers. You will answer several research questions using the data, such as the correlation between co-authors and citations, keyword sharing, and more.

### Research Questions Addressed:
1. **Average number of co-authors per article**.
2. **Do authors mainly cite papers from other authors they've co-authored with?**
3. **How do citations of papers distribute over time, and does this differ for highly cited papers?**
4. **Is there a correlation between shared keywords and citations?**
5. **Do highly cited papers share more keywords with the papers that cite them compared to the general dataset?**

## Project Structure

- **assignment4.py**: This is the main script that reads PubMed XML files, processes the data using PySpark, and answers the research questions.
- **assignment4.sh**
- **README.md**: This file provides an overview and instructions.
- **assignment4_answers.csv**: The results of the analyses are saved in this CSV file.
- **pubmed21n0562.xml**: The PubMed dataset file (used for testing purposes, larger datasets can also be processed).

## Requirements

To run this project, you need:

- **Python 3.x**
- **Apache Spark** (PySpark)
- **Databricks XML package** for reading XML files in Spark

You can install the dependencies using the following command:

```bash
pip install pyspark pandas matplotlib
```

Ensure you have a working Spark cluster. If you are running this locally, you need to download and install Apache Spark from [https://spark.apache.org/downloads.html](https://spark.apache.org/downloads.html).

For XML parsing in Spark, we use the `com.databricks:spark-xml` package.

## How to Run the Project

1. **Set up Spark**:
   - If you are using a cluster, make sure the master node is available and your environment is properly configured.
   - If running locally, ensure Apache Spark is installed and available in your `PATH`.

2. **Prepare the Data**:
   - Place the PubMed XML file (`pubmed21n0562.xml` or any other XML file from PubMed) in the specified location (`/data/datasets/NCBI/PubMed/`).

3. **Running the Script**:
   To execute the analysis and answer the research questions, run the following command in your terminal:

   ```bash
   python3 assignment4.py
   ```

4. **Output**:
   - The script will print the answers to the research questions to the console.
   - The answers will also be saved in a CSV file called `assignment4_answers.csv`.

## Explanation of the Main Script (`assignment4.py`)

- **Creating Spark Session**: 
  A Spark session is created to enable the use of PySpark for data analysis. The script includes the necessary package for XML parsing.

- **Loading Data**:
  The PubMed XML file is loaded using the `spark-xml` library, and a schema is defined to properly parse the XML structure.

- **Answering Research Questions**:
  Several functions are defined to answer the research questions. For example:
  - **q1(df)**: Calculates the average number of co-authors per paper.
  - **q2(df)**: Determines whether authors cite other authors they've co-authored with.
  - **q3(df)**: Analyzes the distribution of citations over time.
  - **q4(df)**: Calculates the correlation between shared keywords and citations.
  - **q5(df)**: Investigates keyword sharing among the most-cited papers and the papers that cite them.

- **Saving Results**:
  After analysis, results are saved into a CSV file and a plot is generated for the citation distribution.

## Customizing the Analysis

You can modify the cutoff for highly-cited papers or adjust the schema based on different XML formats by editing the `assignment4.py` script.

For example, to change the cutoff in **q5** for identifying the most-cited papers:

