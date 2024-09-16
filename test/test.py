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
    timeslot = random.choice(available_timeslots)  # Choose a timeslot

    return {
        'year_id': year_id,
        'course': course['course_name'],
        'teacher': teacher['id'],
        'classroom': classroom['id'],
        'timeslot': timeslot
    }

def generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course):
    """
    Generate a population of timetables for multiple study years.
    """
    population = []

    for _ in range(population_size):
        individual = []
        teacher_workload = {teacher['id']: 0 for teacher in teachers}  # Track workload for each teacher
        year_timeslot_usage = {year['id']: [] for year in years}  # Track timeslot usage for each year
        
        for year in years:
            year_timetable = []
            courses_for_year = year_courses[year['id']]  # Get the specific courses for this year

            for course in courses_for_year:
                course_duration_hours = hours_per_course[course['course_name']]  # Get hours for the course
                slots_needed = course_duration_hours * 60 // COURSE_DURATION_MINUTES  # Convert to number of 45-minute slots

                for _ in range(int(slots_needed)):
                    available_teachers = [
                        t for t in teachers 
                        if course['id'] in t['courses'] and teacher_workload[t['id']] + (COURSE_DURATION_MINUTES / 60) <= teacher_max_hours[t['id']]
                    ]
                    
                    if not available_teachers:
                        raise Exception(f"No available teachers for course {course['course_name']} in year {year['name']}")

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

                    teacher_workload[gene['teacher']] += COURSE_DURATION_MINUTES / 60  # Convert to hours
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
    teacher_timeslots = {}
    classroom_timeslots = {}
    teacher_workload = {teacher['id']: 0 for teacher in teachers}
    year_timeslot_usage = {}

    for year_timetable in individual:
        for gene in year_timetable:
            teacher_id = gene['teacher']
            classroom_id = gene['classroom']
            timeslot = (gene['timeslot']['day'], gene['timeslot']['slot'])
            
            if teacher_id not in teacher_timeslots:
                teacher_timeslots[teacher_id] = []

            if timeslot in teacher_timeslots[teacher_id]:
                fitness -= 10
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60
            else:
                teacher_timeslots[teacher_id].append(timeslot)
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60

            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []

            if timeslot in classroom_timeslots[classroom_id]:
                fitness -= 10
            else:
                classroom_timeslots[classroom_id].append(timeslot)
            
            year_id = gene['year_id']
            if year_id not in year_timeslot_usage:
                year_timeslot_usage[year_id] = []

            if timeslot in year_timeslot_usage[year_id]:
                fitness -= 10
            else:
                year_timeslot_usage[year_id].append(timeslot)

    for teacher_id, workload in teacher_workload.items():
        if workload > teacher_max_hours[teacher_id]:
            fitness -= 11  
    return fitness

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
    Apply mutation to an individual by randomly changing the teacher, classroom, and timeslot of a gene.
    """
    for year_timetable in individual:
        for i in range(len(year_timetable)):
            if random.random() < mutation_rate:
                mutation_choice = random.choice(['teacher', 'classroom', 'timeslot'])

                if mutation_choice == 'teacher':
                    current_course = year_timetable[i]['course']
                    available_teachers = [t for t in teachers if current_course in t['courses']]
                    if available_teachers:
                        new_teacher = random.choice(available_teachers)
                        year_timetable[i]['teacher'] = new_teacher['id']

                elif mutation_choice == 'classroom':
                    new_classroom = random.choice(classrooms)
                    year_timetable[i]['classroom'] = new_classroom['id']

                elif mutation_choice == 'timeslot':
                    new_timeslot = random.choice(timeslots)
                    year_timetable[i]['timeslot'] = new_timeslot

            # Swap mutation
            if random.random() < mutation_rate / 2:
                swap_index = random.randint(0, len(year_timetable) - 1)
                year_timetable[i], year_timetable[swap_index] = year_timetable[swap_index], year_timetable[i]
 
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
                # Fallback: Try to find a teacher who can teach the course or select randomly
                available_teachers = [t for t in teachers if gene['course'] in t['courses']]
                if available_teachers:
                    new_teacher = random.choice(available_teachers)
                else:
                    new_teacher = random.choice(teachers)
                gene['teacher'] = new_teacher['id']
                teacher_workload[new_teacher['id']] += COURSE_DURATION_MINUTES / 60  # Update workload
                # Note: Recalculate workload if necessary
            else:
                teacher_workload[teacher_id] += COURSE_DURATION_MINUTES / 60

            teacher_timeslots[teacher_id].append(timeslot)

            # ---- Repair Classroom Conflicts ----
            if classroom_id not in classroom_timeslots:
                classroom_timeslots[classroom_id] = []
            if timeslot in classroom_timeslots[classroom_id]:
                # Classroom conflict, so repair the gene
                # Fallback: Try to find a different classroom or select randomly
                if classrooms:
                    new_classroom = random.choice(classrooms)
                else:
                    new_classroom = classroom_id  # No change if no alternative available
                gene['classroom'] = new_classroom['id']

            classroom_timeslots[classroom_id].append(timeslot)

    return individual


# Genetic Algorithm Parameters
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
NUM_GENERATIONS = 100000
TOURNAMENT_SIZE = 3

# Example Usage (replace with actual data)


teachers = [
    {'id': 1, 'name': 'Dr. Smith', 'courses': [1, 2], 'state': 'working'},  # Math, Physics
    {'id': 2, 'name': 'Ms. Johnson', 'courses': [3], 'state': 'working'},  # Chemistry
    {'id': 3, 'name': 'Mr. Brown', 'courses': [1, 4], 'state': 'working'},  # Math, Biology
    {'id': 4, 'name': 'Dr. White', 'courses': [5, 6], 'state': 'working'},  # English, History
    {'id': 5, 'name': 'Ms. Davis', 'courses': [7], 'state': 'working'},  # Computer Science
    {'id': 6, 'name': 'Dr. Green', 'courses': [4, 8], 'state': 'working'}  # Biology, Chemistry
]
classrooms = [
    {'id': 101, 'name': 'Room A'},
    {'id': 102, 'name': 'Room B'},
    {'id': 103, 'name': 'Lab 1'},
    {'id': 104, 'name': 'Room C'},
    {'id': 105, 'name': 'Lab 2'}
]
year_courses = {
    1: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 3, 'course_name': 'Chemistry'}, {'id': 5, 'course_name': 'English'}],  # Year 1
    2: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 3, 'course_name': 'Chemistry'}, {'id': 6, 'course_name': 'History'}],  # Year 2
    3: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 7, 'course_name': 'Computer Science'}, {'id': 5, 'course_name': 'English'}],  # Year 3
    4: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 8, 'course_name': 'Advanced Chemistry'}, {'id': 6, 'course_name': 'History'}],  # Year 4
    5: [{'id': 2, 'course_name': 'Physics'}, {'id': 7, 'course_name': 'Computer Science'}, {'id': 8, 'course_name': 'Advanced Chemistry'}, {'id': 6, 'course_name': 'History'}]   # Year 5
}
years = [
    {'id': 1, 'name': 'Year 1'},
    {'id': 2, 'name': 'Year 2'},
    {'id': 3, 'name': 'Year 3'},
    {'id': 4, 'name': 'Year 4'},
    {'id': 5, 'name': 'Year 5'}
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
    
    # Wednesday (slots 23-29)
    {'day': 'Wednesday', 'slot': 23, 'start_time': '08:00', 'end_time': '08:45'},
    {'day': 'Wednesday', 'slot': 24, 'start_time': '08:45', 'end_time': '09:30'},
    {'day': 'Wednesday', 'slot': 25, 'start_time': '09:30', 'end_time': '10:15'},
    {'day': 'Wednesday', 'slot': 26, 'start_time': '10:30', 'end_time': '11:15'},
    {'day': 'Wednesday', 'slot': 27, 'start_time': '11:15', 'end_time': '12:00'},
    {'day': 'Wednesday', 'slot': 28, 'start_time': '14:00', 'end_time': '14:45'},
    {'day': 'Wednesday', 'slot': 29, 'start_time': '14:45', 'end_time': '15:30'},
    ]

teacher_max_hours = {
    1: 35,  # Dr. Smith
    2: 40,  # Ms. Johnson
    3: 20,  # Mr. Brown
    4: 22,  # Dr. White
    5: 25,  # Ms. Davis
    6: 25   # Dr. Green
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

# Initialize Population
population = generate_population(POPULATION_SIZE, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)

# Run Genetic Algorithm
# Run Genetic Algorithm

import random

# Define thresholds

# Define thresholds
RESET_THRESHOLD = -300
STOP_THRESHOLD = -40
# Initialize Population
population = generate_population(20, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)

# Run Genetic Algorithm
for generation in range(NUM_GENERATIONS):
    # Evaluate Fitness
    fitness_values = [fitness_function(individual, teacher_max_hours) for individual in population]
    
    # Print Fitness for Each Individual
    print(f"Generation {generation}:")
    for i, fitness in enumerate(fitness_values):
        print(f"  Individual {i + 1}: Fitness = {fitness}")
    
    # Check if we need to stop or reset
    if max(fitness_values) >= STOP_THRESHOLD:
        print("Stopping early due to fitness threshold.")
        best_index = fitness_values.index(max(fitness_values))
        print(f"Best Fitness of Generation {generation}: {fitness_values[best_index]}")
        print(f"Best Solution of Generation {generation}:")
        display_population([population[best_index]])
        break
    
    if min(fitness_values) <= RESET_THRESHOLD:
        print("Resetting population due to fitness threshold.")
        # Reinitialize the population
        population = generate_population(20, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
        # Proceed to the next generation
        continue  # This will skip the rest of the loop and start the next generation with the new population

    # Generate New Population
    new_population = []
    
    for _ in range(POPULATION_SIZE // 2):  
        parent1, parent2 = tournament_selection(population, fitness_values, k=TOURNAMENT_SIZE)
        child1, child2 = crossover(parent1, parent2)
        new_population.append(repair(mutate(child1, MUTATION_RATE, teachers, classrooms, timeslots), teachers, classrooms, timeslots, teacher_max_hours))
        new_population.append(repair(mutate(child2, MUTATION_RATE, teachers, classrooms, timeslots), teachers, classrooms, timeslots, teacher_max_hours))
    
    # Update population with new generation
    population = new_population

    # # Evaluate fitness of new population
    # fitness_values = [fitness_function(individual, teacher_max_hours) for individual in population]

    # Print Best Solution of the Generation
    best_index = fitness_values.index(max(fitness_values))
    print(f"Best Fitness of Generation {generation}: {fitness_values[best_index]}")
    print(f"Best Solution of Generation {generation}:")
    # display_population([population[best_index]])



# for generation in range(NUM_GENERATIONS):
#     # Evaluate Fitness
#     fitness_values = [fitness_function(individual, teacher_max_hours) for individual in population]
    
#     # Print Fitness for Each Individual
#     print(f"Generation {generation}:")
#     for i, fitness in enumerate(fitness_values):
#         print(f"  Individual {i + 1}: Fitness = {fitness}")
    
#     # Generate New Population
#     new_population = []
#     # new_population = list(population)
    
#     for _ in range(POPULATION_SIZE // 2):  
#         parent1, parent2 = tournament_selection(population, fitness_values, k=TOURNAMENT_SIZE)
#         child1, child2 = crossover(parent1, parent2)
#         new_population.append(repair(mutate(child1, MUTATION_RATE, teachers, classrooms, timeslots), teachers, classrooms, timeslots, teacher_max_hours))
#         new_population.append(repair(mutate(child2, MUTATION_RATE, teachers, classrooms, timeslots), teachers, classrooms, timeslots, teacher_max_hours))
#     # fitness_values = [fitness_function(individual, teacher_max_hours) for individual in new_population]
#     # for i, fitness in enumerate(fitness_values):
#     #     print(f"  Individual of new population {i + 1}: Fitness = {fitness}")
#     population = new_population

#     # Print Best Solution of the Generation
#     best_index = fitness_values.index(max(fitness_values))
#     print(f"Best Fitness of Generation {generation}: {fitness_values[best_index]}")
#     print(f"Best Solution of Generation {generation}:")
#     display_population([population[best_index]])
