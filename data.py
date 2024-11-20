import random
from collections import defaultdict
import math
from generate import generate_groups, generate_subjects, generate_lecturers,generate_rooms
from constants import DAYS, PERIODS_PER_DAY, WEEKS, PERIOD_TIMES
import csv 
from utils import output_conflicts, print_schedule_per_group

# Main execution
groups = generate_groups()
subjects = generate_subjects()
lecturers = generate_lecturers()
rooms_data = generate_rooms()

# Time slots (day and period)
time_slots = [(day, period) for day in DAYS for period in range(1, PERIODS_PER_DAY + 1)]

# Genetic Algorithm Implementation
class Schedule:
    def __init__(self):
        self.assignments = []  # List of assignments
        self.fitness = 0

    def lecturer_conflicts(self, lecturer_time_slots):
        penalty = 0
        for (lecturer, time_slot), assignments in lecturer_time_slots.items():
            if len(assignments) > 1:
                penalty += (len(assignments) - 1) * 10
        return penalty
    
    def group_conflicts(self, group_time_slots):
        penalty = 0
        for (group, time_slot), assignments in group_time_slots.items():
            if len(assignments) > 1:                
                penalty += (len(assignments) - 1) * 10  # 
        return penalty

    def room_conflicts(self, room_time_slots):
        penalty = 0
        for (room, time_slot), assignments in room_time_slots.items():
            if len(assignments) > 1:
                # Check if all assignments are for the same lecture
                first_assignment = assignments[0]
                if first_assignment['class_type'] == 'Lecture':
                    same_lecture = all(
                        a['subject'] == first_assignment['subject'] and
                        a['class_type'] == 'Lecture' and
                        a['lecturer'] == first_assignment['lecturer'] and
                        a['room'] == first_assignment['room']
                        for a in assignments
                    )
                    if not same_lecture:
                        penalty += (len(assignments) - 1) * 5  
                else:
                    # If class type is not 'Lecture', any overlap is a conflict
                    penalty += (len(assignments) - 1) * 5  
        return penalty

    def calculate_fitness(self):
        penalty = 0
        lecturer_time_slots = defaultdict(list)
        group_time_slots = defaultdict(list)
        room_time_slots = defaultdict(list)
        subject_class_counts = defaultdict(int)

        for assignment in self.assignments:             
            key = (assignment['group'], assignment['subject'], assignment['class_type'])       
            lecturer_time_slots[(assignment['lecturer'], assignment['time_slot'])].append(assignment)
            group_time_slots[(assignment['group'], assignment['time_slot'])].append(assignment)
            room_time_slots[(assignment['room'], assignment['time_slot'])].append(assignment)
            subject_class_counts[key] += 1

        penalty += self.lecturer_conflicts(lecturer_time_slots)
        penalty += self.group_conflicts(group_time_slots)
        penalty += self.room_conflicts(room_time_slots)


        # Check individual assignments
        for assignment in self.assignments:
            group = assignment['group']

            # Lecturer qualification
            lecturer_info = next((l for l in lecturers if l['lecturer_name'] == assignment['lecturer']), None)
            if lecturer_info:
                can_teach = lecturer_info['can_teach']
                if not any(ct['subject_name'] == assignment['subject'] and ct['class_type'] == assignment['class_type'] for ct in can_teach):
                    penalty += 5  # Lecturer not qualified
            else:   penalty += 5  # Lecturer not found

            # Room capacity
            if '-' in group:  # subgroup
                group_size = next(gr['num_students'] // gr['num_subgroups'] for gr in groups if group.startswith(gr['group_id']))
            else:
                group_size = next(gr['num_students'] for gr in groups if gr['group_id'] == group)
            room_capacity = next(r['capacity'] for r in rooms_data if r['room_id'] == assignment['room'])
            if group_size > room_capacity:
                penalty += 5  # Room capacity exceeded

        self.fitness = 1 / (1 + penalty)  # Lower penalty means higher fitness

    def mutate(self):
        # Improved mutation that ensures conflicts are less likely
        assignment = random.choice(self.assignments)
        original_time_slot = assignment['time_slot']
        original_lecturer = assignment['lecturer']
        original_group = assignment['group']

        # Attempt to find a new time slot without conflicts
        for _ in range(10):  # Try up to 10 times
            new_time_slot = random.choice(time_slots)
            if new_time_slot != original_time_slot:
                # Check if the new time slot causes conflicts
                lecturer_conflict = any(
                    a for a in self.assignments
                    if a['lecturer'] == original_lecturer and a['time_slot'] == new_time_slot
                )
                group_conflict = any(
                    a for a in self.assignments
                    if a['group'] == original_group and a['time_slot'] == new_time_slot
                )
                if not lecturer_conflict and not group_conflict:
                    assignment['time_slot'] = new_time_slot
                    break

        self.calculate_fitness()

def generate_initial_population(pop_size=100):
    population = []
    for _ in range(pop_size):
        schedule = Schedule()
        time_slot_usage = defaultdict(set)
        subject_class_counts = defaultdict(int)

        for subj in subjects:
            group = subj['group_id']
            subject_name = subj['subject_name']
            lecture_hours = subj['lecture_hours']
            lab_hours = subj['lab_hours']
            total_lecture_classes = int(lecture_hours / 1.5)  # Total lecture classes over the semester
            total_lab_classes = int(lab_hours / 1.5)          # Total lab classes over the semester
            requires_subgroup = subj['requires_subgroup']
            subgroups = next(g['subgroups'] for g in groups if g['group_id'] == group)

            # Schedule lectures
            possible_lecturers = [
                l['lecturer_name'] for l in lecturers
                if any(ct['subject_name'] == subject_name and ct['class_type'] == 'Lecture' for ct in l['can_teach'])
            ]
            if not possible_lecturers:
                continue  # No lecturer available, skip this subject

            # Assign one lecturer per subject/class type
            lecturer = random.choice(possible_lecturers)
            classes_scheduled = 0

            lectures_per_week = math.ceil(total_lecture_classes / WEEKS)
            for week in range(1, WEEKS + 1):
                if classes_scheduled >= lectures_per_week:
                    break
                time_slot = random.choice(time_slots)

                room = random.choice([r['room_id'] for r in rooms_data])
                
                assignment = {
                    'time_slot': time_slot,
                    'group': group,
                    'subject': subject_name,
                    'class_type': 'Lecture',
                    'lecturer': lecturer,
                    'room': room,
                    'total_classes': total_lecture_classes
                }
                schedule.assignments.append(assignment)

                # Update time slot usage
                time_slot_usage[(group, 'group')].add(time_slot)
                time_slot_usage[(lecturer, 'lecturer')].add(time_slot)

                # Update scheduled classes count
                key = (group, subject_name, 'Lecture')
                subject_class_counts[key] += 1

                classes_scheduled += 1

            # Schedule labs
            if lab_hours > 0:
                if requires_subgroup:
                    for subgroup in subgroups:
                        possible_lab_lecturers = [
                            l['lecturer_name'] for l in lecturers
                            if any(ct['subject_name'] == subject_name and ct['class_type'] == 'Lab' for ct in l['can_teach'])
                        ]
                        if not possible_lab_lecturers:
                            continue  # No lecturer available for labs, skip

                        lab_lecturer = random.choice(possible_lab_lecturers)
                        classes_scheduled = 0

                        labs_per_week = math.ceil(total_lab_classes / WEEKS)
                        for week in range(1, WEEKS + 1):
                            if classes_scheduled >= labs_per_week:
                                break
                            time_slot = random.choice(time_slots)

                            room = random.choice([r['room_id'] for r in rooms_data])

                            assignment = {
                                'time_slot': time_slot,
                                'group': subgroup,
                                'subject': subject_name,
                                'class_type': 'Lab',
                                'lecturer': lab_lecturer,
                                'room': room,
                                'total_classes': total_lab_classes
                            }
                            schedule.assignments.append(assignment)

                            # Update time slot usage
                            time_slot_usage[(group, 'group')].add(time_slot)
                            time_slot_usage[(lab_lecturer, 'lecturer')].add(time_slot)

                            # Update scheduled classes count
                            key = (group, subject_name, 'Lab')
                            subject_class_counts[key] += 1

                            classes_scheduled += 1
                else:
                        possible_lab_lecturers = [
                        l['lecturer_name'] for l in lecturers
                        if any(ct['subject_name'] == subject_name and ct['class_type'] == 'Lab' for ct in l['can_teach'])
                        ]
                        if not possible_lab_lecturers:
                            continue  # No lecturer available for labs, skip

                        lab_lecturer = random.choice(possible_lab_lecturers)
                        classes_scheduled = 0

                        labs_per_week = math.ceil(total_lab_classes / WEEKS)
                        for week in range(1, WEEKS + 1):
                            if classes_scheduled >= labs_per_week:
                                break
                            # Find a time slot without conflicts
                            available_time_slots = [ts for ts in time_slots
                                                    if ts not in time_slot_usage[(group, 'group')] and
                                                    ts not in time_slot_usage[(lab_lecturer, 'lecturer')]]
                            if not available_time_slots:
                                break  # No available time slots
                            time_slot = random.choice(available_time_slots)

                            room = random.choice([r['room_id'] for r in rooms_data])

                            assignment = {
                                'time_slot': time_slot,
                                'group': group,
                                'subject': subject_name,
                                'class_type': 'Lab',
                                'lecturer': lab_lecturer,
                                'room': room,
                                'total_classes': total_lab_classes
                            }
                            schedule.assignments.append(assignment)

                            # Update time slot usage
                            time_slot_usage[(group, 'group')].add(time_slot)
                            time_slot_usage[(lab_lecturer, 'lecturer')].add(time_slot)

                            # Update scheduled classes count
                            key = (group, subject_name, 'Lab')
                            subject_class_counts[key] += 1

                            classes_scheduled += 1

        schedule.calculate_fitness()
        population.append(schedule)
    return population

def crossover(parent1, parent2):
    child = Schedule()
    child.assignments = []
    for assignment1, assignment2 in zip(parent1.assignments, parent2.assignments):
        child.assignments.append(random.choice([assignment1, assignment2]))
    child.calculate_fitness()
    return child

def genetic_algorithm():
    population = generate_initial_population()
    generations = 1000

    for generation in range(generations):
        population.sort(key=lambda x: x.fitness, reverse=True)

        # Predator approach: removing bottom 20% population
        num_to_remove = int(0.2 * len(population))
        population = population[:-num_to_remove]

        #Rain
        if len(population) < 90:
            population.extend(generate_initial_population(90 - len(population)))

        if population[0].fitness >= 0.95:
            break  
        new_population = population[:20]
        while len(new_population) < 100:
            parent1 = random.choice(population[:50])
            parent2 = random.choice(population[:50])
            child = crossover(parent1, parent2)
            if random.random() < 0.3:
                child.mutate()
            new_population.append(child)
        population = new_population
    best_schedule = population[0]
    return best_schedule

# Run the genetic algorithm
best_schedule = genetic_algorithm()

print_schedule_per_group(best_schedule, groups)
output_conflicts(best_schedule,subjects, groups)