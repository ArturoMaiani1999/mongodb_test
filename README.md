
# MongoDB Student Data Pipeline

## 📄 Project Overview

This repository is a **complete data engineering and machine learning pipeline** that demonstrates how to:

1. Generate **synthetic student data**
2. Ingest it into **MongoDB Atlas**
3. Perform **ETL transformations** using MongoDB aggregation pipelines
4. Export flat features to **Pandas**
5. Train a **Random Forest classifier** to identify high-performing students
6. Extract **feature importance** for interpretability

The pipeline is **end-to-end reproducible**, modular, and suitable for learning MongoDB, ETL, and ML workflows.

---

## 🗂 Repository Structure

```
mongo-data-pipeline/
│
├── README.md
├── requirements.txt
├── .env.example          # template for MongoDB credentials
├── .gitignore
│
├── data/
│   ├── raw/              # generated raw JSON data
│   └── derived/          # exported ML-ready CSV
│
├── scripts/
│   ├── generate_data/
│   │   └── generate_students.py
│   │
│   ├── ingest/
│   │   └── insert_students.py
│   │
│   ├── etl/
│   │   └── students_features.js
│   │
│   └── export/
│       └── mongo_to_pandas.py
│
├── ml/
│   └── classification.py   # Random Forest training + feature importance
│
└── notebooks/
    └── exploratory_analysis.ipynb
```

---

## ⚙️ Setup Instructions

1. Clone the repo:

```bash
git clone <your-repo-url>
cd mongo-data-pipeline
```

2. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create `.env` file (example in `.env.example`):

```env
MDB_CONNECTION_STRING=mongodb+srv://<user>:<PASSWORD>@cluster.mongodb.net/arturocluster?retryWrites=true&w=majority
```

* Make sure your **current IP is whitelisted** in MongoDB Atlas Network Access
* Encode special characters in your password (`@ → %40`)

---

## 🏃 Pipeline Execution

### 1️⃣ Generate Synthetic Student Data

```bash
python scripts/generate_data/generate_students.py
```

* Produces `data/raw/students_raw.json`
* Each student has nested `courses` and `grades`

---

### 2️⃣ Ingest Raw Data into MongoDB

```bash
python scripts/ingest/insert_students.py
```

* Reads JSON and inserts into `students_raw` collection
* Idempotent: safe to rerun

---

### 3️⃣ ETL: Create ML-ready Features

```bash
mongosh "$MDB_CONNECTION_STRING" scripts/etl/students_features.js
```

**Purpose:** Transform nested documents into a flat, ML-ready collection `students_features`.

#### **Pipeline Steps**

1. **$unwind: courses**

   * Flatten array of courses → one document per course

```json
{
  "student_id": 3,
  "courses": { "course": "Statistics", "grades": [74,57,59] },
  "fullTime": false
}
```

2. **$unwind: courses.grades** (optional)

   * Flatten each grade → one document per grade

```json
{ "student_id": 3, "grade": 74, "fullTime": false }
```

3. **$group: per student**

   * Aggregate features:

```json
{
  "_id": 3,
  "avg_grade": 66.17,
  "max_grade": 75,
  "num_courses": 2,
  "fullTime": false
}
```

4. **$project**

   * Rename `_id → student_id`
   * Keep only relevant fields for ML

```json
{
  "student_id": 3,
  "avg_grade": 66.17,
  "max_grade": 75,
  "num_courses": 2,
  "fullTime": false
}
```

5. **$merge**

   * Writes to `students_features` collection
   * Idempotent: rerunning pipeline **updates existing documents** without duplicates
   * Ensures a **ready-to-use ML dataset**

---

### 4️⃣ Export Features to Pandas / CSV

```bash
python scripts/export/mongo_to_pandas.py
```

* Exports `students_features` collection to `data/derived/students_features.csv`
* Ready for ML or further analysis

---

### 5️⃣ Train ML Model

```bash
python ml/classification.py
```

**What it does:**

1. Loads `students_features.csv`
2. Creates a binary target: `high_performer` = `avg_grade > median`
3. Trains **Random Forest Classifier**:

* Algorithm: **Random Forest**

  * Ensemble of decision trees
  * Handles small feature sets well
  * Robust to overfitting
* Uses `warm_start=True` and **tqdm progress bar** to track tree-by-tree training
* Prints **Accuracy & F1-score every 10 trees**

4. Computes **feature importance**:

* `clf.feature_importances_` gives the contribution of each feature
* Visualized as a bar chart for interpretability

5. Saves trained model:

```
ml/random_forest_students.pkl
```

---

### 6️⃣ Example Output

```
[10 trees] Accuracy: 0.83, F1: 0.83
[20 trees] Accuracy: 0.83, F1: 0.83
...
[100 trees] Accuracy: 0.83, F1: 0.84
```

* Feature importance:

| Feature     | Importance |
| ----------- | ---------- |
| max_grade   | 0.60       |
| num_courses | 0.25       |
| fullTime    | 0.15       |

---

## 📌 Best Practices

* **Idempotency:** ingestion and ETL can be rerun safely
* **Security:** `.env`, raw CSV/JSON, and trained models are **excluded via `.gitignore`**
* **Modular pipeline:** separates data generation, ingestion, ETL, export, and ML
* **Progress monitoring:** training progress bar with incremental metrics
