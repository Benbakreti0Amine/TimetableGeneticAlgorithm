# NUM_SLOTS_PER_DAY = 8  # Number of time slots per day
# NUM_DAYS = 5  # Number of days in the week
# NUM_SUBJECTS = 8  # Number of subjects
# NUM_TEACHERS = 6  # Number of teachers
# NUM_CLASSROOMS = 4  # Number of classrooms
# NUM_STUDENT_GROUPS = 4  # Number of student groups
# TIMETABLE_SIZE = 40  # Total number of time slots (5 days * 8 slots per day)

import random
def generate_gene(year_id, available_teachers, available_courses, available_classrooms, available_timeslots):
    """
    Generate a random gene (course assignment) for a specific year.

    Parameters:
    - year_id: The ID of the study year this gene belongs to.
    - available_teachers: The list of available teachers.
    - available_courses: The list of available courses for this year.
    - available_classrooms: The list of available classrooms.
    - available_timeslots: The list of available timeslots.

    Returns:
    - A dictionary representing the gene.
    """
    course = random.choice(available_courses)  # Randomly choose a course for the year
    teacher = random.choice([t for t in available_teachers if course in t['courses']])  # Select a teacher who can teach the course
    classroom = random.choice(available_classrooms)  # Choose a classroom
    timeslot = random.choice(available_timeslots)  # Choose a timeslot (combining day and slot)

    return {
        'year_id': year_id,
        'course': course,
        'teacher': teacher['id'],
        'classroom': classroom['id'],
        'timeslot': timeslot
    }

def generate_population(population_size, years, teachers, courses, classrooms, timeslots, hours_per_course):
    population = []
    
    for _ in range(population_size):
        individual = []
        for year in years:
            year_timetable = []
            
            for course in courses:
                for _ in range(hours_per_course[course]):
                    gene = generate_gene(
                        year_id=year['id'], 
                        available_teachers=teachers, 
                        available_courses=[course], 
                        available_classrooms=classrooms, 
                        available_timeslots=timeslots
                    )
                    year_timetable.append(gene)
                    
            individual.append(year_timetable)
        population.append(individual)
    
    return population

def display_population(population):
    for idx, individual in enumerate(population):
        print(f"\nIndividual {idx + 1}:")
        for year_timetable in individual:
            for gene in year_timetable:
                print(f"  Year {gene['year_id']} - Course: {gene['course']}, Teacher ID: {gene['teacher']}, "
                      f"Classroom ID: {gene['classroom']}, Timeslot: {gene['timeslot']['day']} Slot {gene['timeslot']['slot']}")

# Test data
teachers = [
    {'id': 1, 'name': 'Dr. Smith', 'courses': ['Math', 'Physics']},
    {'id': 2, 'name': 'Ms. Johnson', 'courses': ['Chemistry']},
    {'id': 3, 'name': 'Mr. Brown', 'courses': ['Math', 'Biology']}
]

classrooms = [
    {'id': 101, 'name': 'Room A', 'capacity': 30},
    {'id': 102, 'name': 'Room B', 'capacity': 25},
    {'id': 103, 'name': 'Lab 1', 'capacity': 20}
]

courses = ['Math', 'Physics', 'Chemistry', 'Biology']

years = [
    {'id': 1, 'name': 'Year 1'},
    {'id': 2, 'name': 'Year 2'}
]

timeslots = [
    {'day': 'Monday', 'slot': 1},
    {'day': 'Monday', 'slot': 2},
    {'day': 'Tuesday', 'slot': 1},
    {'day': 'Tuesday', 'slot': 2}
]

hours_per_course = {'Math': 2, 'Physics': 1, 'Chemistry': 1, 'Biology': 2}

# Generate and display population
population = generate_population(3, years, teachers, courses, classrooms, timeslots, hours_per_course)
display_population(population)
##########################################
########################################
##########################################


# def generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course):
#     """
#     Generate a population of timetables for multiple study years.
    
#     Parameters:
#     - population_size: The number of timetable individuals to generate.
#     - years: List of study years.
#     - year_courses: A dictionary where keys are year IDs and values are the specific courses for that year.
#     - teachers: List of available teachers.
#     - classrooms: List of available classrooms.
#     - timeslots: List of available timeslots.
#     - teacher_max_hours: A dictionary mapping teacher IDs to their maximum allowed teaching hours.
#     - hours_per_course: A dictionary with the number of hours per course.
    
#     Returns:
#     - A list of generated individuals (timetables).
#     """
#     population = []

#     for _ in range(population_size):
#         individual = []
#         teacher_workload = {teacher['id']: 0 for teacher in teachers}  # Track workload for each teacher
        
#         for year in years:
#             year_timetable = []
#             courses_for_year = year_courses[year['id']]  # Get the specific courses for this year

#             for course in courses_for_year:
#                 course_duration_hours = hours_per_course[course['course_name']]  # Get hours for the course
#                 slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES  # Convert to number of 45-minute slots
#                 for _ in range(int(slots_needed)):
#                     # Filter available teachers who have enough remaining teaching hours
#                     available_teachers = [
#                         t for t in teachers 
#                         if course['id'] in t['courses'] and teacher_workload[t['id']] < teacher_max_hours[t['id']]
#                     ]
#                     # if not available_teachers:
#                     #     available_teachers = [ t for t in teachers if course['id'] in t['courses'] ]
                    
#                     if not available_teachers:
#                         raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

