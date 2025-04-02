import random
def immune_coloring(graph, params):

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]

    def add_edge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)

class ImmuneNetwork:
    def __init__(self, graph, num_colors, population_size):
        self.graph = graph
        self.num_colors = num_colors
        self.population_size = population_size
        self.population = []
        self.best_solution = None

    def generate_individual(self):
        return [random.randint(0, self.num_colors - 1) for _ in range(self.graph.V)]

    def fitness(self, individual):
        conflicts = 0
        for u in range(self.graph.V):
            for v in self.graph.graph[u]:
                if individual[u] == individual[v]:
                    conflicts += 1
        return -conflicts  # Чем меньше конфликтов, тем лучше

    def initialize_population(self):
        for _ in range(self.population_size):
            individual = self.generate_individual()
            self.population.append(individual)

    def select_best(self):
        best_fitness = float('-inf')
        best_individual = None
        for individual in self.population:
            fit = self.fitness(individual)
            if fit > best_fitness:
                best_fitness = fit
                best_individual = individual
        return best_individual

    def mutate(self, individual):
        index = random.randint(0, len(individual) - 1)
        new_color = random.randint(0, self.num_colors - 1)
        individual[index] = new_color

    def run(self, iterations):
        self.initialize_population()
        for _ in range(iterations):
            new_population = []
            for individual in self.population:
                new_individual = individual[:]
                if random.random() < 0.1:  # Вероятность мутации
                    self.mutate(new_individual)
                new_population.append(new_individual)

            # Обновляем популяцию
            self.population.extend(new_population)
            # Сохраняем лучшее решение
            best_individual = self.select_best()
            if not self.best_solution or (self.fitness(best_individual) > self.fitness(self.best_solution)):
                self.best_solution = best_individual

# Пример использования
if __name__ == "__main__":
    g = Graph(6)
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(4, 5)
    g.add_edge(0, 5)

    num_colors = 3
    population_size = 100
    iterations = 1

    immune_network = ImmuneNetwork(g, num_colors, population_size)
    immune_network.run(iterations)

    print("Решение:", immune_network.best_solution)
