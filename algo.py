import random

# Constants
COURSE_DURATION_MINUTES = 45

def generate_gene(year_id, available_teachers, available_courses, available_classrooms, available_timeslots):
    """
    Generate a random gene (course assignment) for a specific year.
    """
    course = random.choice(available_courses)  # Randomly choose a course for the year
    teacher = random.choice([t for t in available_teachers if course['id'] in t['courses']])  # Select a teacher
    classroom = random.choice(available_classrooms)  # Choose a classroom
    timeslot = random.choice(available_timeslots)  # Choose a timeslots

    return {
        'year_id': year_id,
        'course': course['course_name'],
        'teacher': teacher['id'],
        'classroom': classroom['id'],
        'timeslot': timeslot
    }
def assign_teacher_to_class(class_day, teacher):
    
    if class_day in teacher['unavailability']:
        return False  # Teacher is unavailable on this day
    else:
        # Proceed with assignment
        return True


import random

def generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours):
    population = []

    for _ in range(population_size):
        individual = []
        teacher_workload = {teacher['id']: 0 for teacher in teachers}
        year_timeslot_usage = {year['id']: [] for year in years}

        for year in years:
            year_timetable = []
            courses_for_year = year_courses[year['id']]

            for course in courses_for_year:
                course_duration_hours = course['hours']
                slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES

                for _ in range(int(slots_needed)):
                    # Filter teachers based on course they can teach and their max workload
                    available_teachers = [
                        t for t in teachers 
                        if course['id'] in t['courses'] and 
                        teacher_workload[t['id']] + (COURSE_DURATION_MINUTES / 60) <= teacher_max_hours[t['id']]
                    ]

                    if not available_teachers:
                        raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

                    # Find available timeslots not yet used in this year
                    available_timeslots = [
                        ts for ts in timeslots 
                        if (ts['day'], ts['slot']) not in year_timeslot_usage[year['id']]
                    ]

                    if not available_timeslots:
                        raise Exception(f"No available timeslots for year {year['name']} to schedule {course['course_name']}")

                    # Shuffle the available timeslots to maintain randomness
                    random.shuffle(available_timeslots)

                    # Try to generate a valid gene
                    assigned = False
                    for ts in available_timeslots:
                        # Filter teachers based on unavailability for this specific timeslot
                        available_teachers_for_slot = [
                            t for t in available_teachers 
                            if assign_teacher_to_class(ts['day'], t)
                        ]

                        if available_teachers_for_slot:
                            # Generate the gene with available resources
                            gene = generate_gene(
                                year_id=year['id'], 
                                available_teachers=available_teachers_for_slot, 
                                available_courses=[course], 
                                available_classrooms=classrooms, 
                                available_timeslots=[ts]
                            )

                            # Update teacher workload
                            teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60
                            # Mark the timeslot as used for this year
                            year_timeslot_usage[year['id']].append((gene['timeslot']['day'], gene['timeslot']['slot']))
                            # Add the scheduled class (gene) to the year timetable
                            year_timetable.append(gene)

                            assigned = True
                            break  # Exit the loop once a class is successfully assigned

                    if not assigned:
                        raise Exception(f"Could not assign a teacher for {course['course_name']} in year {year['name']} after checking all available timeslots.")

            # Add the year timetable to the individual
            individual.append(year_timetable)
        # Add the individual (complete timetable for all years) to the population
        population.append(individual)

    return population

def display_population(population):
    """
    Display the generated population in a readable format.
    """
    for idx, individual in enumerate(population):
        # print(f"\nIndividual {idx + 1}:")
        for year_timetable in individual:
            for gene in year_timetable:
                print(f"  {gene['year_id']}- Course: {gene['course']}, TeachID: {gene['teacher']}, "
                      f"ClassID: {gene['classroom']},{gene['timeslot']['day']}  {gene['timeslot']['start_time']} - {gene['timeslot']['end_time']} Slot {gene['timeslot']['slot']}")

