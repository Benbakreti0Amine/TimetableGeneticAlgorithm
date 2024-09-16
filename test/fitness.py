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

def generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course):
    """
    Generate a population of timetables for multiple study years while ensuring no time conflicts for each year.

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
        teacher_workload = {teacher['id']: -1 for teacher in teachers}  # Track workload for each teacher
        year_timeslot_usage = {year['id']: [] for year in years}  # Track timeslot usage for each year
        
        for year in years:
            year_timetable = []
            courses_for_year = year_courses[year['id']]  # Get the specific courses for this year

            for course in courses_for_year:
                course_duration_hours = hours_per_course[course['course_name']]  # Get hours for the course
                slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES  # Convert to number of 45-minute slots

                for _ in range(int(slots_needed)):
                    # Filter available teachers who have enough remaining teaching hours across all years
                    available_teachers = [
                        t for t in teachers 
                        if course['id'] in t['courses'] and teacher_workload[t['id']] + (COURSE_DURATION_MINUTES / 60) <= teacher_max_hours[t['id']]
                    ]
                    
                    if not available_teachers:
                        raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

                    # Ensure no timeslot conflict for the same year
                    available_timeslots = [
                        ts for ts in timeslots 
                        if (ts['day'], ts['slot']) not in year_timeslot_usage[year['id']]
                    ]
                    
                    if not available_timeslots:
                        raise Exception(f"No available timeslots for year {year['name']} to schedule {course['course_name']}")

                    gene = generate_gene(
                        year_id=year['id'], 
                        available_teachers=available_teachers, 
                        available_courses=[course], 
                        available_classrooms=classrooms, 
                        available_timeslots=available_timeslots
                    )

                    # Update teacher workload cumulatively across both years
                    teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60  # Convert to hours
                    
                    # Mark the timeslot as used for this year
                    year_timeslot_usage[year['id']].append((gene['timeslot']['day'], gene['timeslot']['slot']))
                    
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
                print(f"  {gene['year_id']}- Course: {gene['course']},TeachID: {gene['teacher']}, "
                      f"ClassID: {gene['classroom']}, Tslot: {gene['timeslot']['day']}  {gene['timeslot']['start_time']} - {gene['timeslot']['end_time']} Slot {gene['timeslot']['slot']}")



######################################
######################################
######################################

def fitness_function(individual, teacher_max_hours):
    fitness = 0
    teacher_timeslots = {}  # Dictionary to track which timeslots a teacher has been assigned
    classroom_timeslots = {}  # Track which timeslots a classroom has been occupied
    teacher_workload = {teacher['id']: 0 for teacher in teachers}  # Initialize workload dictionary
    year_timeslot_usage = {}  # Track timeslot usage for each year

    # Initialize dictionaries
    for year_timetable in individual:
        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            timeslot = (gene['timeslot']['day'], gene['timeslot']['slot'])  # Combine day and slot as a tuple
            
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []

            # Check if the teacher is already assigned to this timeslot in any year
            if timeslot in teacher_timeslots[teacher_id]:
                # Penalize for a conflict (teacher teaching more than one course at the same time)
                fitness -= 10
                # Add course duration to the workload
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60
            else:
                teacher_timeslots[teacher_id].append(timeslot)
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60  # Update workload

            # ---- Check Classroom Conflicts ----
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []

            if timeslot in classroom_timeslots[classroom_id]:
                fitness -= 10  # Penalize for a conflict (classroom occupied by more than one group at the same time)
            else:
                classroom_timeslots[classroom_id].append(timeslot)
            
            # ---- Check Time Slot Conflicts in Each Year ----
            year_id = gene['year_id']
            if year_id not in year_timeslot_usage:
                year_timeslot_usage[year_id] = []

            if timeslot in year_timeslot_usage[year_id]:
                fitness -= 10  # Penalize for repeating timeslot in the same year
            else:
                year_timeslot_usage[year_id].append(timeslot)

    # ---- Check Teacher Workload ----
    for teacher_id, workload in teacher_workload.items():
        if workload > teacher_max_hours[teacher_id]:
            fitness -= 10  
    return fitness




def crossover(parent1, parent2):
    """
    Perform random crossover between two parents to create two new individuals.

    Parameters:
    - parent1: The first parent individual.
    - parent2: The second parent individual.

    Returns:
    - Two new individuals created from the crossover of parent1 and parent2.
    """
    assert len(parent1) == len(parent2) , "The number of years must be fixed at 5."

    # Create children with more random crossover
    child1, child2 = [], []

    # Randomly choose genes from each parent for each year
    for i in range(len(parent1)):
        if i % 2 == 0:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])

    return child1, child2



######################################

# def mutatee(individual, mutation_rate, classrooms):
#     """
#     Apply mutation to an individual by randomly changing the timeslot of a gene with a given mutation rate.

