# Real-Time Earthquake Alerting System

This project is a replica of a real-time data engineering pipeline originally built on Microsoft Fabric. It ingests, processes, and analyzes live earthquake data from the USGS API to provide alerts for significant seismic events and visualize the findings on an interactive dashboard.

## Project Architecture

The pipeline follows a multi-layered "Lakehouse" architecture, where data is progressively refined as it moves through different layers. This ensures data quality, modularity, and easy maintenance.

### 1. **Bronze Layer: Raw Data Ingestion**
- **What it is**: The first point of entry for our data.
- **How it's achieved**: A Python script (`src/ingest_data.py`) runs on a schedule (e.g., every 5 minutes). It fetches live earthquake data from the public USGS GeoJSON API and saves the raw, unaltered JSON output into the `data/bronze` directory. Each file is timestamped to maintain a historical record of every fetch.

### 2. **Silver Layer: Cleaned & Structured Data**
- **What it is**: The raw data is transformed into a clean, structured, and queryable format.
- **How it's achieved**: The `src/process_data.py` script reads new JSON files from the bronze layer. It extracts the key attributes for each earthquake (magnitude, location, time, etc.), cleans the data (e.g., converts timestamps), and organizes it into a tabular format using the pandas library. The resulting clean dataset is saved as a Parquet file in the `data/silver` directory. Processed JSON files are moved to an archive to prevent re-processing.

### 3. **Gold Layer: Aggregated & Business-Ready Data**
- **What it is**: This layer contains the most valuable, filtered data ready for analysis and alerting.
- **How it's achieved**: The `src/analyze_and_alert.py` script processes data from the silver layer. It filters for "significant" earthquakes (defined as magnitude >= 5.0) and saves this high-value subset into the `data/gold` directory.

### 4. **Alerting & Monitoring**
- **What it is**: An automated system to notify stakeholders of significant earthquakes.
- **How it's achieved**: As part of the `src/analyze_and_alert.py` script, the system checks the gold layer for any new significant earthquakes that haven't been seen before. For each new event, it prints a formatted alert to the console and logs the event ID to prevent duplicate alerts.

### 5. **Visualization**
- **What it is**: An interactive dashboard for exploring the earthquake data.
- **How it's achieved**: The `src/dashboard.py` script uses the Streamlit and Plotly libraries to create a web-based dashboard. It reads the clean data from the silver layer and presents it as an interactive map, a filterable data table, and a set of summary statistics.

## Technology Stack

### Technologies Used in This Project

- **Language**: Python 3
- **Data Ingestion**: `requests` library to fetch data from the API.
- **Data Transformation**: `pandas` for data manipulation and cleaning.
- **Data Storage**: Local filesystem storing data in `JSON` (Bronze) and `Apache Parquet` (Silver/Gold) formats.
- **Visualization**: `Streamlit` for the web dashboard and `Plotly` for interactive charts.
- **Environment Management**: `venv` for creating an isolated Python environment.

### Comparison to Original Project Scope (Microsoft Fabric)

This project successfully replicates the logic of the original system using open-source tools. Here is a comparison of the technology stacks:

| Component | Original Project (Microsoft Fabric) | This Project (Open-Source Replica) |
|---|---|---|
| **Data Orchestration**| **Fabric Notebook (PySpark)**, scheduled in a Data Pipeline. | **Python scripts** (`src/*.py`). We would use a system scheduler like `cron` (Linux/macOS) or Task Scheduler (Windows) to run them automatically. |
| **Data Lakehouse** | **Microsoft Fabric Lakehouse** (OneLake) storing Bronze, Silver, and Gold tables. | **Local file system** with directories (`data/bronze`, `data/silver`, `data/gold`) storing Parquet files. An object storage service like **Amazon S3** or **MinIO** would be a more scalable alternative. |
| **Alerting** | **Microsoft Fabric Data Activator**, monitoring the Lakehouse. | A **custom Python script** (`src/analyze_and_alert.py`) that checks for new data and logs alerts. A more robust alternative would be to integrate with a messaging service like **Slack** or **Twilio**. |
| **Dashboard** | **Power BI** with a Semantic Model in DirectLake mode. | **Streamlit** with **Plotly**. This is excellent for rapid prototyping. For a production-grade solution, hosting it on a dedicated server or using a framework like **Dash** or **FastAPI + React** would be more suitable. |
| **Compute Engine**| **Apache Spark** (within Fabric Notebooks). | **Pandas**. While pandas is perfect for this scale, **Spark** (or Dask) would be necessary if the data volume grew to millions or billions of records. |

## How to Run the Project

1.  **Set up the environment**:
    ```bash
    # Create and activate the virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

2.  **Run the pipeline**:
    ```bash
    # 1. Ingest raw data
    python src/ingest_data.py

    # 2. Process data to silver layer
    python src/process_data.py

    # 3. Analyze data and generate alerts
    python src/analyze_and_alert.py
    ```

3.  **Launch the dashboard**:
    ```bash
    streamlit run src/dashboard.py
    ```
<img width="1848" height="1022" alt="Screenshot 2025-12-06 at 9 44 43 AM" src="https://github.com/user-attachments/assets/804c47c4-3a63-4ea3-886a-10c5c82de5a5" />
<img width="1848" height="1022" alt="Screenshot 2025-12-06 at 9 44 57 AM" src="https://github.com/user-attachments/assets/e7c1cc4a-3c4f-44d2-835a-d4ebf11cd773" />
<img width="1848" height="1022" alt="Screenshot 2025-12-06 at 9 45 31 AM" src="https://github.com/user-attachments/assets/8113a7e3-6fb8-404a-95de-72f793a7e889" />