def fitness_function(individual, teacher_max_hours):
    """
    Evaluate the fitness of an individual.
    """
    fitness = 0
    gap_penalty = 5
    teacher_timeslots = {}
    classroom_timeslots = {}
    teacher_workload = {teacher['id']: 0 for teacher in teachers}
    year_timeslot_usage = {}

    for year_timetable in individual:
        day_slots = {}  # Reset day_slots for each year timetable
        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            day = gene['timeslot']['day']
            slot = gene['timeslot']['slot']
            timeslot = (day, slot)

            # Track teacher timeslots
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []

            if timeslot in teacher_timeslots[teacher_id]:
                fitness -= 10  # Teacher overlap penalty
            else:
                teacher_timeslots[teacher_id].append(timeslot)
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60

            # Track classroom timeslots
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []

            if timeslot in classroom_timeslots[classroom_id]:
                fitness -= 10  # Classroom overlap penalty
            else:
                classroom_timeslots[classroom_id].append(timeslot)

            # Track year timeslot usage
            year_id = gene['year_id']
            if year_id not in year_timeslot_usage:
                year_timeslot_usage[year_id] = []

            if timeslot in year_timeslot_usage[year_id]:
                fitness -= 10  # Year overlap penalty
            else:
                year_timeslot_usage[year_id].append(timeslot)

            # Track the slots per day for gap detection
            if day not in day_slots:
                day_slots[day] = []
            day_slots[day].append(slot)

        for day, slots in day_slots.items():
            slots.sort()  # Sort slots to ensure they are consecutive
            for i in range(len(slots) - 1):
                current_slot = slots[i]
                next_slot = slots[i + 1]

                if next_slot > current_slot + 1:  # Gap detected
                    gap_size = next_slot - (current_slot + 1)
                    fitness -= gap_penalty * gap_size
                    #* gap_size

    # Check if teacher workload exceeds max allowed hours
    for teacher_id, workload in teacher_workload.items():
        if workload > teacher_max_hours.get(teacher_id, float('inf')):
            fitness -= 11  # Workload penalty

    return fitness
                    # Determine if this gap should be penalized
                    # Assuming morning session ends at a specific slot (e.g., 11 for 1-11 slots)
                    # and evening starts at a specific slot (e.g., 3 for 12-15 slots)
def crossover(parent1, parent2):
    """
    Perform random crossover between two parents to create two new individuals.
    """
    assert len(parent1) == len(parent2), "The number of years must be fixed."

    child1, child2 = [], []

    for i in range(len(parent1)):
        if random.random() < 0.5:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])

    return child1, child2

def mutate(individual, mutation_rate, teachers, classrooms, timeslots):
    """
    Apply mutation to an individual by randomly changing the teacher, classroom, and timeslot of one gene per year.
    Mutation occurs randomly once per year if the mutation rate condition is met.
    """
    for year_timetable in individual:
        # Check if mutation should occur for this year (one mutation per year)
        if random.random() < mutation_rate:
            # Select a random index (gene) in the year timetable to mutate
            mutation_index = random.randint(0, len(year_timetable) - 1)
            mutation_choice = random.choice(['teacher', 'classroom', 'timeslot'])

            # Apply the mutation based on the randomly chosen mutation type
            if mutation_choice == 'teacher':
                current_course = year_timetable[mutation_index]['course']
                available_teachers = [t for t in teachers if current_course in t['courses']]
                if available_teachers:
                    new_teacher = random.choice(available_teachers)
                    year_timetable[mutation_index]['teacher'] = new_teacher['id']

            elif mutation_choice == 'classroom':
                new_classroom = random.choice(classrooms)
                year_timetable[mutation_index]['classroom'] = new_classroom['id']

            elif mutation_choice == 'timeslot':
                new_timeslot = random.choice(timeslots)
                year_timetable[mutation_index]['timeslot'] = new_timeslot

    return individual