#     Parameters:
#     - individual: The individual (timetable) to mutate.
#     - mutation_rate: The probability of mutating a gene's timeslot (e.g., 0.1 for 10% chance).
#     - available_timeslots: List of available timeslots.

#     Returns:
#     - Mutated individual with possibly changed timeslots.
#     """
#     for year_timetable in individual:
#         for i in range(len(year_timetable)):
#             if random.random() < mutation_rate:
#                 new_classroom = random.choice(classrooms)
#                 new_classroom_id = new_classroom['id']
#                 # print(year_timetable[i], new_classroom_id)
#                 year_timetable[i]['classroom'] = new_classroom_id              
#     return individual

def mutatee(individual, mutation_rate, teachers, classrooms, timeslots):
    """
    Apply mutation to an individual by randomly changing the teacher, classroom, and timeslot of a gene
    with a given mutation rate to increase diversity.

    Parameters:
    - individual: The individual (timetable) to mutate.
    - mutation_rate: The probability of mutating a gene (e.g., 0.1 for 10% chance).
    - teachers: List of available teachers.
    - classrooms: List of available classrooms.
    - timeslots: List of available timeslots.

    Returns:
    - Mutated individual with possibly changed teachers, classrooms, and timeslots.
    """
    for year_timetable in individual:
        for i in range(len(year_timetable)):
            if random.random() < mutation_rate:
                # Randomly decide what to mutate (teacher, classroom, or timeslot)
                mutation_choice = random.choice(['teacher', 'classroom', 'timeslot'])

                # ---- Mutate Teacher ----
                if mutation_choice == 'teacher':
                    current_course = year_timetable[i]['course']
                    available_teachers = [t for t in teachers if current_course in t['courses']]
                    if available_teachers:
                        new_teacher = random.choice(available_teachers)
                        year_timetable[i]['teacher'] = new_teacher['id']

                # ---- Mutate Classroom ----
                elif mutation_choice == 'classroom':
                    new_classroom = random.choice(classrooms)
                    year_timetable[i]['classroom'] = new_classroom['id']

                # ---- Mutate Timeslot ----
                elif mutation_choice == 'timeslot':
                    new_timeslot = random.choice(timeslots)
                    year_timetable[i]['timeslot'] = new_timeslot

            # Add additional diversity: swap mutations
            if random.random() < mutation_rate / 2:  # Lower chance for swap mutation
                swap_index = random.randint(0, len(year_timetable) - 1)
                year_timetable[i], year_timetable[swap_index] = year_timetable[swap_index], year_timetable[i]

    return individual

######################################
######################################
def tournament_selection(population, fitness_values, k=3):
    """
    Selects two individuals from the population using tournament selection.
    
    Parameters:
    - population: List of individuals in the current generation.
    - fitness_values: List of fitness values corresponding to the population.
    - k: Tournament size (how many individuals to compete in each tournament).

    Returns:
    - Two selected individuals (parents) based on their fitness.
    """
    # Randomly select 'k' individuals for the tournament
    tournament_indices = random.sample(range(len(population)), k)
    tournament_individuals = [population[i] for i in tournament_indices]
    tournament_fitness = [fitness_values[i] for i in tournament_indices]

    # Sort the individuals by fitness (best individuals first)
    sorted_indices = sorted(range(len(tournament_fitness)), key=lambda i: tournament_fitness[i], reverse=True)

    # Return the top two individuals for crossover
    parent1 = tournament_individuals[sorted_indices[0]]
    parent2 = tournament_individuals[sorted_indices[1]]

    return parent1, parent2


