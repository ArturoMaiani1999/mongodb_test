import random
import json
from pathlib import Path
from datetime import datetime

import numpy as np


# --------------------
# Configuration
# --------------------
RANDOM_SEED = 42
N_STUDENTS = 10_000
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "students_raw.json"


# --------------------
# Setup
# --------------------
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------
# Data generation
# --------------------
MAJORS = ["CS", "Math", "Physics", "Economics"]
COURSES = {
    "CS": ["Algorithms", "Databases", "ML"],
    "Math": ["Calculus", "Linear Algebra", "Statistics"],
    "Physics": ["Mechanics", "Electromagnetism"],
    "Economics": ["Micro", "Macro"]
}


def generate_student(student_id: int) -> dict:
    major = random.choice(MAJORS)
    full_time = random.random() < 0.7  # 70% full-time

    base_performance = {
        "CS": 78,
        "Math": 75,
        "Physics": 73,
        "Economics": 76
    }[major]

    # Full-time students slightly outperform part-time
    performance_shift = 5 if full_time else -2

    courses = []
    for course in random.sample(COURSES[major], k=2):
        grades = np.clip(
            np.random.normal(
                loc=base_performance + performance_shift,
                scale=8,
                size=3
            ),
            50,
            100
        ).astype(int).tolist()

        courses.append({
            "course": course,
            "credits": random.choice([3, 4]),
            "grades": grades
        })

    return {
        "student_id": student_id,
        "age": random.randint(18, 30),
        "major": major,
        "enrollment_year": random.choice([2019, 2020, 2021, 2022]),
        "fullTime": full_time,
        "courses": courses,
        "generated_at": datetime.utcnow().isoformat()
    }


# --------------------
# Generate dataset
# --------------------
def main():
    students = [generate_student(i) for i in range(1, N_STUDENTS + 1)]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(students, f, indent=2)

    print(f"Generated {len(students)} students")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
