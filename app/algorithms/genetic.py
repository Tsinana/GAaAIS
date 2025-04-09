import random
import networkx as nx
from typing import List, Dict, Tuple


Chromosome = List[int]
Population = List[Chromosome]


class GeneticAlgorithm:
    def __init__(self, graph: nx.Graph, population_size: int, generations: int):
        self.graph = graph
        self.population_size = population_size
        self.generations = generations
        self.nodes = list(graph.nodes)
        self.num_nodes = len(self.nodes)
    
    def initial_population(self) -> Population:
        """Создает начальную популяцию (дробовик)."""
        return [random.sample(self.nodes, self.num_nodes) for _ in range(self.population_size)]
    
    def decode_chromosome(self, chromosome: Chromosome) -> Dict[int, int]:
        """Декодирует хромосому в раскраску графа."""
        color_assignment = {}
        current_color = 0
        for node in chromosome:
            if all(not self.graph.has_edge(node, colored_node)
                   or color_assignment[colored_node] != current_color
                   for colored_node in color_assignment):
                color_assignment[node] = current_color
            else:
                current_color += 1
                color_assignment[node] = current_color
        return color_assignment
    
    def fitness(self, chromosome: Chromosome) -> float:
        """Вычисляет целевую функцию (отношение цветов к вершинам)."""
        colors = self.decode_chromosome(chromosome)
        num_colors = len(set(colors.values()))
        return num_colors / self.num_nodes
    
    def selection(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        """Турнирная селекция с размером турнира 2."""
        participants = random.sample(population, 4)
        participants.sort(key=self.fitness)
        return participants[0], participants[1]
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        """Упорядоченный кроссинговер."""
        point = random.randint(1, self.num_nodes - 2)
        child = parent1[:point] + [node for node in parent2 if node not in parent1[:point]]
        return child
    
    def mutate(self, chromosome: Chromosome, mutation_rate: float = 0.05) -> Chromosome:
        """Оператор мутации, аналогичный модели Де Фриза (мутация с глобальным изменением)."""
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(self.num_nodes), 2)
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
        return chromosome
    
    def evolve(self, population: Population) -> Population:
        """Эволюционный шаг по Дарвину с мутацией Де Фриза при отсутствии улучшения."""
        new_population = []
        best_fitness = min(self.fitness(chromo) for chromo in population)
        
        for _ in range(self.population_size):
            parent1, parent2 = self.selection(population)
            child = self.crossover(parent1, parent2)
            
            child_fitness = self.fitness(child)
            if child_fitness >= best_fitness:
                child = self.mutate(child, mutation_rate=0.2)  # Де Фриз
            else:
                child = self.mutate(child, mutation_rate=0.05)  # Дарвин
            
            new_population.append(child)
        
        return new_population
    
    def solve(self) -> Dict[int, int]:
        """Основной метод для запуска ГА."""
        population = self.initial_population()
        best_solution = min(population, key=self.fitness)
        
        for _ in range(self.generations):
            population = self.evolve(population)
            current_best = min(population, key=self.fitness)
            
            if self.fitness(current_best) < self.fitness(best_solution):
                best_solution = current_best
        
        return self.decode_chromosome(best_solution)


# Основная точка входа
def genetic_coloring(graph: nx.Graph, params: Dict) -> Dict[int, int]:
    """
    Генетический алгоритм раскраски графа с использованием эволюционных моделей Дарвина и Де Фриза.

    :param graph: Граф NetworkX для раскраски.
    :param params: Словарь с параметрами (размер популяции и число поколений).
    :return: Словарь (вершина: цвет).
    """
    try:
        ga = GeneticAlgorithm(
            graph=graph,
            population_size=params.get("population_size", 50),
            generations=params.get("generations", 100)
        )
        return ga.solve()
    except Exception as e:
        raise RuntimeError(f"Ошибка при выполнении генетического алгоритма: {e}")
