import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime


class Sheet():
    



def connect_to_sheets():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open("app_tracker").sheet1

    return sheet



def append_to_sheet(user_input, sheet):
    data = connect_to_nutrix(user_input)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")


    for exercise in data["exercises"]:
        row = [
            date,
            time,
            exercise["name"].title(),
            exercise["duration_min"],
            exercise["nf_calories"]
        ]

    sheet.append_row(row)
    print(f"Logged: {exercise['name']} - {exercise['duration_min']} min")
