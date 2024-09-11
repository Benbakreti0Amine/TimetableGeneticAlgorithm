import random

# Constants
COURSE_DURATION_MINUTES = 45
#each year have specific courses, capacity for a class not classroom like 1st year students cant be more than 40
def generate_gene(year_id, available_teachers, available_courses, available_classrooms, available_timeslots):
    """
    Generate a random gene (course assignment) for a specific year.

    Parameters:
    - year_id: The ID of the study year this gene belongs to.
    - available_teachers: The list of available teachers (filtered based on courses and year of study).
    - available_courses: The list of available courses for this year.
    - available_classrooms: The list of available classrooms.
    - available_timeslots: The list of available timeslots.

    Returns:
    - A dictionary representing the gene.
    """
    course = random.choice(available_courses)  # Randomly choose a course for the year
    teacher = random.choice([t for t in available_teachers if course['id'] in t['courses']])  # Select a teacher who can teach the course
    classroom = random.choice(available_classrooms)  # Choose a classroom
    timeslot = random.choice(available_timeslots)  # Choose a timeslot (combining day and slot)

    return {
        'year_id': year_id,
        'course': course['course_name'],
        'teacher': teacher['id'],
        'classroom': classroom['id'],
        'timeslot': timeslot
    }
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
#         teacher_workload = {teacher['id']: -1 for teacher in teachers}  # Track workload for each teacher
        
#         for year in years:
#             year_timetable = []
#             courses_for_year = year_courses[year['id']]  # Get the specific courses for this year

#             for course in courses_for_year:
#                 course_duration_hours = hours_per_course[course['course_name']]  # Get hours for the course
#                 slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES  # Convert to number of 45-minute slots
#                 for _ in range(int(slots_needed)):
#                     # Filter available teachers who have enough remaining teaching hours across all years
#                     available_teachers = [
#                         t for t in teachers 
#                         if course['id'] in t['courses'] and teacher_workload[t['id']] + (COURSE_DURATION_MINUTES / 60) <= teacher_max_hours[t['id']]
#                     ]
                    
#                     if not available_teachers:
#                         raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

#                     gene = generate_gene(
#                         year_id=year['id'], 
#                         available_teachers=available_teachers, 
#                         available_courses=[course], 
#                         available_classrooms=classrooms, 
#                         available_timeslots=timeslots
#                     )

#                     # Update teacher workload cumulatively across both years
#                     teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60  # Convert to hours
#                     year_timetable.append(gene)

#             individual.append(year_timetable)
#         population.append(individual)

#     return population
def generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course):
    """
    Generate a population of timetables for multiple study years.
    
    Parameters:
    - population_size: The number of timetable individuals to generate.
    - years: List of study years.
    - year_courses: A dictionary where keys are year IDs and values are the specific courses for that year.
    - teachers: List of available teachers.
    - classrooms: List of available classrooms.
    - timeslots: List of available timeslots.
    - teacher_max_hours: A dictionary mapping teacher IDs to their maximum allowed teaching hours.
    - hours_per_course: A dictionary with the number of hours per course.
    
    Returns:
    - A list of generated individuals (timetables).
    """
    population = []

    for _ in range(population_size):
        individual = []
        teacher_workload = {teacher['id']: 0 for teacher in teachers}  # Track workload for each teacher
        
        for year in years:
            year_timetable = []
            used_timeslots = set()  # Track used timeslots for the current year

            courses_for_year = year_courses[year['id']]  # Get the specific courses for this year

            for course in courses_for_year:
                course_duration_hours = hours_per_course[course['course_name']]  # Get hours for the course
                slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES  # Convert to number of 45-minute slots
                for _ in range(int(slots_needed)):
                    # Filter available teachers who have enough remaining teaching hours
                    available_teachers = [
                        t for t in teachers 
                        if course['id'] in t['courses'] and teacher_workload[t['id']] < teacher_max_hours[t['id']]
                    ]
                    
                    if not available_teachers:
                        raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

                    # Filter out the timeslots already used by this year
                    available_timeslots = [ts for ts in timeslots if (ts['day'], ts['slot']) not in used_timeslots]

                    if not available_timeslots:
                        raise Exception(f"No available timeslots for year {year['name']}")

                    gene = generate_gene(
                        year_id=year['id'], 
                        available_teachers=available_teachers, 
                        available_courses=[course], 
                        available_classrooms=classrooms, 
                        available_timeslots=available_timeslots
                    )

                    # Update teacher workload
                    teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60  # Convert to hours

                    # Mark the timeslot as used for this year
                    used_timeslots.add((gene['timeslot']['day'], gene['timeslot']['slot']))

                    year_timetable.append(gene)

            individual.append(year_timetable)
        population.append(individual)

    return population

