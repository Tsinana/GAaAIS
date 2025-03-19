import random


class GeneticAlgorithm:
    def __init__(self, graph, params):
        self.graph = graph
        self.population_size = params.get('population_size', 50)
        self.generations = params.get('generations', 10)
        self.mutation_rate = params.get('mutation_rate', 0.1)
        self.elite_size = params.get('elite_size', 5)
        self.stagnation_limit = params.get('stagnation_limit', 10)
        self.best_fitness_history = []

    def initial_population(self):
        """Генерирует начальную популяцию."""
        population = []
        for _ in range(self.population_size):
            coloring = {node: random.randint(0, len(self.graph.nodes)) for node in self.graph.nodes}
            population.append(coloring)
        return population

    def fitness(self, coloring):
        """Функция оценки особей. Меньшее количество конфликтов лучше."""
        conflicts = sum(1 for u, v in self.graph.edges if coloring[u] == coloring[v])
        colors_used = len(set(coloring.values()))
        return conflicts, colors_used

    def selection(self, population):
        """Селекция на основе рулетки."""
        fitness_values = [1 / (1 + self.fitness(ind)[0]) for ind in population]
        return random.choices(population, weights=fitness_values, k=2)

    def crossover(self, parent1, parent2):
        """Одноточечный кроссовер."""
        crossover_point = random.randint(0, len(parent1) - 1)
        child = {}
        for i, node in enumerate(parent1):
            child[node] = (
                parent1[node] if i <= crossover_point else parent2[node]
            )
        return child

    def mutate(self, coloring):
        """Мутация."""
        node = random.choice(list(coloring.keys()))
        coloring = coloring.copy()
        coloring[node] = random.randint(0, max(coloring.values()) + 1)
        return coloring

    def mutate_drastic(self, coloring):
        """Резкая мутация (Де Фриз)."""
        coloring = {node: random.randint(0, len(self.graph.nodes)) for node in coloring}
        return coloring

    def evolve(self, population):
        """Эволюционный шаг по модели Дарвина."""
        new_population = []
        sorted_pop = sorted(population, key=lambda ind: self.fitness(ind))
        new_population.extend(sorted_pop[:self.elite_size])

        while len(new_population) < len(population):
            parent1, parent2 = self.selection(sorted_pop)
            child = self.crossover(parent1, parent2)
            if random.random() < self.mutation_rate:
                child = self.mutate(child)
            new_population.append(child)

        return new_population

    def evolve_with_de_vries(self, population):
        """Эволюционный шаг по модели Де Фриза."""
        return [self.mutate_drastic(individual) for individual in population]

    def solve(self):
        population = self.initial_population()
        stagnation_counter = 0

        for generation in range(self.generations):
            population = self.evolve(population)
            best_fitness = min(self.fitness(ind) for ind in population)[0]

            if self.best_fitness_history and best_fitness >= self.best_fitness_history[-1]:
                stagnation_counter += 1
            else:
                stagnation_counter = 0

            self.best_fitness_history.append(best_fitness)

            if stagnation_counter >= self.stagnation_limit:
                population = self.evolve_with_de_vries(population)
                stagnation_counter = 0

        best_solution = min(population, key=lambda ind: self.fitness(ind))
        return best_solution


def genetic_coloring(graph, params):
    ga = GeneticAlgorithm(graph, params)
    best_solution = ga.solve()
    return best_solution