def tournament_selection(population, fitness_values, k=3):#tkhayar best 1 mn 3 random, ttrepeata 
    """
    Selects two individuals from the population using tournament selection.
    """
    tournament_indices = random.sample(range(len(population)), k)
    tournament_individuals = [population[i] for i in tournament_indices]
    tournament_fitness = [fitness_values[i] for i in tournament_indices]

    sorted_indices = sorted(range(len(tournament_fitness)), key=lambda i: tournament_fitness[i], reverse=True)
    # print('Tournament:', tournament_individuals[sorted_indices[0]], tournament_individuals[sorted_indices[1]])
    parent1 = tournament_individuals[sorted_indices[0]]
    parent2 = tournament_individuals[sorted_indices[1]]
    

    return parent1, parent2

def repair(individual, teachers, classrooms, timeslots, teacher_max_hours):
    """
    Repairs an individual (chromosome) by resolving hard constraint violations 
    (e.g., teacher conflicts, classroom conflicts, workload limits), and minimizing gaps between slots.
    
    Parameters:
    - individual: The individual (timetable) to be repaired.
    - teachers: List of teachers.
    - classrooms: List of classrooms.
    - timeslots: List of available timeslots.
    - teacher_max_hours: Max teaching hours per teacher.

    Returns:
    - Repaired individual.
    """
    teacher_timeslots = {}  # Dictionary to track which timeslots a teacher has been assigned
    classroom_timeslots = {}  # Track which timeslots a classroom has been occupied
    teacher_workload = {teacher['id']: 0 for teacher in teachers}  # Initialize workload dictionary

    # Repair hard constraint violations
    for year_timetable in individual:
        day_slots = {}  # Track timeslots per day to detect gaps

        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            timeslot = (gene['timeslot']['day'], gene['timeslot']['slot'])  # Combine day and slot
            day = gene['timeslot']['day']
            slot = gene['timeslot']['slot']

            # ---- Repair Teacher Conflicts ----
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []
            if timeslot in teacher_timeslots[teacher_id] or teacher_workload[teacher_id] >= teacher_max_hours[teacher_id]:
                # Teacher conflict or exceeding max hours, so repair the gene
                available_teachers = [t for t in teachers if gene['course'] in t['courses']]
                if available_teachers:
                    new_teacher = random.choice(available_teachers)
                else:
                    new_teacher = random.choice(teachers)
                gene['teacher'] = new_teacher['id']
                teacher_workload[new_teacher['id']] += COURSE_DURATION_MINUTES / 60  # Update workload
            else:
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60

            teacher_timeslots[teacher_id].append(timeslot)

            # ---- Repair Classroom Conflicts ----
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []
            if timeslot in classroom_timeslots[classroom_id]:
                # Classroom conflict, so repair the gene
                new_classroom = random.choice(classrooms)
                gene['classroom'] = new_classroom['id']

            classroom_timeslots[classroom_id].append(timeslot)

            # Track day slots for gap detection
            if day not in day_slots:
                day_slots[day] = []
            day_slots[day].append(slot)

        # ---- Repair Gaps in Timetables ----
        for day, slots in day_slots.items():
            slots.sort()  # Sort slots to find gaps

            # Try to reduce gaps by shifting or swapping slots
            for i in range(len(slots) - 1):
                current_slot = slots[i]
                next_slot = slots[i + 1]

                if next_slot > current_slot + 1:  # Gap detected
                    gap_size = next_slot - (current_slot + 1)

                    # Attempt to fill the gap by shifting a nearby timeslot or reassigning
                    for j, gene in enumerate(year_timetable):
                        if gene['timeslot']['day'] == day and gene['timeslot']['slot'] == next_slot:
                            available_timeslots = [ts for ts in timeslots if ts['slot'] == current_slot + 1 and ts not in classroom_timeslots[gene['classroom']]]
                            if available_timeslots:
                                # Shift the next slot to close the gap
                                gene['timeslot'] = available_timeslots[0]
                                classroom_timeslots[gene['classroom']].append((day, current_slot + 1))
                                break

    return individual

