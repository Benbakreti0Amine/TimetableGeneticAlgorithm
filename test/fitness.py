# 3 bits for Time Slot | 3 bits for Day | 2 bits for Course | 3 bits for Teacher | 3 bits for Classroom | 2 bits for Student Group
import random
from simple.init import  crossover, mutate, selection
# Define constants for encoding
NUM_SLOTS_PER_DAY = 8  # 8 periods per day
NUM_DAYS = 5  # 5 days a week
NUM_SUBJECTS = 4  # 4 subjects
TIMETABLE_SIZE = NUM_SLOTS_PER_DAY * NUM_DAYS  # Total slots in the timetable (8 * 5 = 40)
NUM_TEACHERS = 8
NUM_CLASSROOMS = 8
NUM_STUDENT_GROUPS = 4
def generate_gene():
    """
    Generate a random 16-bit gene representing time slot, day, course, teacher, classroom, and student group.
    
    Returns:
    - 16-bit integer for one slot
    """
    time_slot = random.randint(0, NUM_SLOTS_PER_DAY - 1)  # 3 bits
    day = random.randint(0, NUM_DAYS - 1)  # 3 bits
    course = random.randint(0, NUM_SUBJECTS - 1)  # 2 bits
    teacher = random.randint(0, NUM_TEACHERS - 1)  # 3 bits (assumes up to 8 teachers)
    classroom = random.randint(0, NUM_CLASSROOMS - 1)  # 3 bits (assumes up to 8 classrooms)
    student_group = random.randint(0, NUM_STUDENT_GROUPS - 1)  # 2 bits (assumes up to 4 groups)
    
    return encode_schedule(time_slot, day, course, teacher, classroom, student_group)

###############################################################

def generate_population(population_size):
    """
    Generate a population of random timetables.
    Each timetable is a list of genes, where each gene is a 16-bit integer.

    Returns:
    - List of individuals (each a list of genes)
    """
    population = []
    for _ in range(population_size):
        individual = [generate_gene() for _ in range(TIMETABLE_SIZE)]  # 40 slots, each represented by 16 bits
        population.append(individual)
    return population

###############################################################

def encode_schedule(time_slot, day, course, teacher, classroom, student_group):
    """
    Encode a schedule into a 16-bit integer.
    - time_slot: 3 bits (0 to 7)
    - day: 3 bits (0 to 4)
    - course: 2 bits (0 to 3)
    - teacher: 3 bits (0 to 7)
    - classroom: 3 bits (0 to 7)
    - student_group: 2 bits (0 to 3)
    
    Returns:
    - 16-bit integer representation of the schedule
    """
    return (time_slot << 13) | (day << 10) | (course << 8) | (teacher << 5) | (classroom << 2) | student_group

###############################################################

def decode_schedule(schedule_code):
    """
    Decode a 16-bit schedule back into components.
    - schedule_code: 16-bit encoded value
    
    Returns:
    - Tuple (time_slot, day, course, teacher, classroom, student_group)
    """
    time_slot = (schedule_code >> 13) & 0b111
    day = (schedule_code >> 10) & 0b111
    course = (schedule_code >> 8) & 0b11
    teacher = (schedule_code >> 5) & 0b111
    classroom = (schedule_code >> 2) & 0b111
    student_group = schedule_code & 0b11
    return time_slot, day, course, teacher, classroom, student_group

###############################################################
def fitness_function(schedule):
    """
    Evaluate the fitness of a schedule based on several criteria.
    Higher fitness means fewer clashes and better adherence to constraints.
    
    Parameters:
    - schedule: List of 16-bit schedules
    
    Returns:
    - Fitness score (higher is better)
    """
    fitness = 0
    seen_slots = set()
    teacher_slots = {}
    classroom_slots = {}
    student_group_slots = {}

    for code in schedule:
        time_slot, day, course, teacher, classroom, student_group = decode_schedule(code)
        
        # Check for clashes
        if (time_slot, day) in seen_slots:
            fitness -= 1  # Penalize for clashes
        else:
            seen_slots.add((time_slot, day))
            fitness += 1  # Reward for valid assignments

        # Additional checks
        # Teacher scheduling
        if (teacher, time_slot, day) in teacher_slots:
            fitness -= 2  # Penalize for teacher conflicts
        else:
            teacher_slots[(teacher, time_slot, day)] = course
            fitness += 2  # Reward for valid teacher scheduling

        # Classroom scheduling
        if (classroom, time_slot, day) in classroom_slots:
            fitness -= 2  # Penalize for classroom conflicts
        else:
            classroom_slots[(classroom, time_slot, day)] = course
            fitness += 2  # Reward for valid classroom scheduling

        # Student group scheduling
        if (student_group, course, time_slot, day) in student_group_slots:
            fitness -= 2  # Penalize for student group conflicts
        else:
            student_group_slots[(student_group, course, time_slot, day)] = True
            fitness += 2  # Reward for valid student group scheduling

    return fitness

###############################################################

def display_timetable(timetable):
    """
    Display the timetable in a readable format.
    
    Parameters:
    - timetable: List of 16-bit genes
    
    Returns:
    - None (prints the timetable)
    """
    print("Timetable:")
    for gene in timetable:
        time_slot, day, course, teacher, classroom, student_group = decode_schedule(gene)
        print(f"Time Slot: {time_slot}, Day: {day}, Course: {course}, Teacher: {teacher}, Classroom: {classroom}, Student Group: {student_group}")

###############################################################
def genetic_algorithm(population_size, generations, mutation_rate=0.01):
    """
    Main genetic algorithm loop with tracking of the best timetable.
    
    Parameters:
    - population_size: Number of individuals in the population
    - generations: Number of generations to run the algorithm for
    - mutation_rate: Probability of mutation per gene
    
    Returns:
    - The best individual (timetable) found after all generations
    """
    # Initialize population
    population = generate_population(population_size)
    
    # Initialize variables to track the best individual
    best_individual = None
    best_fitness = -float('inf')
    
    for generation in range(generations):
        # Evaluate fitness for the current population
        population_fitness = [fitness_function(ind) for ind in population]
        population = [ind for _, ind in sorted(zip(population_fitness, population), key=lambda x: x[0], reverse=True)]
        
        # Track the best individual
        current_best_fitness = fitness_function(population[0])
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = population[0]
        
        # Print the best fitness in each generation
        print(f"Generation {generation+1} - Best fitness: {best_fitness}")
        
        # If optimal solution is found (you can define your own threshold)
        if best_fitness == TIMETABLE_SIZE:  # Full score (no clashes)
            break
        
        # Selection (choose parents)
        new_population = []
        for _ in range(population_size // 2):
            parent1, parent2 = selection(population, fitness_function)
            
            # Crossover to create offspring
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            
            # Mutate offspring
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            # Add offspring to new population
            new_population.extend([child1, child2])
        
        population = new_population  # Update population
    
    # Return the best individual found
    return display_timetable(best_individual)

# Example run:
best_timetable = genetic_algorithm(population_size=100, generations=100)
print("\nBest timetable:")
display_timetable(best_timetable)


###############################################################
###############################################################
