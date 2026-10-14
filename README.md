# Crypto Market Data Pipeline

## Overview

An end-to-end data engineering portfolio project that collects hourly cryptocurrency market data, processes it using Python, stores it in Microsoft SQL Server, and prepares analytical datasets for Power BI.

The project is designed to practice Python ETL, SQL-based data transformations, data warehousing, and business intelligence.

## Architecture

Cryptocurrency Market API → Python ETL → SQL Server Data Warehouse → SQL Data Marts → Power BI

### Data Processing

- **Raw staging:** Preserve original API responses and ingestion metadata in SQL Server.
- **Python ETL:** Validate, clean, transform, and load staged data into the data warehouse.
- **SQL data marts:** Transform warehouse data into reporting-ready datasets.
- **Power BI:** Visualize historical prices, price changes, and trading volume.

## Technology Stack

- Python
- Pandas
- Requests
- PyODBC
- Microsoft SQL Server
- SQL Server Management Studio (SSMS)
- Power BI Desktop
- Git and GitHub

## Planned Features

- Hourly market data ingestion
- Raw data preservation
- Python-based data transformation
- SQL Server data warehouse
- SQL-based data marts
- Incremental loading and duplicate prevention
- Data validation and error handling
- Pipeline logging and recovery
- Automated scheduling
- Power BI dashboards

## Project Status

**Status:** Initial setup

This project is under development. Features will be documented as they are implemented and tested.

## Learning Objectives

- Build an ETL pipeline using Python.
- Practice SQL Server database design and data warehousing.
- Implement SQL transformations for analytical data marts.
- Learn incremental data loading and pipeline monitoring.
- Create Power BI dashboards from structured data.

## Author

Personal data engineering portfolio project.
