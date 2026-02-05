// --------------------
// students_features.js
// ETL aggregation pipeline
// --------------------

// Connects to the current database (run with: mongosh "$MDB_CONNECTION_STRING" etl/students_features.js)

db.students_raw.aggregate([
  // 1️⃣ Flatten the courses array
  { $unwind: "$courses" },

  // 2️⃣ Flatten the grades array
  { $unwind: "$courses.grades" },

  // 3️⃣ Group by student_id to compute metrics
  {
    $group: {
      _id: "$student_id",
      avg_grade: { $avg: "$courses.grades" },
      max_grade: { $max: "$courses.grades" },
      courses_set: { $addToSet: "$courses.course" },
      fullTime: { $first: "$fullTime" }  // copy fullTime
    }
  },

  // 4️⃣ Project final fields
  {
    $project: {
      student_id: "$_id",
      avg_grade: 1,
      max_grade: 1,
      num_courses: { $size: "$courses_set" },
      fullTime: 1,
      _id: 0
    }
  },

  // 5️⃣ Persist results in a new collection
  {
    $merge: {
      into: "students_features",   // target collection
      whenMatched: "replace",      // overwrite existing document for same student_id
      whenNotMatched: "insert"     // insert new documents
    }
  }
]);

print("ETL completed: students_features updated.");