years = [
    {'id': 1, 'name': 'Year 1'},
    {'id': 2, 'name': 'Year 2'},
    {'id': 3, 'name': 'Year 3'},
    {'id': 4, 'name': 'Year 4'},
    # {'id': 5, 'name': 'Year 5'}
]

timeslots = [
    # Sunday (slots 1-7)
    {'day': 'Sunday', 'slot': 1, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Sunday', 'slot': 2, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Sunday', 'slot': 3, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Sunday', 'slot': 4, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Sunday', 'slot': 5, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Sunday', 'slot': 6, 'start_time': '14:45', 'end_time': '15:30'},
    {'day': 'Sunday', 'slot': 7, 'start_time': '15:30', 'end_time': '16:15'},

    # Monday (slots 8-14)
    {'day': 'Monday', 'slot': 8, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Monday', 'slot': 9, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Monday', 'slot': 10, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Monday', 'slot': 11, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Monday', 'slot': 12, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Monday', 'slot': 13, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Monday', 'slot': 14, 'start_time': '14:45', 'end_time': '15:30'},
    {'day': 'Monday', 'slot': 15, 'start_time': '15:30', 'end_time': '16:15'},

    # Tuesday (slots 16-22)
    {'day': 'Tuesday', 'slot': 16, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Tuesday', 'slot': 17, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Tuesday', 'slot': 18, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Tuesday', 'slot': 19, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Tuesday', 'slot': 20, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Tuesday', 'slot': 21, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Tuesday', 'slot': 22, 'start_time': '14:45', 'end_time': '15:30'},

    # Wednesday (slots 23-29)
    {'day': 'Wednesday', 'slot': 23, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Wednesday', 'slot': 24, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Wednesday', 'slot': 25, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Wednesday', 'slot': 26, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Wednesday', 'slot': 27, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Wednesday', 'slot': 28, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Wednesday', 'slot': 29, 'start_time': '14:45', 'end_time': '15:30'},

    # Thursday (slots 30-36)
    {'day': 'Thursday', 'slot': 30, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Thursday', 'slot': 31, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Thursday', 'slot': 32, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Thursday', 'slot': 33, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Thursday', 'slot': 34, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Thursday', 'slot': 35, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Thursday', 'slot': 36, 'start_time': '14:45', 'end_time': '15:30'}
]

teacher_max_hours = {
    101: 26, 
    102: 26, 
    103: 26, 
    104: 26, 
    105: 26
}

teachers = [
    {'id': 101, 'name': 'John Smith', 'courses': [1, 4, 7, 10, 14,15], 'state': 'working','unavailability': ['Tuesday']},  
    {'id': 102, 'name': 'Sarah Johnson', 'courses': [2, 3, 8, 11], 'state': 'working','unavailability': ['Tuesday']},  
    {'id': 103, 'name': 'Michael Lee', 'courses': [1, 5, 6, 9, 12], 'state': 'working','unavailability': ['Tuesday']}, 
    {'id': 104, 'name': 'Emily Davis', 'courses': [4, 13, 15, 9, 10], 'state': 'working','unavailability': ['Tuesday']},  
    {'id': 105, 'name': 'David Brown', 'courses': [3, 7, 12, 11,17], 'state': 'working','unavailability': ['Tuesday']} 
]


year_courses = {
    1: [
        # {'id': 1, 'course_name': 'اللغة العربية', 'hours': 2.25}, 
        {'id': 2, 'course_name': 'اللغة الفرنسية', 'hours': 4.5},  
        {'id': 3, 'course_name': 'اللغة الانجليزية', 'hours': 2.25},  # 1.5 hours + 45 minutes
        {'id': 4, 'course_name': 'الرياضيات', 'hours': 0.75},  # 3 x 1.5 hours
        {'id': 7, 'course_name': 'التربية الإسلامية', 'hours': 1.5},  # 1.5 hours
        {'id': 8, 'course_name': 'التاريخ و الجغرافيا', 'hours': 2.25},  # 2 x 1.125 hours
        {'id': 9, 'course_name': 'التربية المدنية', 'hours': 1.5},  # 1.5 hours
        {'id': 10, 'course_name': 'التربية الفنية', 'hours': 1.5},  # 1.5 hours
        {'id': 11, 'course_name': 'التربية الموسيقية', 'hours': 1.5},  # 1.5 hours
        {'id': 12, 'course_name': 'التربية البدنية', 'hours': 2.25},  # 2 x 1.125 hours
        {'id': 13, 'course_name': 'اللغة الأمازيغية', 'hours': 1.5},  # 1.5 hours
        # {'id': 14, 'course_name': 'علوم الطبيعة و الحياة', 'hours': 2.25},  # 2 x 1.125 hours
        # {'id': 15, 'course_name': 'العلوم الفيزيائية و التكنولوجيا', 'hours': 2.25},  # 2 x 1.125 hours
        # {'id': 17, 'course_name': 'الاعلام الآلي', 'hours': 1.5}  # 1.5 hours
    ],
    2: [
        # {'id': 1, 'course_name': 'اللغة العربية', 'hours':1.5},
        # {'id': 2, 'course_name': 'اللغة الفرنسية', 'hours': 1.5},
        {'id': 3, 'course_name': 'اللغة الانجليزية', 'hours': 2.25},
        {'id': 4, 'course_name': 'الرياضيات', 'hours': 1.5},
        {'id': 7, 'course_name': 'التربية الإسلامية', 'hours': 1.5},
        {'id': 8, 'course_name': 'التاريخ و الجغرافيا', 'hours': 2.25},
        {'id': 9, 'course_name': 'التربية المدنية', 'hours': 1.5},
        {'id': 10, 'course_name': 'التربية الفنية', 'hours': 1.5},
        {'id': 11, 'course_name': 'التربية الموسيقية', 'hours': 1.5},
        {'id': 12, 'course_name': 'التربية البدنية', 'hours': 2.25},
        # {'id': 13, 'course_name': 'اللغة الأمازيغية', 'hours': 1.5},
        {'id': 14, 'course_name': 'علوم الطبيعة و الحياة', 'hours': 2.25},
        # {'id': 15, 'course_name': 'العلوم الفيزيائية و التكنولوجيا', 'hours': 2.25},
        # {'id': 17, 'course_name': 'الاعلام الآلي', 'hours': 1.5}
    ],
    3: [
        # {'id': 1, 'course_name': 'اللغة العربية', 'hours': 2.25},
        # {'id': 2, 'course_name': 'اللغة الفرنسية', 'hours': 1.5},
        {'id': 3, 'course_name': 'اللغة الانجليزية', 'hours': 1.5},
        {'id': 4, 'course_name': 'الرياضيات', 'hours': 1.5},
        {'id': 7, 'course_name': 'التربية الإسلامية', 'hours': 1.5},
        {'id': 8, 'course_name': 'التاريخ و الجغرافيا', 'hours': 2.25},
        {'id': 9, 'course_name': 'التربية المدنية', 'hours': 1.5},
        {'id': 10, 'course_name': 'التربية الفنية', 'hours': 1.5},
        {'id': 11, 'course_name': 'التربية الموسيقية', 'hours': 1.5},
        {'id': 12, 'course_name': 'التربية البدنية', 'hours': 2.25},
        {'id': 13, 'course_name': 'اللغة الأمازيغية', 'hours': 1.5},
        {'id': 14, 'course_name': 'علوم الطبيعة و الحياة', 'hours': 2.25},
        # {'id': 15, 'course_name': 'العلوم الفيزيائية و التكنولوجيا', 'hours': 2.25},
        # {'id': 17, 'course_name': 'الاعلام الآلي', 'hours': 1.5}
    ],
    4: [
        # {'id': 1, 'course_name': 'اللغة العربية', 'hours':1.5},
        # {'id': 2, 'course_name': 'اللغة الفرنسية', 'hours': 1.5},
        {'id': 3, 'course_name': 'اللغة الانجليزية', 'hours': 2.25},
        {'id': 4, 'course_name': 'الرياضيات', 'hours': 1.5},
        {'id': 7, 'course_name': 'التربية الإسلامية', 'hours': 1.5},
        {'id': 8, 'course_name': 'التاريخ و الجغرافيا', 'hours': 2.25},
        {'id': 9, 'course_name': 'التربية المدنية', 'hours': 1.5},
        {'id': 10, 'course_name': 'التربية الفنية', 'hours': 1.5},
        {'id': 11, 'course_name': 'التربية الموسيقية', 'hours': 1.5},
        {'id': 12, 'course_name': 'التربية البدنية', 'hours': 2.25},
        {'id': 13, 'course_name': 'اللغة الأمازيغية', 'hours': 1.5},
        {'id': 14, 'course_name': 'علوم الطبيعة و الحياة', 'hours': 2.25},
        # {'id': 15, 'course_name': 'العلوم الفيزيائية و التكنولوجيا', 'hours': 2.25},
        # {'id': 17, 'course_name': 'الاعلام الآلي', 'hours': 1.5}
    ]
}



classrooms = [
    {'id': 101, 'name': 'Room A'},
    {'id': 102, 'name': 'Room B'},
    {'id': 103, 'name': 'Lab 1'},
    {'id': 104, 'name': 'Room C'},
    {'id': 105, 'name': 'Lab 3'},
    {'id': 106, 'name': 'Room D'},
    {'id': 107, 'name': 'Room E'},
    {'id': 108, 'name': 'Lab 2'},   
    {'id': 109, 'name': 'Lab 4'}
]



POPULATION_SIZE = 10
MUTATION_RATE = 0.1
NUM_GENERATIONS = 10000
TOURNAMENT_SIZE = 3
RESET_THRESHOLD = -600
STOP_THRESHOLD = 0
population = generate_population(POPULATION_SIZE, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours)

# Run Genetic Algorithm
for generation in range(NUM_GENERATIONS):
    # Evaluate Fitness
    fitness_values = [fitness_function(individual, teacher_max_hours) for individual in population]

    
    # Print Fitness for Each Individual
    print(f"Generation {generation}:")
    for i, fitness in enumerate(fitness_values):
        print(f"  Individual {i + 1}: Fitness = {fitness}")

    if max(fitness_values) >= STOP_THRESHOLD:
      print("Stopping early due to fitness threshold.")
      best_index = fitness_values.index(max(fitness_values))
      print(f"Best Fitness of Generation {generation}: {fitness_values[best_index]}")
      print(f"Best Solution of Generation {generation} before fixing:")
      display_population([population[best_index]])


      break
    # Check if all fitness values are the same and below the reset threshold
    if len(set(fitness_values)) == 1 or min(fitness_values) <= RESET_THRESHOLD:
        print("Resetting population due to no improvement.")

        population = generate_population(POPULATION_SIZE, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours)
        if len(set(fitness_values)) == 1: print("All individuals have the same fitness value. Stopping early.")
        if min(fitness_values) <= RESET_THRESHOLD: print("All individuals have a fitness value less than or equal to the reset threshold. ")
        continue  

    print(2)
    
    # Generate New Population
    new_population = []
    
    for _ in range(POPULATION_SIZE // 2):  
        parent1, parent2 = tournament_selection(population, fitness_values, k=TOURNAMENT_SIZE)
        child1, child2 = crossover(parent1, parent2)

        child1= mutate(child1, MUTATION_RATE, teachers, classrooms, timeslots)
        child2= mutate(child1, MUTATION_RATE, teachers, classrooms, timeslots)
        new_population.append(repair(child1, teachers, classrooms, timeslots, teacher_max_hours))
        new_population.append(repair(child2, teachers, classrooms, timeslots, teacher_max_hours))
    
    # Update population with new generation
    population = new_population

    # Print Best Solution of the Generation
    best_index = fitness_values.index(max(fitness_values))
    print(f"Best Fitness of Generation {generation}: {fitness_values[best_index]}")
    print(f"Best Solution of Generation {generation}:")


