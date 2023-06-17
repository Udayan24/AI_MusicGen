from random import choices, randint, randrange, random, sample
from typing import List, Optional, Callable, Tuple

Genome = List[int]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc  = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]

# Swap sub-arrays from a random point
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes A and B must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    # Pick a random point and swap sub-arrays
    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

# Change a bit according to specified probability
def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )

def generate_weighted_distribution(population: Population, fitness_func: FitnessFunc) -> Population:
    result = []

    for gene in population:
        result += [gene] * int(fitness_func(gene)+1)

    return result
