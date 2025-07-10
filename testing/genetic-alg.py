import random
import string

# PARAMETERS
TARGET = "Hello, world!"
POP_SIZE = 200
MUTATION_RATE = 0.01
GENERATIONS = 1000

# HELPERS
CHARACTERS = string.ascii_letters + string.punctuation + ' '

def random_string(length):
    return ''.join(random.choice(CHARACTERS) for _ in range(length))

def fitness(individual):
    return sum(1 for i, c in enumerate(individual) if c == TARGET[i])

def mutate(individual):
    return ''.join(
        c if random.random() > MUTATION_RATE else random.choice(CHARACTERS)
        for c in individual
    )

def crossover(parent1, parent2):
    pivot = random.randint(0, len(parent1))
    return parent1[:pivot] + parent2[pivot:]

def select(population, fitnesses):
    # Roulette wheel selection
    total_fit = sum(fitnesses)
    pick = random.uniform(0, total_fit)
    current = 0
    for ind, fit in zip(population, fitnesses):
        current += fit
        if current > pick:
            return ind

# INITIALIZE
population = [random_string(len(TARGET)) for _ in range(POP_SIZE)]

# RUN
for generation in range(GENERATIONS):
    fitnesses = [fitness(ind) for ind in population]
    best = max(population, key=fitness)
    print(f"Gen {generation}: {best} (Fitness: {fitness(best)})")

    if best == TARGET:
        print("Target reached!")
        break

    new_population = []
    for _ in range(POP_SIZE):
        p1 = select(population, fitnesses)
        p2 = select(population, fitnesses)
        child = crossover(p1, p2)
        child = mutate(child)
        new_population.append(child)

    population = new_population
