# Capstone Project

## Contents
* [About](#about)
  * [Purpose](#purpose)
  * [Technologies](#technologies) 
  * [Data Sources](#data-sources)
* [Data Processing](#data-processing)
  * [Output Data Model](#output-data-model)
  * [Dictionary](#dictionary) 
  * [Pipeline Structure](#pipeline-structure)
* [Running the Pipeline](#running-the-pipeline)    
* [Future Challenges](#future-challenges)
  * [Scaling Data Volume](#scaling-data-volume)
  * [Running Periodically](#running-periodically)
  * [Access For Multiple Users](#access-for-multiple-users)

## About

### Purpose

The goal of this project is to analyze the Earth Surface Temperature and Storm Events data ([Sources Below](#data-sources)), either independently or in conjunction with each other, in order to gain insights into these phenomena. To achieve this goal, we will utilize Apache Spark to develop a pipeline that reads the data from the source CSV files (which will be stored on S3), cleans and organizes it, and then stores the processed data as Parquet files on S3.

By structuring and processing the data using [Apache Spark](https://spark.apache.org/), we aim to efficiently handle large volumes of data and enhance the analysis process. The resulting Parquet files will be optimized for query performance and storage efficiency, enabling us to quickly and easily access the data for further analysis.

Overall, this project aims to provide valuable insights into Earth Surface Temperature and Storm Events data by leveraging Apache Spark to structure, process, and store the data efficiently.

### Technologies
We chose Spark for its speed, versatility, and horizontal scalability. It runs on a cluster, utilizing multiple machines' memory and compute capabilities to handle large amounts of data. Its SQL-like syntax makes analytics easier, and the same pipeline code could be used if data storage changed.

For data storage, we chose S3 due to its cost-effectiveness and low administration overhead compared to HDFS or databases. S3 also has good scalability and availability properties, making it an optimal choice.

### Data Sources

- [Earth Surface Temperatures (Kaggle)](https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data)
- [NOAA Storm Events Data](https://www.ncdc.noaa.gov/stormevents/ftp.jsp)

## Data Processing

### Output Data Model

Data will be organized in a small snowflake-type schema in S3 with two fact and two dimension tables stored as a Parquet dataset. Parquet's scalability, partitioning, and columnar storage reduce administrative overhead and scalability issues.

Output data is stored in two facts tables, `storms` and `temperatures`, and two dimension tables, `location` and `time`. This structure allows independent analysis of facts by location and time, and joint analysis by joining them. The most common aggregations are by time or location, allowing analysis of trends in temperatures and storm severity, and types of storms in different areas.

### Dictionary
The `storms` table will contain the following facts about the storm events:
- `start_date`: Date in which the storm event started.
- `event_id`: ID of the storm event given by the NWS.
- `episode_id`: ID of the episode given by the NWS. One episode can contain several events.
- `location_id`: ID of the location (state) where the event occurred. This can be used to join to the
  `locations` table.
- `event_type`: Type of event (text).
- `magnitude_type`: Type of magnitude measurement recorded (if magnitude is provided).
- `magnitude`: Magnitude measurement.
- `damage_property`: Estimated damage to property caused (in US dollars).
- `damage_crops`: Estimated damage to property caused (in US dollars).
- `deaths_direct`: Deaths directly caused by the event.
- `injuries_direct`: Injuries directly caused by the event.

The `temperatures` table, on the other hand, will contain the following:
- `date_year_month`: Year and month in which the measurement was taken. This can be used to join to the
  `dates` table.
- `average_temperature`: Average temperature for the given period.
- `average_temperature_uncertainty`: Uncertainty for the temperature measurement.
- `location_id`: ID of the location where the measurement was taken. his can be used to join to the
  `locations` table.

Here the date will consist only of the month and year, since the dataset only contains average
temperatures on a monthly basis. 

As for the dimension tables, the `location` table contains the 
following fields:
- `location_id`: Unique ID of the location (hash of the state and country).
- `state`: State (within the country).
- `country`: Country.

The dimension is determined by state and country because that is the greatest common resolution
common to both datasets. 

The `time` table has the following fields:
- `date`: Date.
- `year`: Year of the date (integer).
- `month`: Month of the date (integer).
- `year_month`: Year and month of the date in `yyyy-MM` format.

### Pipeline Structure
The pyspark pipeline has four basic steps:

1. Read raw temperature and storm data from S3.
2. Create facts and dimensions tables.
3. Perform quality checks:
    - Verify correct location ids by joining storms and locations tables.
    - Verify all dates are present by joining storms and dates tables.
4. Write results to S3.

## Running the Pipeline

To run the pipeline, first upload the raw files to the S3 bucket and fill a `.env` file with the following variables:

```dotenv
BUCKET_NAME=
STORM_DATA_PATH=
OUTPUT_PATH=
TEMP_DATA_FILE=
```

`STORM_DATA_PATH` denotes the prefix containing the noaa files in the bucket, `TEMP_DATA_FILE` is the path
to `GlobalTemperaturesByState.csv`, and `OUTPUT_PATH` is the prefix where processed files will be stored.

To run on a cluster, use the `prepare_submit_command.py` script to prepare the spark-submit command with necessary 
environment variables. Then run the pipeline using the `spark_process.py` script.

## Future Challenges

### Scaling Data Volume
For data scaling (e.g. by 100x), the current solution should work well by scaling out the Spark Cluster. 
As for storage, S3 is a highly scalable option.

### Running Periodically

To schedule the pipeline to run periodically, it is recommended to use [Airflow](https://airflow.apache.org/), a platform that allows 
for the scheduling and execution of jobs with traceability and insights into the execution. The job would still be performed by a Spark
cluster and not by Airflow workers, as these have limited capabilities. Airflow Spark or Spark Submit operators can be used to achieve 
this. It's even possible to set up the DAG to spin up an [AWS EMR](https://aws.amazon.com/emr/) cluster for the job and then shut it down
 once the task is completed.

### Access for Multiple Users
For high user access scenarios, S3 can handle read requests effectively, but the Spark cluster may require scaling. Alternatively, to enhance concurrency and performance, precomputing the most commonly performed aggregations and storing the results in a database optimized for concurrent access such as Cassandra could be considered.

[Back to top.](#capstone-project)
