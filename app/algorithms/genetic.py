import random
import networkx as nx
from typing import List, Dict, Tuple


Chromosome = List[int]
Population = List[Chromosome]


def exact_coloring(graph: nx.Graph) -> Dict[int, int]:
    """
    Реализация точного алгоритма раскраски графа с использованием жадного алгоритма.
    """
    coloring = nx.greedy_color(graph, strategy='largest_first')
    return coloring


class GeneticAlgorithm:
    """
    Генетический алгоритм для раскраски графа.
    
    Кодирование хромосом:
    - Генами являются номера вершин графа
    - Порядок расположения вершин в хромосоме определяет порядок раскраски
    - Хромосома содержит все номера вершин графа (число генов = количеству вершин)
    
    Декодирование хромосомы:
    1. Начинаем с первого цвета (0) как текущего
    2. Последовательно берем вершины из хромосомы:
       - Если вершина не смежна с вершинами, уже окрашенными текущим цветом,
         то она также окрашивается текущим цветом
       - Иначе увеличиваем номер текущего цвета и раскрашиваем вершину новым цветом
    3. Процесс повторяется для всех генов хромосомы
    
    Целевая функция:
    - Отношение количества использованных цветов к количеству вершин графа
    - Задача алгоритма - минимизация целевой функции
    """
    def __init__(self, graph: nx.Graph, population_size: int, generations: int):
        self.graph = graph
        self.population_size = population_size
        self.generations = generations
        self.nodes = list(graph.nodes)
        self.num_nodes = len(self.nodes)
    
    def initial_population(self) -> Population:
                # """Создает начальную популяцию (дробовик)."""
        # return [random.sample(self.nodes, self.num_nodes) for _ in range(self.population_size)]
        """Создает начальную популяцию на основе жадного алгоритма."""
        population = []
        
        # Создаем первую хромосому с помощью жадного алгоритма
        coloring = exact_coloring(self.graph)
        # Сортируем узлы по их цветам
        sorted_nodes = sorted(self.nodes, key=lambda node: coloring[node])
        population.append(sorted_nodes)
        
        # Создаем вариации начальной популяции
        for _ in range(self.population_size - 1):
            # Комбинируем жадное решение со случайными перестановками
            new_chromosome = sorted_nodes.copy()
            # Вносим случайное возмущение
            idx1, idx2 = random.sample(range(self.num_nodes), 2)
            new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]
            population.append(new_chromosome)
            
        return population
    
    def decode_chromosome(self, chromosome: Chromosome) -> Dict[int, int]:
        """
        Декодирует хромосому в раскраску графа.
        
        Алгоритм:
        1. Берем вершины из хромосомы по порядку
        2. Для каждой вершины проверяем возможность окрашивания текущим цветом
        3. Если смежные вершины не окрашены текущим цветом, используем его
        4. Иначе увеличиваем номер цвета и используем новый цвет
        
        Returns:
            Словарь с раскраской графа (вершина: цвет)
        """
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
        """
        Вычисляет целевую функцию (отношение цветов к вершинам).
        
        Функция должна быть минимизирована, поэтому лучшие решения имеют
        меньшие значения фитнеса (меньшее количество цветов).
        
        Returns:
            Значение целевой функции (число цветов / число вершин)
        """
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
        """
        Основной метод для запуска генетического алгоритма.
        
        Алгоритм:
        1. Создание начальной популяции
        2. Поиск лучшего решения в текущей популяции
        3. Эволюция популяции через указанное число поколений:
           - Отбор родителей (турнирная селекция)
           - Кроссинговер (создание потомков)
           - Мутация (внесение случайных изменений)
           - Отбор лучших особей для следующего поколения
        4. Возврат лучшего найденного решения
        
        Returns:
            Словарь с оптимальной раскраской графа (вершина: цвет)
        """
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
    
    Алгоритм использует специальное кодирование хромосом, где гены представляют порядок
    рассмотрения вершин при раскраске. Хромосома декодируется путем последовательного
    назначения цветов вершинам в порядке их расположения в хромосоме.
    
    Целевая функция: отношение количества использованных цветов к числу вершин графа.
    Задача - минимизировать это отношение, тем самым уменьшая количество цветов.
    
    Args:
        graph: Граф NetworkX для раскраски
        params: Словарь с параметрами (размер популяции и число поколений)
    
    Returns:
        Словарь (вершина: цвет) с оптимальной раскраской графа
    
    Raises:
        RuntimeError: При возникновении ошибок в процессе работы алгоритма
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
