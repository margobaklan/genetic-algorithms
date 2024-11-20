from collections import defaultdict
from constants import PERIOD_TIMES, DAYS

# Function to output conflicts
def output_conflicts(schedule, subjects, groups):
    conflicts_found = False
    lecturer_time_slots = defaultdict(list)
    group_time_slots = defaultdict(list)
    room_time_slots = defaultdict(list)
    subject_class_counts = defaultdict(int)
    total_required_classes = {}

    # Prepare a mapping of required total classes per subject/class type
    for subj in subjects:
        group = subj['group_id']
        subject_name = subj['subject_name']
        lecture_hours = subj['lecture_hours']
        lab_hours = subj['lab_hours']
        total_lecture_classes = int(lecture_hours / 1.5)
        total_lab_classes = int(lab_hours / 1.5)
        total_required_classes[(group, subject_name, 'Lecture')] = total_lecture_classes
        total_required_classes[(group, subject_name, 'Lab')] = total_lab_classes
        if subj['requires_subgroup']:
            subgroups = next(g['subgroups'] for g in groups if g['group_id'] == group)
            for subgroup in subgroups:
                total_required_classes[(subgroup, subject_name, 'Lab')] = total_lab_classes

    for assignment in schedule.assignments:
        time_slot = assignment['time_slot']
        lecturer = assignment['lecturer']
        group = assignment['group']
        room = assignment['room']
        subject = assignment['subject']
        class_type = assignment['class_type']
        key = (group, subject, class_type)

        lecturer_time_slots[(lecturer, time_slot)].append(assignment)
        group_time_slots[(group, time_slot)].append(assignment)
        room_time_slots[(room, time_slot)].append(assignment)

        # Count the number of scheduled classes per subject/class type/group
        subject_class_counts[key] += 1

    # Lecturer Conflicts
    print("\nLecturer Conflicts:")
    for key, assignments in lecturer_time_slots.items():
        if len(assignments) > 1:
            conflicts_found = True
            lecturer, time_slot = key
            day, period = time_slot
            print(f"\nLecturer {lecturer} has conflicts at {day} period {period}:")
            for assignment in assignments:
                print(f"  - Group {assignment['group']}, Subject {assignment['subject']} ({assignment['class_type']}), Room {assignment['room']}")

    # Group Conflicts
    print("\nGroup Conflicts:")
    for key, assignments in group_time_slots.items():
        if len(assignments) > 1:
            conflicts_found = True
            group, time_slot = key
            day, period = time_slot
            print(f"\nGroup {group} has conflicts at {day} period {period}:")
            for assignment in assignments:
                print(f"  - Subject {assignment['subject']} ({assignment['class_type']}), Lecturer {assignment['lecturer']}, Room {assignment['room']}")

    # Room Conflicts
    print("\nRoom Conflicts:")
    for key, assignments in room_time_slots.items():
        if len(assignments) > 1:
            conflicts_found = True
            room, time_slot = key
            day, period = time_slot
            print(f"\nRoom {room} has conflicts at {day} period {period}:")
            for assignment in assignments:
                print(f"  - Group {assignment['group']}, Subject {assignment['subject']} ({assignment['class_type']}), Lecturer {assignment['lecturer']}")

    # Over-scheduling Conflicts
    # print("\nOver-Scheduling Conflicts:")
    # for key, scheduled_classes in subject_class_counts.items():
    #     required_classes = total_required_classes.get(key)
    #     # print(required_classes)
    #     group, subject, class_type = key
    #     # print(f"{subject} {class_type} - {scheduled_classes}")
    #     if required_classes is not None and scheduled_classes > required_classes:
    #         conflicts_found = True
    #         group, subject, class_type = key
    #         excess = scheduled_classes - required_classes
    #         print(f"\nGroup {group} has over-scheduled {class_type} for {subject}:")
    #         print(f"  - Scheduled classes: {scheduled_classes}, Required classes: {required_classes}, Excess: {excess}")

    if not conflicts_found:
        print("\nNo conflicts found in the schedule.")

# Output the schedule in a readable format for each group
def print_schedule_per_group(schedule, groups):
    group_schedules = defaultdict(lambda: defaultdict(list))

    for assignment in schedule.assignments:
        group_id = assignment['group']
        day, period = assignment['time_slot']
        start_time, end_time = PERIOD_TIMES[period]
        entry = {
            'Period': f'{start_time} - {end_time}',
            'Subject': assignment['subject'],
            'Class Type': assignment['class_type'],
            'Lecturer': assignment['lecturer'],
            'Room': assignment['room']
        }
        group_schedules[group_id][day].append(entry)

    for group in groups:
        # print(group)
        group_id = group['group_id']
        print(f'\nSchedule for Group {group_id}:')
        for day in DAYS:
            print(f'\n{day.upper()}')
            if day in group_schedules[group_id]:
                day_schedule = sorted(group_schedules[group_id][day], key=lambda x: [k for k, v in PERIOD_TIMES.items() if v[0] == x['Period'].split(' - ')[0]][0])
                for entry in day_schedule:
                    print(f"{entry['Period']} {entry['Subject']} ({entry['Class Type']}) - {entry['Lecturer']}, Room: {entry['Room']}")
            else:
                print('No classes scheduled.')
        # Print subgroup schedules
        for subgroup_id in group['subgroups']:
            # subgroup_id = subgroup_info['subgroup_id']
            print(f'\nSchedule for Subgroup {subgroup_id}:')
            if subgroup_id in group_schedules and group_schedules[subgroup_id]:
                for day in DAYS:
                    if day in group_schedules[subgroup_id] and group_schedules[subgroup_id][day]:
                        day_schedule = sorted(group_schedules[subgroup_id][day], key=lambda x: [k for k, v in PERIOD_TIMES.items() if v[0] == x['Period'].split(' - ')[0]][0])
                        for entry in day_schedule:
                            print(f'\n{day.upper()}')
                            print(f"{entry['Period']} {entry['Subject']} ({entry['Class Type']}) - {entry['Lecturer']}, Room: {entry['Room']}")
            else:
                print('No classes scheduled.')