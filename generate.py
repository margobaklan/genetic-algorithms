from constants import NUM_GROUPS, NUM_SUBGROUPS, GROUP_PREFIX, SUBJECT_NAMES, LECTURER_NAMES, LECTURER_SUBJECTS, NUM_ROOMS
import random
import csv

# Load data from CSV
def load_csv(file_name):
    with open(file_name, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Generate groups
def generate_groups(file_name='groups.csv'):
    group_data = load_csv(file_name)
    groups = []
    for row in group_data:
        groups.append({
            'group_id': row['group_id'],
            'num_students': int(row['num_students']),
            'num_subgroups': int(row['num_subgroups']),
            'subgroups': [f"{row['group_id']}-S{i+1}" for i in range(int(row['num_subgroups']))]
        })
    return groups

# Generate subjects
def generate_subjects(file_name='subjects.csv'):
    subject_data = load_csv(file_name)
    subjects = []
    for row in subject_data:
        subjects.append({
            'group_id': row['group_id'],
            'subject_name': row['subject_name'],
            'lecture_hours': int(row['lecture_hours']),
            'lab_hours': int(row['lab_hours']),
            'requires_subgroup': row['requires_subgroup'].lower() == 'true'
        })
    return subjects

# Generate lecturers
def generate_lecturers(file_name='lecturers.csv'):
    lecturer_data = load_csv(file_name)
    lecturers = {}
    for row in lecturer_data:
        if row['lecturer_name'] not in lecturers:
            lecturers[row['lecturer_name']] = []
        lecturers[row['lecturer_name']].append({
            'subject_name': row['subject_name'],
            'class_type': row['class_type']
        })
    return [{'lecturer_name': name, 'can_teach': subjects} for name, subjects in lecturers.items()]

# Generate rooms
def generate_rooms(file_name='rooms.csv'):
    room_data = load_csv(file_name)
    rooms = []
    for row in room_data:
        rooms.append({
            'room_id': row['room_id'],
            'capacity': int(row['capacity'])
        })
    return rooms

