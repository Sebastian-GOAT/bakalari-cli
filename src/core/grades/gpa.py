def calculate_gpa(subjects):

    valid_averages = []

    for subject in subjects:
        average_text = subject.get('AverageText')

        if average_text is None:
            continue

        try:
            average = float(average_text.replace(",", "."))
        except (TypeError, ValueError):
            continue

        if 1 <= average <= 5:
            valid_averages.append(5 - average)

    if not valid_averages:
        return 0.0

    return sum(valid_averages) / len(valid_averages)

def calculate_final_gpa(years):
    valid_grades = []

    for year in years:
        for semester in year.get('Semesters', []):
            for grade_entry in semester.get('Grades', []):
                grade_text = grade_entry.get('GradeText')

                try:
                    grade = float(grade_text.replace(",", "."))
                except (AttributeError, TypeError, ValueError):
                    continue

                if 1 <= grade <= 5:
                    valid_grades.append(5 - grade)

    if not valid_grades:
        return 0.0

    return sum(valid_grades) / len(valid_grades)