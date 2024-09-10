import random

# Define constants for encoding
NUM_SLOTS_PER_DAY = 8  # 8 periods per day
NUM_DAYS = 5  # 5 days a week
NUM_SUBJECTS = 4  # 4 subjects
TIMETABLE_SIZE = NUM_SLOTS_PER_DAY * NUM_DAYS  # Total slots in the timetable (8 * 5 = 40)

def encode_slot(time_slot, day, subject):
    """
    Encode a slot into an 8-bit string.
    - time_slot: 3 bits (0 to 7)
    - day: 3 bits (0 to 4)
    - subject: 2 bits (0 to 3)
    
    Returns:
    - 8-bit integer representation of the slot
    """
    return (time_slot << 5) | (day << 2) | subject

def decode_slot(slot_code):
    """
    Decode an 8-bit slot back into time slot, day, and subject.
    - slot_code: 8-bit encoded value
    
    Returns:
    - Tuple (time_slot, day, subject)
    """
    time_slot = (slot_code >> 5) & 0b111
    day = (slot_code >> 2) & 0b111
    subject = slot_code & 0b11
    return time_slot, day, subject

def generate_gene():
    """
    Generate a random 8-bit gene representing a time slot, day, and subject.
    
    Returns:
    - 8-bit integer for one slot
    """
    time_slot = random.randint(0, NUM_SLOTS_PER_DAY - 1)  # 3 bits
    day = random.randint(0, NUM_DAYS - 1)  # 3 bits
    subject = random.randint(0, NUM_SUBJECTS - 1)  # 2 bits
    return encode_slot(time_slot, day, subject)

def generate_population(population_size):
    """
    Generate a population of random timetables (chromosomes).
    Each timetable is a list of 40 8-bit genes (40 slots x 8 bits).
    
    Args:
    - population_size: The number of timetables (chromosomes) to generate.
    
    Returns:
    - List of timetables, each a list of 40 8-bit genes
    """
    population = []
    for _ in range(population_size):
        individual = [generate_gene() for _ in range(TIMETABLE_SIZE)]
        population.append(individual)
    return population

####################################################
def fitness_function(timetable):
    """
    Evaluate the fitness of a timetable. 
    Higher fitness means fewer clashes and better optimization.
    
    Parameters:
    - timetable: List of 8-bit slots
    
    Returns:
    - Fitness score (higher is better)
    """
    fitness = 0
    
    # Example fitness rules (these can be adjusted as needed):
    seen_slots = set()
    
    for slot in timetable:
        # Decode the slot
        time_slot, day, subject = decode_slot(slot)
        
        # Rule 1: No duplicate classes in the same time slot (clash check)
        if (time_slot, day) in seen_slots:
            fitness -= 1  # Penalize for clashes
        else:
            seen_slots.add((time_slot, day))
            fitness += 1  # Reward for valid assignments

    return fitness
#################################################################

def selection(population, fitness_func, k=2):
    """
    Select k individuals from the population based on their fitness scores.
    
    Returns:
    - A pair of selected individuals (parents)
    """
    return random.choices(population, weights=[fitness_func(ind) for ind in population], k=k)

