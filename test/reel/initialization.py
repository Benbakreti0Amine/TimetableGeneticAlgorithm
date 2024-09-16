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
                print(f" Year {gene['year_id']}- Course: {gene['course']},TeacherID: {gene['teacher']}, "
                      f"ClassID: {gene['classroom']}, Timeslot: {gene['timeslot']['day']}  {gene['timeslot']['start_time']} - {gene['timeslot']['end_time']} Slot {gene['timeslot']['slot']}")



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
            fitness -= 20  
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
        if random.random() < 0.5:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])

    return child1, child2

######################################
######################################
######################################

def mutate(individual, mutation_rate=0.2):
    """
    Perform mutation on an individual by randomly changing a course, teacher, or timeslot with a probability.

    Parameters:
    - individual: The individual timetable to mutate.
    - mutation_rate: Probability of mutating a gene.

    Returns:
    - A potentially mutated individual.
    """
    for year_timetable in individual:
        for gene in year_timetable:
            if random.random() < mutation_rate:
                # print(f"Mutating gene ")
                # print(random.choice(classrooms))
                # gene['teacher'] = random.choice([t['id'] for t in teachers if gene['course'] in [course['course_name'] for course in year_courses[gene['year_id']]]])
                # gene['timeslot'] = random.choice(timeslots)
                gene['classroom'] = random.choice(classrooms)['id']
    return individual

TARGET_FITNESS = -50
MAX_GENERATIONS = 5000
# def genetic_algorithm(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course, max_generations=MAX_GENERATIONS, target_fitness=TARGET_FITNESS):
#     """
#     Execute the genetic algorithm to find an optimal timetable.
#     This version stores the best individual from all generations.
    
#     Parameters:
#     - population_size: Number of individuals in the population.
#     - years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course: As defined in your setup.
#     - max_generations: Maximum number of generations to run the algorithm.
#     - target_fitness: Desired fitness level to achieve (0 for perfect solution).
    
#     Returns:
#     - Best individual found and its fitness.
#     """
#     # Generate initial population
#     population = generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
    
#     best_individual = None
#     best_fitness = float('-inf')  # Start with the lowest possible fitness
    
#     for generation in range(max_generations):
#         # Calculate fitness for each individual
#         fitness_scores = [fitness_function(individual, teacher_max_hours) for individual in population]
        
#         # Display current generation results
#         print(f"Generation {generation + 1}")
#         for idx, fitness in enumerate(fitness_scores):
#             print(f"  Fitness of individual {idx + 1}: {fitness}")
        
#         # Check if we have a new best individual
#         current_best_fitness = max(fitness_scores)
#         current_best_individual = population[fitness_scores.index(current_best_fitness)]
        
#         # Update the best individual if the current one is better
#         if current_best_fitness > best_fitness:
#             best_fitness = current_best_fitness
#             best_individual = current_best_individual
#             print(f"New best individual found with fitness {best_fitness}")
        
#         # Check if we have found a solution with target fitness
#         if best_fitness >= target_fitness:
#             print("Found optimal solution!")
#             return best_individual, best_fitness
        
#         # Pair fitness scores with individuals
#         paired_population = list(zip(fitness_scores, population))

#         # Sort based on fitness scores (highest fitness is better)
#         sorted_population = sorted(paired_population, key=lambda x: x[0], reverse=True)
        
#         # Select the top half of the population based on fitness
#         top_half = [indiv for _, indiv in sorted_population[:len(sorted_population) // 2]]
        
#         # Generate new population through crossover
#         new_population = []
#         while len(new_population) < population_size:
#             parent1, parent2 = random.sample(top_half, 2)
#             child1, child2 = crossover(parent1, parent2)
#             # child1 = mutate(child1)
#             # child2 = mutate(child2)
#             new_population.extend([child1, child2])
        
#         # Ensure the new population size matches the required population size
#         population = new_population[:population_size]

#     print("Reached maximum generations.")
#     return best_individual, best_fitness
import numpy as np

