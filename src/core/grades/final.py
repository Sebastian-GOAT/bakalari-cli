from typing import Any, Dict, List

import typer
from rich import print as stdout
from core.data.fetch_data import get_response
from core.data.tokens import update_tokens

def get_final_grades(access_token: str, refresh_token: str, school_url: str):

    path = '/api/3/marks/final'

    res = get_response(access_token, school_url, path)

    if res.status_code == 401:
        update_tokens(refresh_token, school_url)
        res = get_response(access_token, school_url, path)

    if res.ok:
        data = res.json()
        return transform_data(data)
    else:
        stdout("[bold red]❌ ERROR: couldn't fetch the grades")
        raise typer.Exit(code=1)

def transform_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    transformed = []
    years = {}

    for term in data["CertificateTerms"]:
        year_in_school = term["Grade"]

        if year_in_school not in years:
            year = {"YearInSchool": year_in_school, "Semesters": []}
            years[year_in_school] = year
            transformed.append(year)

        subject_names = {
            subject["Id"]: {
                "Name": subject["Name"],
                "Abbrev": subject["Abbrev"]
            } for subject in term["Subjects"]
        }
        semester = {
            "SemesterName": term["SemesterName"],
            "Grades": [
                {
                    "SubjectName": subject_names[mark["SubjectId"]]["Name"],
                    "SubjectAbbrev": subject_names[mark["SubjectId"]]["Abbrev"],
                    "GradeText": mark["MarkText"],
                }
                for mark in term["FinalMarks"]
            ],
        }
        years[year_in_school]["Semesters"].append(semester)

    return transformed