############################################
def repair(individual, teachers, classrooms, timeslots, teacher_max_hours):
    """
    Repairs an individual (chromosome) by resolving hard constraint violations.
    
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
        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            timeslot = (gene['timeslot']['day'], gene['timeslot']['slot'])  # Combine day and slot

            # ---- Repair Teacher Conflicts ----
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []
            if timeslot in teacher_timeslots[teacher_id] or teacher_workload[teacher_id] >= teacher_max_hours[teacher_id]:
                # Teacher conflict or exceeding max hours, so repair the gene
                new_teacher = random.choice([t for t in teachers if gene['course'] in t['courses']])
                gene['teacher'] = new_teacher['id']
                teacher_workload[new_teacher['id']] += COURSE_DURATION_MINUTES / 60  # Update workload

            teacher_timeslots[teacher_id].append(timeslot)

            # ---- Repair Classroom Conflicts ----
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []
            if timeslot in classroom_timeslots[classroom_id]:
                # Classroom conflict, so repair the gene
                new_classroom = random.choice(classrooms)
                gene['classroom'] = new_classroom['id']

            classroom_timeslots[classroom_id].append(timeslot)

    return individual

############################################
def elitism(population, fitness_values, elitism_size):
    """
    Selects the top `elitism_size` individuals from the current population based on fitness.
    
    Parameters:
    - population: The current population of individuals.
    - fitness_values: The corresponding fitness values of the population.
    - elitism_size: The number of individuals to preserve for the next generation.

    Returns:
    - A list of the top `elitism_size` individuals.
    """
    # Sort population by fitness (higher fitness is better)
    sorted_indices = sorted(range(len(fitness_values)), key=lambda i: fitness_values[i], reverse=True)

    # Select the top `elitism_size` individuals
    elite_individuals = [population[i] for i in sorted_indices[:elitism_size]]

    return elite_individuals

############################################
############################################




teachers = [
    {'id': 1, 'name': 'Dr. Smith', 'courses': [1, 2], 'state': 'working'},  # Math, Physics
    {'id': 2, 'name': 'Ms. Johnson', 'courses': [3], 'state': 'working'},  # Chemistry
    {'id': 3, 'name': 'Mr. Brown', 'courses': [1, 4], 'state': 'working'},  # Math, Biology
    {'id': 4, 'name': 'Dr. White', 'courses': [5, 6], 'state': 'working'},  # English, History
    {'id': 5, 'name': 'Ms. Davis', 'courses': [7], 'state': 'working'},  # Computer Science
    # {'id': 6, 'name': 'Dr. Green', 'courses': [4, 8], 'state': 'working'}  # Biology, Chemistry
]
classrooms = [
    {'id': 101, 'name': 'Room A'},
    {'id': 102, 'name': 'Room B'},
    {'id': 103, 'name': 'Lab 1'},
    # {'id': 104, 'name': 'Room C'},
    # {'id': 105, 'name': 'Lab 2'}
]
year_courses = {
    1: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 3, 'course_name': 'Chemistry'}, {'id': 5, 'course_name': 'English'}],  # Year 1
    2: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 3, 'course_name': 'Chemistry'}, {'id': 6, 'course_name': 'History'}],  # Year 2
    3: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 7, 'course_name': 'Computer Science'}, {'id': 5, 'course_name': 'English'}],  # Year 3
    # 4: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 8, 'course_name': 'Advanced Chemistry'}, {'id': 6, 'course_name': 'History'}],  # Year 4
    # 5: [{'id': 2, 'course_name': 'Physics'}, {'id': 7, 'course_name': 'Computer Science'}, {'id': 8, 'course_name': 'Advanced Chemistry'}, {'id': 6, 'course_name': 'History'}]   # Year 5
}
years = [
    {'id': 1, 'name': 'Year 1'},
    {'id': 2, 'name': 'Year 2'},
    {'id': 3, 'name': 'Year 3'},
    # {'id': 4, 'name': 'Year 4'},
    # {'id': 5, 'name': 'Year 5'}
]
timeslots = [
    # Sunday (slots 1-7)
    {'day': 'Sunday', 'slot': 1, 'start_time': '08:30', 'end_time': '09:15'},
    {'day': 'Sunday', 'slot': 2, 'start_time': '09:15', 'end_time': '10:00'},
    {'day': 'Sunday', 'slot': 3, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Sunday', 'slot': 4, 'start_time': '11:15', 'end_time': '12:00'},
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
    
    # # Wednesday (slots 23-29)
    # {'day': 'Wednesday', 'slot': 23, 'start_time': '08:00', 'end_time': '08:45'},
    # {'day': 'Wednesday', 'slot': 24, 'start_time': '08:45', 'end_time': '09:30'},
    # {'day': 'Wednesday', 'slot': 25, 'start_time': '09:30', 'end_time': '10:15'},
    # {'day': 'Wednesday', 'slot': 26, 'start_time': '10:30', 'end_time': '11:15'},
    # {'day': 'Wednesday', 'slot': 27, 'start_time': '11:15', 'end_time': '12:00'},
    # {'day': 'Wednesday', 'slot': 28, 'start_time': '14:00', 'end_time': '14:45'},
    # {'day': 'Wednesday', 'slot': 29, 'start_time': '14:45', 'end_time': '15:30'},
    ]

teacher_max_hours = {
    1: 20,  # Dr. Smith
    2: 15,  # Ms. Johnson
    3: 18,  # Mr. Brown
    4: 22,  # Dr. White
    5: 17,  # Ms. Davis
    6: 19   # Dr. Green
}
hours_per_course = {
    'Math': 4,  # A more intensive subject
    'Physics': 3,  # Requires in-depth coverage
    'Chemistry': 3.5,  # Lab and theory hours
    'Biology': 3,  # Includes practicals
    'English': 2.5,  # Language arts
    'History': 3,  # In-depth historical studies
    'Computer Science': 4,  # Practical and theoretical components
    'Advanced Chemistry': 4  # Higher-level content
}


def display_best_result(best_individual, fitness):
    """
    Display the best result found by the genetic algorithm.
    """
    print("\nBest Individual Found:")
    display_population([best_individual])
    print(f"Fitness: {fitness}")


population = generate_population(2, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)

if len(population) > 1:
    parent1 = population[0]
    parent2 = population[1]

    # Perform crossover
    child1, child2 = crossover(parent1, parent2)
    mutation_rate = 0.2  # 10% chance of mutation for each timeslot


    # Display parents and offspring
    print("\n--- Parent 1 ---")
    display_population([parent1])
    fitness_parent1 = fitness_function(parent1, teacher_max_hours)
    

    print("\n--- Parent 2 ---")
    display_population([parent2])
    fitness_parent2 = fitness_function(parent2, teacher_max_hours)

    # print("\n--- Child 1 ---")
    # display_population([child1])

    # print("\n--- Child 2 ---")
    # display_population([child2])

    # Calculate fitness for children
    print(f"\nFitness of Parent 1: {fitness_parent1}")
    print(f"\nFitness of Parent 2: {fitness_parent2}")

    fitness_child1 = fitness_function(child1, teacher_max_hours)
    fitness_child2 = fitness_function(child2, teacher_max_hours)

    print(f"\nFitness of Child 1: {fitness_child1}")
    print(f"Fitness of Child 2: {fitness_child2}")

    child3 = mutatee(child1, mutation_rate, teachers,classrooms, timeslots)
    child4 = mutatee(child2, mutation_rate, teachers,classrooms, timeslots)
   
    fitness_child3 = fitness_function(child3, teacher_max_hours)        
    fitness_child4 = fitness_function(child4, teacher_max_hours)

    print(f"\nFitness of Child 3: {fitness_child3}")
    print(f"Fitness of Child 4: {fitness_child4}")


else:
    print("Not enough individuals in the population to perform crossover.")