#################################################################
def crossover(parent1, parent2):
    """
    Perform crossover between two parents to create offspring.
    
    Returns:
    - A new child individual (list of 8-bit genes)
    """
    crossover_point = random.randint(1, TIMETABLE_SIZE - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    return child

#################################################################
def mutate(individual, mutation_rate=0.01):
    """
    Mutate an individual by flipping random bits with a certain probability.
    
    Parameters:
    - individual: List of 8-bit genes
    - mutation_rate: Probability of mutation per gene
    
    Returns:
    - Mutated individual
    """
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            individual[i] = generate_gene()  # Replace the gene with a new random one
    return individual

#################################################################
def format_timetable(timetable):
    """
    Format the timetable into a readable string.
    
    Parameters:
    - timetable: List of 8-bit slots
    
    Returns:
    - Formatted string representing the timetable
    """
    formatted_slots = []
    for slot in timetable:
        time_slot, day, subject = decode_slot(slot)
        formatted_slots.append(f"Time Slot: {time_slot}, Day: {day}, Subject: {subject}")
    
    return "Timetable:\n" + "\n".join(formatted_slots)
# #################################################################
def genetic_algorithm(population_size, generations, mutation_rate=0.01):
    """
    Main genetic algorithm loop.
    
    Parameters:
    - population_size: Number of individuals in the population
    - generations: Number of generations to run the algorithm for
    - mutation_rate: Probability of mutation per gene
    
    Returns:
    - Formatted string of the best timetable after all generations
    """
    # Initialize population
    population = generate_population(population_size)
    
    # Variable to track the best timetable found
    best_timetable = None
    best_fitness = float('-inf')  # Start with a very low fitness score

    for generation in range(generations):
        # Evaluate fitness for the current population
        population = sorted(population, key=lambda ind: fitness_function(ind), reverse=True)
        
        # Get the best individual of the current generation
        current_best_timetable = population[0]
        current_best_fitness = fitness_function(current_best_timetable)
        
        # Update the best timetable if the current one is better
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_timetable = current_best_timetable
        
        # Print the best fitness in each generation
        print(f"Generation {generation+1} - Best fitness: {best_fitness}")
        
        # If optimal solution is found, print and break (Optional: To stop early if perfect solution is found)
        if best_fitness == TIMETABLE_SIZE:  # Full score (no clashes)
            print("Perfect timetable found!")
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

    # Return the best individual found, formatted
    
    return format_timetable(best_timetable)

# Example run:
best_timetable_formatted = genetic_algorithm(population_size=300, generations=300)
print("\n" + best_timetable_formatted)









#################################################################
# def genetic_algorithm(population_size, generations, mutation_rate=0.01):
#     """
#     Main genetic algorithm loop.
    
#     Parameters:
#     - population_size: Number of individuals in the population
#     - generations: Number of generations to run the algorithm for
#     - mutation_rate: Probability of mutation per gene
    
#     Returns:
#     - The best individual (timetable) after all generations
#     """
#     # Initialize population
#     population = generate_population(population_size)
    
#     for generation in range(generations):
#         # Evaluate fitness for the current population, iterate each timetable
#         population = sorted(population, key=lambda ind: fitness_function(ind), reverse=True)
        
#         # After sorting, population[0] represents the best individual (the one with the highest fitness).
#         best_fitness = fitness_function(population[0])
#         print(f"Generation {generation+1} - Best fitness: {best_fitness}")
        
#         # If optimal solution is found (you can define your own threshold)
#         if best_fitness == TIMETABLE_SIZE:  # Full score (no clashes)
#             break
        
#         # Selection (choose parents)
#         new_population = []
#         for _ in range(population_size // 2):
#             parent1, parent2 = selection(population, fitness_function)#tfout 3la nos population ,50% lwala w
#                                                                       #tkhrej parents l kol wahed tsma nkhrjou f population jdida
#             # Crossover to create offspring
#             child1 = crossover(parent1, parent2)
#             child2 = crossover(parent2, parent1)
            
#             # Mutate offspring
#             child1 = mutate(child1, mutation_rate)
#             child2 = mutate(child2, mutation_rate)
            
#             # Add offspring to new population
#             new_population.extend([child1, child2])
        
#         population = new_population  # Update population, hnaya ttbedel population tji fi blassetha jdida w n3awdou hadi 3la hseb number of generations
    
#     # Return the best individual found
#     best_timetable = population[0]
#     return format_timetable(best_timetable)

# # Example run:
# best_timetable = genetic_algorithm(population_size=100, generations=100)
# print("\nBest timetable (encoded genes):", best_timetable)






# def print_population_with_fitness(population):
#     """
#     Print the population in a readable format showing each timetable (chromosome),
#     and calculate and print the fitness of each timetable.
#     """
#     for idx, individual in enumerate(population):
#         print(f"Timetable {idx + 1}:")
#         for gene in individual:
#             time_slot, day, subject = decode_slot(gene)
#             print(f"  Time Slot: {time_slot}, Day: {day}, Subject: {subject}")
        
#         # Calculate fitness for the individual timetable
#         fitness = fitness_function(individual)
#         print(f"Fitness score for Timetable {idx + 1}: {fitness}")
#         print("-" * 40)


# # Generate a population of 3 timetables (chromosomes) as an example
# population_size = 3
# population = generate_population(population_size)

# # Print the population
# print_population_with_fitness(population)