def display_population(population):
    """
    Display the generated population in a readable format.
    """
    for idx, individual in enumerate(population):
        print(f"\nIndividual {idx + 1}:")
        for year_timetable in individual:
            for gene in year_timetable:
                print(f"  Year {gene['year_id']} - Course: {gene['course']}, Teacher ID: {gene['teacher']}, "
                      f"Classroom ID: {gene['classroom']}, Timeslot: {gene['timeslot']['day']}  {gene['timeslot']['start_time']} - {gene['timeslot']['end_time']} Slot {gene['timeslot']['slot']}")

# Test data setup
teachers = [
    {'id': 1, 'name': 'Dr. Smith', 'courses': [1, 2], 'state': 'working'},  # Teaches Math, Physics
    {'id': 2, 'name': 'Ms. Johnson', 'courses': [3], 'state': 'working'},  # Teaches Chemistry
    {'id': 3, 'name': 'Mr. Brown', 'courses': [1, 4], 'state': 'working'}  # Teaches Math, Biology
]

classrooms = [
    {'id': 101, 'name': 'Room A'},
    {'id': 102, 'name': 'Room B'},
    {'id': 103, 'name': 'Lab 1'}
]

# Courses available for each year
year_courses = {
    1: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 3, 'course_name': 'Chemistry'}],  # Year 1 courses
    2: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 3, 'course_name': 'Chemistry'}]  # Year 2 courses
}

years = [
    {'id': 1, 'name': 'Year 1'},
    {'id': 2, 'name': 'Year 2'}
]

# Timeslots updated with the 45-minute intervals
timeslots = [
    {'day': 'Sunday', 'slot': 1, 'start_time': '08:30', 'end_time': '09:15'},
    {'day': 'Sunday', 'slot': 2, 'start_time': '09:15', 'end_time': '10:00'},
    {'day': 'Sunday', 'slot': 3, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Sunday', 'slot': 4, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Sunday', 'slot': 5, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Sunday', 'slot': 6, 'start_time': '14:45', 'end_time': '15:30'},
    {'day': 'Sunday', 'slot': 7, 'start_time': '15:30', 'end_time': '16:15'},
    {'day': 'Monday', 'slot': 8, 'start_time': '08:30', 'end_time': '09:15'},
    {'day': 'Monday', 'slot': 9, 'start_time': '09:15', 'end_time': '10:00'},
    {'day': 'Monday', 'slot': 10, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Monday', 'slot': 11, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Monday', 'slot': 12, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Monday', 'slot': 13, 'start_time': '14:45', 'end_time': '15:30'},
    {'day': 'Monday', 'slot': 14, 'start_time': '15:30', 'end_time': '16:15'},
]

# Number of hours per course
hours_per_course = {'Math': 3, 'Physics': 1.5, 'Chemistry': 1.5, 'Biology': 1.5}

# Maximum teaching hours for each teacher
teacher_max_hours = {1: 6, 2: 6, 3: 6}  # Teacher 1 can teach up to 6 hours, etc.

# Generate and display population
population = generate_population(13, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
display_population(population)


######################################
######################################
######################################

def fitness_function(individual):
    fitness = 0
    teacher_timeslots = {}  # Dictionary to track which timeslots a teacher has been assigned
    classroom_timeslots = {}  # Track which timeslots a classroom has been occupied
    # Iterate over the entire timetable (across all years)
    for year_timetable in individual:
        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            timeslot = (gene['timeslot']['day'], gene['timeslot']['slot'])  # Combine day and slot as a tuple

            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []

            # Check if the teacher is already assigned to this timeslot in any year
            if timeslot in teacher_timeslots[teacher_id]:
                fitness -= 10  # Penalize for a conflict (teacher teaching more than one course at the same time)
            else:
                teacher_timeslots[teacher_id].append(timeslot)
                # fitness += 1  # Reward for a valid assignment

            # ---- Check Classroom Conflicts ----
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []

            if timeslot in classroom_timeslots[classroom_id]:
                fitness -= 10  # Penalize for a conflict (classroom occupied by more than one group at the same time)
            else:
                classroom_timeslots[classroom_id].append(timeslot)
                # fitness += 1  # Reward for a valid classroom assignment

    return fitness

for idx, individual in enumerate(population):
    fitness = fitness_function(individual)
    print(f"Fitness of individual {idx + 1}: {fitness}")