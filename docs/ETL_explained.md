

# ETL Pipeline: `students_features.js`

This document explains the **MongoDB ETL aggregation pipeline** used to transform nested `students_raw` documents into a **flat, ML-ready collection** called `students_features`.

---

## **Overview**

* **Input:** `students_raw` collection (nested arrays for `courses` and `grades`)
* **Output:** `students_features` collection (one document per student, with aggregated metrics)
* **Execution:**

```bash
mongosh "$MDB_CONNECTION_STRING" scripts/etl/students_features.js
```

* **Goal:** Compute per-student metrics (`avg_grade`, `max_grade`, `num_courses`) and copy over `fullTime` status in a **flat structure** suitable for machine learning or data analysis.

---

## **Sample Input Document**

```json
{
  "_id": ObjectId("6984a7d65e377cf3801bc677"),
  "student_id": 3,
  "age": 27,
  "courses": [
    { "course": "Statistics", "credits": 3, "grades": [74, 57, 59] },
    { "course": "Linear Algebra", "credits": 4, "grades": [68, 64, 75] }
  ],
  "enrollment_year": 2021,
  "fullTime": false,
  "major": "Math"
}
```

---

## **Step-by-Step Explanation**

### **1️⃣ Flatten the `courses` array**

```js
{ $unwind: "$courses" }
```

* Converts each element of the `courses` array into a separate document.
* **Purpose:** Make per-course calculations easier.

**Result:**

```
Doc 1: { student_id: 3, courses: { course: "Statistics", grades: [74, 57, 59] }, fullTime: false }
Doc 2: { student_id: 3, courses: { course: "Linear Algebra", grades: [68, 64, 75] }, fullTime: false }
```

---

### **2️⃣ Flatten the `grades` array**

```js
{ $unwind: "$courses.grades" }
```

* Converts each grade in a course into a separate document.
* **Purpose:** Enables aggregation per student across **all grades**, not per course.

**Result:**

```
Doc 1: { student_id: 3, grade: 74, fullTime: false }
Doc 2: { student_id: 3, grade: 57, fullTime: false }
Doc 3: { student_id: 3, grade: 59, fullTime: false }
Doc 4: { student_id: 3, grade: 68, fullTime: false }
Doc 5: { student_id: 3, grade: 64, fullTime: false }
Doc 6: { student_id: 3, grade: 75, fullTime: false }
```

---

### **3️⃣ Group by `student_id` to compute metrics**

```js
{
  $group: {
    _id: "$student_id",
    avg_grade: { $avg: "$courses.grades" },
    max_grade: { $max: "$courses.grades" },
    courses_set: { $addToSet: "$courses.course" },
    fullTime: { $first: "$fullTime" }
  }
}
```

**Explanation:**

* `_id: "$student_id"` → groups all documents by student
* `$avg` → computes **average of all grades** for the student
* `$max` → finds **highest grade**
* `$addToSet` → creates a **unique set of courses**
* `$first` → copies `fullTime` boolean from any of the documents (all are same per student)

**Example Result:**

```json
{
  "_id": 3,
  "avg_grade": 66.1667,
  "max_grade": 75,
  "courses_set": ["Statistics", "Linear Algebra"],
  "fullTime": false
}
```

---

### **4️⃣ Project final fields**

```js
{
  $project: {
    student_id: "$_id",
    avg_grade: 1,
    max_grade: 1,
    num_courses: { $size: "$courses_set" },
    fullTime: 1,
    _id: 0
  }
}
```

**Explanation:**

* `student_id: "$_id"` → rename `_id` to `student_id` for clarity
* `avg_grade: 1, max_grade: 1` → keep the aggregated fields
* `num_courses: { $size: "$courses_set" }` → counts total unique courses
* `_id: 0` → remove original `_id` field
* `fullTime: 1` → keep fullTime boolean

**Resulting Document (ML-ready):**

```json
{
  "student_id": 3,
  "avg_grade": 66.1667,
  "max_grade": 75,
  "num_courses": 2,
  "fullTime": false
}
```

---

### **5️⃣ Persist results in a new collection**

```js
{
  $merge: {
    into: "students_features",
    whenMatched: "replace",
    whenNotMatched: "insert"
  }
}
```

**Explanation:**

* **`into: "students_features"`** → writes output to a separate collection
* **`whenMatched: "replace"`** → overwrite existing documents with the same `_id`
* **`whenNotMatched: "insert"`** → insert new documents if not present
* **Benefit:** Idempotent ETL — safe to rerun without duplicates

**Final Collection: `students_features`**

```json
{
  "student_id": 3,
  "avg_grade": 66.1667,
  "max_grade": 75,
  "num_courses": 2,
  "fullTime": false
}
```

---

## **Summary of ETL Operations**

| Stage           | Operator   | Purpose                                                      |
| --------------- | ---------- | ------------------------------------------------------------ |
| Flatten courses | `$unwind`  | One document per course                                      |
| Flatten grades  | `$unwind`  | One document per grade                                       |
| Aggregate       | `$group`   | Compute avg, max, num_courses, copy fullTime                 |
| Select & rename | `$project` | Remove `_id`, rename `_id → student_id`, keep only ML fields |
| Persist         | `$merge`   | Save transformed documents idempotently                      |

---

**✅ Outcome:**

* Nested arrays transformed into **flat, ML-ready features**
* Aggregated metrics per student: `avg_grade`, `max_grade`, `num_courses`, `fullTime`
* Stored safely in a dedicated collection for further analysis or ML pipelines

