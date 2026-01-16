# ecommerce-faker-data-generator

## Table of Contents
- [Introduction](#introduction)
- [Project Workflow](#project-workflow)
- [File Structure](#file-structure)
- [Installation & Usage](#installation--usage)

##  Introduction

This is a project for generating synthetic data for an E-commerce OLTP system and then loading the data into local PostgreSQL. The generation is contructed by using Faker library.

## Project Workflow

1. Define the database schema  
2. Generate synthetic data using Python + Faker  
3. Convert/adjust data types to match schema  
4. Insert data into the PostgreSQL Server

## File Structure
```
ecommerce-faker-data-generator/
├── readme.md
├── database.ini
├── poetry.lock
├── pyproject.tom
├── run_data_generation.sh
│
├── src/
    ├── __init__.py
    ├── load_config.py
    ├── create_objects.py
    └── create_tables.py

```

## Installation & Usage
### 1. Clone Repo
~~~
git clone https://github.com/baonguyen-lq/ecommerce-faker-data-generator.git
~~~

### 2. Navigate to the project directory

~~~
cd ecommerce-faker-data-generator
~~~

### 3. Install dependencies

~~~
poetry install
~~~

### 4. Run script

~~~
./run_data_generation.sh
~~~