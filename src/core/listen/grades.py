import time
from plyer import notification
from rich import print as stdout
from core.auth.load_config import load_config_formatted
from core.data.fetch_data import get_response
from core.data.tokens import update_tokens

path = '/api/3/marks'

# Previous data + first population
prev_grade_ids = set()

(access_token, refresh_token, school_url) = load_config_formatted()

res = get_response(access_token, school_url, path)

if res.status_code == 401:
    update_tokens(refresh_token, school_url)
    res = get_response(access_token, school_url, path)

if res.ok:
    data = res.json()
    subjects = data['Subjects']

    for subject in subjects:
        for grade in subject['Marks']:
            grade_id = grade['Id']
            prev_grade_ids.add(grade_id)
else:
    stdout("[bold red]❌ ERROR: couldn't fetch the grades")

# Fetching function
def fetch():

    (access_token, refresh_token, school_url) = load_config_formatted()

    res = get_response(access_token, school_url, path)

    if res.status_code == 401:
        update_tokens(refresh_token, school_url)
        res = get_response(access_token, school_url, path)

    if res.ok:
        data = res.json()
        subjects = data['Subjects']

        for subject in subjects:
            subject_name = subject['Subject']['Name']

            for grade in subject['Marks']:
                grade_id = grade['Id']

                if not grade_id in prev_grade_ids:
                    prev_grade_ids.add(grade_id)
                    
                    grade_text = grade['MarkText']
                    grade_caption = grade['Caption']
                    is_points = grade['IsPoints']

                    title = f'{grade_text} points from {subject_name}' if is_points else f'Grade {grade_text} from {subject_name}'

                    notification.notify(
                        title=title,
                        message=grade_caption,
                        app_name='bakalari-cli',
                        timeout=5
                    )
                    time.sleep(5)
    else:
        stdout("[bold red]❌ ERROR: couldn't fetch the grades")