def roulette_wheel_selection(population, fitness_scores):
    """
    Perform roulette wheel selection based on fitness scores.
    The better fitness values (less negative) get higher probability.

    Parameters:
    - population: List of individuals.
    - fitness_scores: Corresponding fitness scores for the population (negative values).
    
    Returns:
    - Selected individual from the population.
    """
    # Convert negative fitness scores to positive for selection probability
    positive_fitness = [-fitness for fitness in fitness_scores]  # Convert to positive values
    
    # Total weight for normalization
    total_weight = sum(positive_fitness)
    
    # Calculate selection probabilities
    selection_probs = [weight / total_weight for weight in positive_fitness]
    
    # Select an individual based on the probabilities
    selected_index = random.choices(range(len(population)), weights=selection_probs, k=1)[0]
    
    return population[selected_index]

def genetic_algorithm(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course, max_generations=MAX_GENERATIONS, target_fitness=TARGET_FITNESS):
    """
    Execute the genetic algorithm to find an optimal timetable using roulette wheel selection.

    Parameters:
    - population_size: Number of individuals in the population.
    - years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course: As defined in your setup.
    - max_generations: Maximum number of generations to run the algorithm.
    - target_fitness: Desired fitness level to achieve (0 for perfect solution).

    Returns:
    - Best individual found and its fitness.
    """
    # Generate initial population
    population = generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
    
    best_individual = None
    best_fitness = float('-inf')  # Start with the lowest possible fitness
    
    for generation in range(max_generations):
        # Calculate fitness for each individual
        fitness_scores = [fitness_function(individual, teacher_max_hours) for individual in population]
        
        # Display current generation results
        print(f"Generation {generation + 1}")
        for idx, fitness in enumerate(fitness_scores):
            print(f"  Fitness of individual {idx + 1}: {fitness}")
        
        # Check if we have a new best individual
        current_best_fitness = max(fitness_scores)
        current_best_individual = population[fitness_scores.index(current_best_fitness)]
        
        # Update the best individual if the current one is better
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual
            print(f"New best individual found with fitness {best_fitness}")
        
        # Check if we have found a solution with target fitness
        if best_fitness >= target_fitness:
            print("Found optimal solution!")
            return best_individual, best_fitness
        
        # Generate new population through crossover and mutation
        new_population = list(population)
        while len(new_population) < population_size:
            # Select two parents using roulette wheel selection
            parent1 = roulette_wheel_selection(population, fitness_scores)
            parent2 = roulette_wheel_selection(population, fitness_scores)
            
            # Perform crossover and mutation
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            
            new_population.extend([child1, child2])
        
        # Ensure the new population size matches the required population size

    print("Reached maximum generations.")
    return best_individual, best_fitness



######################################
######################################
######################################


# # Test data setup
# teachers = [
#     {'id': 1, 'name': 'Dr. Smith', 'courses': [1, 2], 'state': 'working'},  # Teaches Math, Physics
#     {'id': 2, 'name': 'Ms. Johnson', 'courses': [3], 'state': 'working'},  # Teaches Chemistry
#     {'id': 3, 'name': 'Mr. Brown', 'courses': [1, 4], 'state': 'working'}  # Teaches Math, Biology
# ]

# classrooms = [
#     {'id': 101, 'name': 'Room A'},
#     {'id': 102, 'name': 'Room B'},
#     {'id': 103, 'name': 'Lab 1'}
# ]

# # Courses available for each year
# year_courses = {
#     1: [{'id': 1, 'course_name': 'Math'}, {'id': 2, 'course_name': 'Physics'}, {'id': 3, 'course_name': 'Chemistry'}],  # Year 1 courses
#     2: [{'id': 1, 'course_name': 'Math'}, {'id': 4, 'course_name': 'Biology'}, {'id': 3, 'course_name': 'Chemistry'}]  # Year 2 courses
# }

# years = [
#     {'id': 1, 'name': 'Year 1'},
#     {'id': 2, 'name': 'Year 2'}
# ]

