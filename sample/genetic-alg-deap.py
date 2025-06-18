import random
import string
from deap import base, creator, tools, algorithms

# PARAMETERS
TARGET = "Hello, world!"
CHARS = string.ascii_letters + string.punctuation + " "
IND_SIZE = len(TARGET)
POP_SIZE = 300
GENS = 1000
MUTPB = 0.2
CXPB = 0.5

# FITNESS: maximize number of correct characters
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_char", random.choice, CHARS)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_char, n=IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def eval_fitness(individual):
    return sum(individual[i] == TARGET[i] for i in range(len(TARGET))),  # comma = tuple

toolbox.register("evaluate", eval_fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(CHARS)-1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

# Needed because mutUniformInt works with ints
def repair(individual):
    for i in range(len(individual)):
        if isinstance(individual[i], int):
            individual[i] = CHARS[individual[i]]

# MAIN LOOP
def main():
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", max)

    for gen in range(GENS):
        offspring = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB)
        for ind in offspring:
            repair(ind)
            ind.fitness.values = toolbox.evaluate(ind)
        pop = toolbox.select(offspring, k=len(pop))
        hof.update(pop)

        print(f"Gen {gen:3}: Best = {''.join(hof[0])} | Fitness = {hof[0].fitness.values[0]}")
        if ''.join(hof[0]) == TARGET:
            print("Target reached.")
            break

if __name__ == "__main__":
    main()
