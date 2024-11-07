import csv
import random
import pandas as pd
from collections import defaultdict

def generate_groups(num_groups):
    with open('groups.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['GroupID', 'NumStudents', 'NumSubgroups'])
        for i in range(1, num_groups + 1):
            num_students = random.randint(20, 35)
            num_subgroups = 2  
            writer.writerow([f'G{i}', num_students, num_subgroups])

def generate_rooms(num_rooms):
    with open('rooms.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['RoomID', 'Capacity'])
        for i in range(1, num_rooms + 1):
            capacity = random.randint(15, 40)
            writer.writerow([f'R{i}', capacity])

def generate_lecturers(num_lecturers, subjects):
    with open('lecturers.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['LecturerID', 'Subjects', 'Types'])
        for i in range(1, num_lecturers + 1):
            lecturer_subjects = random.sample(subjects, random.randint(1, 3))
            types = random.choice(['Lecture', 'Practice', 'Both'])
            writer.writerow([f'L{i}', ','.join(lecturer_subjects), types])

def generate_subjects(num_subjects):
    with open('subjects.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SubjectID', 'LectureHours', 'PracticeHours', 'RequiresSplit'])
        for i in range(1, num_subjects + 1):
            lecture_hours = random.randint(10, 20)
            practice_hours = random.randint(5, 15)
            requires_split = random.choice(['Yes', 'No'])
            writer.writerow([f'S{i}', lecture_hours, practice_hours, requires_split])

def load_data():
    groups = pd.read_csv('groups.csv')
    rooms = pd.read_csv('rooms.csv')
    lecturers = pd.read_csv('lecturers.csv')
    subjects = pd.read_csv('subjects.csv')
    return groups, rooms, lecturers, subjects

def generate_schedule(groups, rooms, lecturers, subjects):
    schedule = defaultdict(list) 

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods = [1, 2, 3, 4]   

    for _, group in groups.iterrows():
        group_id = group['GroupID']
        for _, subject in subjects.iterrows():
            hours = subject['LectureHours'] + subject['PracticeHours']
            remaining_hours = hours
            
            while remaining_hours > 0:
                day = random.choice(days)
                period = random.choice(periods)
                room = rooms.sample(1).iloc[0]
                lecturer = lecturers.sample(1).iloc[0]

                if group['NumStudents'] <= room['Capacity']:
                    event = {
                        "Day": day,
                        "Period": period,
                        "Subject": subject['SubjectID'],
                        "Room": room['RoomID'],
                        "Lecturer": lecturer['LecturerID'],
                        "Type": "Lecture" if remaining_hours == subject['LectureHours'] else "Practice"
                    }
                    schedule[group_id].append(event)
                    remaining_hours -= 1.5  

    return schedule

def print_schedule(schedule):
    for group, events in schedule.items():
        print(f"\nSchedule for {group}:")
        events = sorted(events, key=lambda x: (x["Day"], x["Period"]))
        for event in events:
            print(f"  {event['Day']} Period {event['Period']} - {event['Subject']} in Room {event['Room']} with {event['Lecturer']} ({event['Type']})")

generate_groups(5)
generate_rooms(6)
generate_subjects(8)
generate_lecturers(4, [f'S{i}' for i in range(1, 9)])

groups, rooms, lecturers, subjects = load_data()
schedule = generate_schedule(groups, rooms, lecturers, subjects)
print_schedule(schedule)