#                     gene = generate_gene(
#                         year_id=year['id'], 
#                         available_teachers=available_teachers, 
#                         available_courses=[course], 
#                         available_classrooms=classrooms, 
#                         available_timeslots=timeslots
#                     )

#                     # Update teacher workload
#                     teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60  # Convert to hours
#                     year_timetable.append(gene)

#             individual.append(year_timetable)
#         population.append(individual)

#     return population


# def calculate_fitness(population, hours_per_course, teacher_max_hours):
#     """
#     Calculate the fitness of each individual in the population.
    
#     The fitness is calculated based on the number of constraint violations.
#     Lower fitness values indicate better solutions.

#     Parameters:
#     - population: List of individuals, where each individual is a list of timetables for each year.
#     - hours_per_course: Dictionary of total teaching hours required for each course.
#     - teacher_max_hours: Dictionary of maximum teaching hours for each teacher.

#     Returns:
#     - A list of fitness scores for each individual in the population.
#     """
#     fitness_scores = []

#     for individual in population:
#         # Initialize penalties
#         teacher_conflict_penalty = 0
#         classroom_conflict_penalty = 0
#         course_hours_penalty = 0
#         total_hours_penalty = 0
#         teacher_hours = {teacher['id']: 0 for teacher in teachers}

#         # Track occupied classrooms and teacher schedules
#         occupied_timeslots = {}
#         teacher_schedule = {}
        
#         # Check each year's timetable
#         for year_timetable in individual:
#             # Check for conflicts in this year's timetable
#             year_teacher_schedule = {}
#             year_classroom_schedule = {}
            
#             for gene in year_timetable:
#                 year_id = gene['year_id']
#                 teacher_id = gene['teacher']
#                 classroom_id = gene['classroom']
#                 timeslot = (gene['timeslot']['day'], gene['timeslot']['start_time'], gene['timeslot']['end_time'])
#                 course_name = gene['course']

#  #This line checks if the current (teacher_id, timeslot) combination already exists in the year_teacher_schedule dictionary.
#  #If it does exist, it means that the same teacher is assigned to a class during the same timeslot more than once, which is a conflict.
                   
#                 if (teacher_id, timeslot) in year_teacher_schedule:
#                     teacher_conflict_penalty += 1
#                 year_teacher_schedule[(teacher_id, timeslot)] = True #this tuple already exist

#         #         # Check classroom conflicts within the same year
#         #         if (classroom_id, timeslot) in year_classroom_schedule:
#         #             classroom_conflict_penalty += 1
#         #         year_classroom_schedule[(classroom_id, timeslot)] = True

#         #         # Update global teacher schedule
#         #         if (teacher_id, timeslot) in teacher_schedule:
#         #             teacher_conflict_penalty += 1
#         #         teacher_schedule[(teacher_id, timeslot)] = True

#         #         # Update global classroom schedule
#         #         if (classroom_id, timeslot) in occupied_timeslots:
#         #             classroom_conflict_penalty += 1
#         #         occupied_timeslots[(classroom_id, timeslot)] = True

#         #         # Check teacher's maximum hours
#         #         teacher_hours[teacher_id] += 0.75  # Each class is 45 minutes (0.75 hours)
#         #         if teacher_hours[teacher_id] > teacher_max_hours[teacher_id]:
#         #             total_hours_penalty += 1

#         #         # Track teacher's hours per year
#         #         if (teacher_id, year_id) not in year_teacher_schedule:
#         #             year_teacher_schedule[(teacher_id, year_id)] = 0
#         #         year_teacher_schedule[(teacher_id, year_id)] += 0.75
                
#         #         # Track classroom occupancy per year
#         #         if (classroom_id, year_id) not in year_classroom_schedule:
#         #             year_classroom_schedule[(classroom_id, year_id)] = 0
#         #         year_classroom_schedule[(classroom_id, year_id)] += 0.75

#         #         # Check if course hours are met
#         #         if course_name not in hours_per_course:
#         #             continue
#         #         required_hours = hours_per_course[course_name]
#         #         if required_hours > sum([gene['course'] == course_name for gene in year_timetable]) * 0.75:
#         #             course_hours_penalty += 1

#         # # Penalize for inconsistencies in hours
#         # for teacher_id in teacher_hours:
#         #     if teacher_hours[teacher_id] > teacher_max_hours[teacher_id]:
#         #         total_hours_penalty += 1

#         fitness = (teacher_conflict_penalty + classroom_conflict_penalty + 
#                    course_hours_penalty + total_hours_penalty)
#         fitness_scores.append(fitness)
    
#     return fitness_scores

# def display_fitness(population, fitness_scores):
#     """
#     Display the fitness scores of the population.

#     Parameters:
#     - population: List of individuals.
#     - fitness_scores: List of fitness scores for each individual in the population.
#     """
#     for idx, individual in enumerate(population):
#         print(f"Individual {idx + 1}:")
#         for year_timetable in individual:
#             print("  Year Timetable:")
#             for gene in year_timetable:
#                 print(f"    Course: {gene['course']}, Teacher ID: {gene['teacher']}, Classroom ID: {gene['classroom']}, Time: {gene['timeslot']['start_time']} - {gene['timeslot']['end_time']} - {gene['timeslot']['day']}")
#         print(f"  Fitness Score: {fitness_scores[idx]}")
#         print()

# # # Example Usage
# # population_size = 2
# # population = generate_population(population_size, years, teachers, year_courses, classrooms, timeslots, hours_per_course)
# fitness_scores = calculate_fitness(population, hours_per_course, teacher_max_hours)
# display_fitness(population, fitness_scores)