# # Timeslots updated with the 45-minute intervals
# timeslots = [
#     {'day': 'Sunday', 'slot': 1, 'start_time': '08:30', 'end_time': '09:15'},
#     {'day': 'Sunday', 'slot': 2, 'start_time': '09:15', 'end_time': '10:00'},
#     {'day': 'Sunday', 'slot': 3, 'start_time': '10:30', 'end_time': '11:15'},
#     {'day': 'Sunday', 'slot': 4, 'start_time': '11:15', 'end_time': '12:00'},
#     {'day': 'Sunday', 'slot': 5, 'start_time': '14:00', 'end_time': '14:45'},
#     {'day': 'Sunday', 'slot': 6, 'start_time': '14:45', 'end_time': '15:30'},
#     {'day': 'Sunday', 'slot': 7, 'start_time': '15:30', 'end_time': '16:15'},
#     {'day': 'Monday', 'slot': 8, 'start_time': '08:30', 'end_time': '09:15'},
#     {'day': 'Monday', 'slot': 9, 'start_time': '09:15', 'end_time': '10:00'},
#     {'day': 'Monday', 'slot': 10, 'start_time': '10:30', 'end_time': '11:15'},
#     {'day': 'Monday', 'slot': 11, 'start_time': '11:15', 'end_time': '12:00'},
#     {'day': 'Monday', 'slot': 12, 'start_time': '14:00', 'end_time': '14:45'},
#     {'day': 'Monday', 'slot': 13, 'start_time': '14:45', 'end_time': '15:30'},
#     {'day': 'Monday', 'slot': 14, 'start_time': '15:30', 'end_time': '16:15'},
# ]

# # Number of hours per course
# hours_per_course = {'Math': 3, 'Physics': 1.5, 'Chemistry': 1.5, 'Biology': 1.5}

# # Maximum teaching hours for each teacher
# teacher_max_hours = {1: 6, 2: 6, 3: 6}  # Teacher 1 can teach up to 6 hours, etc.




teachers = [
    {'id': 1, 'name': 'Dr. Smith', 'courses': [1, 2], 'state': 'working'},  # Math, Physics
    {'id': 2, 'name': 'Ms. Johnson', 'courses': [3], 'state': 'working'},  # Chemistry
    {'id': 3, 'name': 'Mr. Brown', 'courses': [1, 4], 'state': 'working'},  # Math, Biology
    {'id': 4, 'name': 'Dr. White', 'courses': [5, 6], 'state': 'working'},  # English, History
    {'id': 5, 'name': 'Ms. Davis', 'courses': [7], 'state': 'working'},  # Computer Science
    {'id': 6, 'name': 'Dr. Green', 'courses': [4, 8], 'state': 'working'}  # Biology, Chemistry
]

# Expanded classroom data
classrooms = [
    {'id': 101, 'name': 'Room A'},
    {'id': 102, 'name': 'Room B'},
    {'id': 103, 'name': 'Lab 1'},
    # {'id': 104, 'name': 'Room C'},
    # {'id': 105, 'name': 'Lab 2'}
]

# Courses available for 5 years
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
# Continuous timeslots from Sunday to Thursday with 45-minute intervals
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

# Maximum teaching hours for each teacher
teacher_max_hours = {
    1: 20,  # Dr. Smith
    2: 15,  # Ms. Johnson
    3: 18,  # Mr. Brown
    4: 22,  # Dr. White
    5: 17,  # Ms. Davis
    6: 19   # Dr. Green
}
# Number of hours per course
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

# population = generate_population(1, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
# display_population(population)

# for idx, individual in enumerate(population):
#     fitness = fitness_function(individual,teacher_max_hours)
#     print(f"Fitness of individual {idx + 1}: {fitness}")




# def genetic_algorithm(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course, max_generations=MAX_GENERATIONS, target_fitness=TARGET_FITNESS):
#     """
#     Execute the genetic algorithm to find an optimal timetable.

#     Parameters:
#     - population_size: Number of individuals in the population.
#     - years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course: As defined in your setup.
#     - max_generations: Maximum number of generations to run the algorithm.
#     - target_fitness: Desired fitness level to achieve (0 for perfect solution).

#     Returns:
#     - Best individual found and its fitness.
#     """
#     # Generate initial population
#     population = generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)
    
