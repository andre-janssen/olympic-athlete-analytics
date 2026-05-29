# Olympic Athlete Analytics

End-to-end data pipeline and analysis for Olympic athlete performance data (1960–2016), built for **SportsStats** — a platform delivering data-driven insights to sports journalists and elite personal trainers.

---

## Project Overview

This project transforms raw Olympic athlete data into a structured PostgreSQL data warehouse and derives actionable insights across three analytical dimensions:

- **Peak age analysis** — when do athletes in each sport reach their performance peak?
- **Career transition paths** — which sports share compatible athlete profiles for post-peak transitions?
- **Age and medal efficiency** — how much does age actually affect medal probability?

### Target audiences

| Audience | Use case |
|---|---|
| Sports journalists | Story-ready insights with surprising, data-backed narratives |
| Elite personal trainers | Evidence-based recommendations for athlete career planning |

---

## Repository Structure

```
olympic-athlete-analytics/
│
├── README.md                       ← This file
├── .env.example                    ← Environment variable template
├── .gitignore                      ← Excludes raw data and credentials
│
├── data/
│   └── olympics.csv                ← Raw data (not tracked by Git)
│
├── database/
│   └── setup.sql                   ← PostgreSQL schema (star schema)
│
├── etl/
│   └── import.py                   ← ETL pipeline: CSV → PostgreSQL
│
├── analysis/
│   └── olympics_analysis.ipynb     ← Exploratory analysis and insights
│
└── docs/
    └── erd.png                     ← Entity Relationship Diagram
```

---

## Data Model

The database follows a **star schema** with one fact table and six dimension tables.

![ERD](docs/erd.png)

### Tables

| Table | Description |
|---|---|
| `fact_medals` | Central fact table — one row per athlete participation |
| `dim_athletes` | Athlete master data (name, sex) |
| `dim_event` | Olympic events with sport reference |
| `dim_sport` | Sport categories |
| `dim_date` | Continuous year dimension (no gaps) |
| `dim_medal` | Medal types (Gold, Silver, Bronze) |
| `dim_countries` | Countries with NOC codes |

### Key design decisions

- `age_at_event`, `body_size_at_event`, `body_weight_at_event` stored in `fact_medals` — not in `dim_athletes` — because these attributes change over an athlete's career
- `dim_date` uses a continuous range (not just years with events) to enable gap-free time series analysis
- `dim_event` is time-agnostic — "100m Sprint" is one entry regardless of how many Olympics it appeared in; the year reference is in `fact_medals`
- NOC code used as the unique country identifier (more stable than country names across political changes)

---

## Dataset

**Source:** [120 years of Olympic history: athletes and results](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) (Kaggle)

**Scope:** Summer and Winter Olympics, filtered to 1960–2016

| Metric | Value |
|---|---|
| Raw entries | 216,784 |
| Entries after 1960 filter | 165,978 |
| Unique athletes | 87,734 |
| Sports | 49 |
| Countries (NOC) | 222 |
| Events | 3,576 |

> The raw data file `olympics.csv` is excluded from this repository. Download it from Kaggle and place it in the `data/` folder before running the pipeline.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data storage | PostgreSQL |
| ETL pipeline | Python · pandas · SQLAlchemy · psycopg2 |
| Analysis | Jupyter Notebook · pandas · NumPy · scikit-learn |
| Environment | python-dotenv |

---

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL (local or remote)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/andre-janssen/olympic-athlete-analytics.git
cd olympic-athlete-analytics
```

### 2. Install dependencies

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv scikit-learn jupyter
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```dotenv
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/your_database
```

### 4. Add raw data

Download `olympics.csv` from Kaggle and place it in the `data/` folder:

```
data/
└── olympics.csv
```

### 5. Set up the database schema

Run `setup.sql` in pgAdmin or via psql:

```bash
psql -U postgres -d your_database -f database/setup.sql
```

### 6. Run the ETL pipeline

```bash
python etl/import.py
```

Expected output:

```
dim_date:       57 rows
dim_sport:      49 rows
dim_medal:       3 rows
dim_athletes: 87734 rows
dim_countries:  222 rows
dim_event:     3576 rows
fact_medals: 165978 rows
All tables imported successfully.
```

---

## Key Insights

*Coming soon — to be derived from the analysis notebook.*

---

## Limitations

- Body measurements (`body_size`, `body_weight`) reflect a single snapshot per athlete — changes over a career are not captured
- Dataset ends in 2016 — newer sports (skateboarding, climbing, surfing) and updated training methods are not represented
- Career transition analysis shows only successful cases (survivorship bias)
- Body profile similarity does not account for motor skills, cognitive demands, or training background

---

## Author

**Andre Janssen**
Data Analytics · [GitHub](https://github.com/andre-janssen)

*Project developed as part of a Data Analytics continuing education program (2026).*
