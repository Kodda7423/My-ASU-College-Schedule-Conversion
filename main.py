from bs4 import BeautifulSoup as bs
import re
import json
import random
import datetime

# Constants
FILE_PATH = "My ASU - Schedule.html"
INFO_LIST = ['class-title', "times-column", "days-column", "instructors-column", "location-column"]
COLORS = {
    "Red": "#FF5733",
    "Green": "#33FF57",
    "Blue": "#3357FF",
    "Yellow": "#FFFF33",
    "Purple": "#9D33FF",
    "Orange": "#FF9D33",
    "Pink": "#FF33A6",
    "Teal": "#33FFF6",
    "Lavender": "#E6E6FA",
    "Gold": "#FFD700"
}

# Initialize variables
iteration = 0
data_list = []

def create_csmo_file(items, filename):
    """
    Create a .csmo file with the given items and filename.
    """
    data = {
        "dataCheck": "69761aa6-de4c-4013-b455-eb2a91fb2b76",
        "saveVersion": 4,
        "schedules": [
            {
                "title": "ASU Class Schedule",
                "items": items
            }
        ],
        "currentSchedule": "0"
    }
    with open(filename, 'w') as file:
        json.dump(data, file, separators=(',', ':'))

def time_range(time_range):
    """
    Convert a time range string to start and end times in 24-hour format.
    """
    start_time, end_time = time_range.split(' - ')
    start_hour, start_minute = map(int, datetime.datetime.strptime(start_time, '%I:%M %p').strftime('%H:%M').split(':'))
    end_hour, end_minute = map(int, datetime.datetime.strptime(end_time, '%I:%M %p').strftime('%H:%M').split(':'))
    return start_hour, start_minute, end_hour, end_minute

def day_dict(days_string):
    """
    Convert a string of days to a dictionary with days of the week as keys and boolean values.
    """
    days_dict = {day: False for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    day_map = {'M': 'Monday', 'Tu': 'Tuesday', 'W': 'Wednesday', 'Th': 'Thursday', 'F': 'Friday', 'S': 'Saturday', 'U': 'Sunday'}
    for day in days_string.split():
        if day in day_map:
            days_dict[day_map[day]] = True
    return days_dict

def rand_color():
    """
    Select a random color from the predefined COLORS dictionary.
    """
    global iteration
    selected_color_hex = list(COLORS.values())[iteration]
    iteration += 1
    return selected_color_hex

def create_item(title, time, days, instructor, location):
    """
    Create a dictionary representing a course item with the given details.
    """
    start_hour, start_minute, end_hour, end_minute = time_range(time)
    day = day_dict(days)
    return {
        "uid": "",
        "type": "Course",
        "title": title,
        "meetingTimes": [
            {
                "uid": "",
                "courseType": "",
                "instructor": instructor,
                "location": location,
                "startHour": start_hour,
                "endHour": end_hour,
                "startMinute": start_minute,
                "endMinute": end_minute,
                "days": {day.lower(): value for day, value in day.items()}
            }
        ],
        "backgroundColor": rand_color()
    }

# Read and parse the HTML file
with open(FILE_PATH, 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = bs(html_content, 'html.parser')
tab_panel = soup.find(id='class-schedule')
pattern = re.compile(r'^class-content-container-\d{5}$')
elements = soup.find_all(id=pattern)

# Extract class IDs
id_list = [element['id'] for element in elements]

# Extract class data
for class_id in id_list:
    class_data = []
    class_div = tab_panel.find(id=class_id)
    for info in INFO_LIST:
        text = ' '.join(class_div.find(class_=info).text.split())
        class_data.append(text)
    data_list.append(class_data)

# Format class data
for data in data_list:
    data[1] = data[1][5:]  # Format time string
    data[2] = data[2][4:]  # Format day string
    data[3] = data[3][11:] # Format instructor string
    data[4] = data[4][15:] # Format location string

# Create items and save to file
items = [create_item(*data) for data in data_list]
create_csmo_file(items, "ASU Class Schedule.csmo")