#     for generation in range(max_generations):
#         # Calculate fitness for each individual
#         fitness_scores = [fitness_function(individual, teacher_max_hours) for individual in population]
        
#         # Display current generation results
#         print(f"Generation {generation + 1}")
#         for idx, fitness in enumerate(fitness_scores):
#             print(f"  Fitness of individual {idx + 1}: {fitness}")
        
#         # Check if we have found a solution with target fitness
#         if max(fitness_scores) >=50:
#             best_index = fitness_scores.index(max(fitness_scores))
#             best_individual = population[best_index]
#             print("Found optimal solution!")
#             # display_population([best_individual])
#             return best_individual, fitness_scores[best_index]

#         # Pair fitness scores with individuals
#         paired_population = list(zip(fitness_scores, population))

#         # Sort based on fitness scores (highest fitness is better)
#         sorted_population = sorted(paired_population, key=lambda x: x[0], reverse=True)

#         # Select the top half of the population based on fitness
#         top_half = [indiv for _, indiv in sorted_population[:len(sorted_population) // 2]]
        
#         # Generate new population through crossover
#         new_population = []
#         while len(new_population) < population_size:
#             parent1, parent2 = random.sample(top_half, 2)
#             child1, child2 = crossover(parent1, parent2)
#             # child1 = mutate(child1)
#             # child2 = mutate(child2) 
#             new_population.extend([child1, child2])
        
#         # Ensure the new population size matches the required population size
#         population = new_population[:population_size]

#     # Final output
#     best_index = fitness_scores.index(max(fitness_scores))
#     best_individual = population[best_index]
#     print("Reached maximum generations.")
#     display_population([best_individual])
#     return best_individual, fitness_scores[best_index]

def display_best_result(best_individual, fitness):
    """
    Display the best result found by the genetic algorithm.
    """
    print("\nBest Individual Found:")
    display_population([best_individual])
    print(f"Fitness: {fitness}")

# Example usage:
best_individual, best_fitness = genetic_algorithm(
    population_size=10, 
    years=years, 
    year_courses=year_courses, 
    teachers=teachers, 
    classrooms=classrooms, 
    timeslots=timeslots, 
    teacher_max_hours=teacher_max_hours, 
    hours_per_course=hours_per_course
)
display_best_result(best_individual, best_fitness)








# def genetic_algorithm(population_size, generations, mutation_rate, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course):
#     # Generate the initial population
#     population = generate_population(population_size, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)

#     # Initialize year_timeslot_usage
#     year_timeslot_usage = {year['id']: [] for year in years}

#     for generation in range(generations):
#         # Evaluate fitness for each individual
#         fitness_scores = [fitness_function(individual, teacher_max_hours) for individual in population]
#         print(f"Generation {generation + 1} Best Fitness: {max(fitness_scores)}")

#         # Select parents based on fitness
#         parents = sorted(zip(population, fitness_scores), key=lambda x: x[1])
#         parents = [p[0] for p in parents[:population_size // 2]]  # Select the top half as parents

#         # Generate new population through crossover and mutation
#         new_population = []
#         while len(new_population) < population_size:
#             parent1, parent2 = random.sample(parents, 2)
#             offspring1, offspring2 = crossover(parent1, parent2)
#             new_population.append(offspring1)
#             new_population.append(offspring2)
#             # new_population.append(mutate(offspring1, mutation_rate, teachers, classrooms, timeslots, teacher_max_hours, year_timeslot_usage))
#             # new_population.append(mutate(offspring2, mutation_rate, teachers, classrooms, timeslots, teacher_max_hours, year_timeslot_usage))
        
#         population = new_population

#         # Display best individual of the current generation
#         best_individual = min(population, key=lambda ind: fitness_function(ind, teacher_max_hours))
#         # print(f"Generation {generation + 1} Best Fitness: {fitness_function(best_individual, teacher_max_hours)}")

#     return population

# Test setup
# population_size = 10
# generations = 50
# mutation_rate = 0.1


# Run the genetic algorithm
# final_population = genetic_algorithm(population_size, generations, mutation_rate, years, year_courses, teachers, classrooms, timeslots, teacher_max_hours, hours_per_course)

