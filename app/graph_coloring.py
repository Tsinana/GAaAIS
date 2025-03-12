import os
import networkx as nx
import matplotlib.pyplot as plt

class GraphColoring:
    def exact_coloring(self, graph):
        """Реализация точного алгоритма раскраски графа с использованием жадного алгоритма."""
        coloring = nx.greedy_color(graph, strategy='largest_first')
        return coloring

    def genetic_coloring(self, graph, params):
        """Заглушка для генетического алгоритма.
        Здесь можно использовать параметры из params (например, population_size, mutation_rate и т.д.)
        """
        return {node: 0 for node in graph.nodes}

    def immune_coloring(self, graph, params):
        """Заглушка для алгоритма иммунной сети.
        Здесь можно использовать параметры из params (например, количество антител, скорость мутации и т.д.)
        """
        return {node: 0 for node in graph.nodes}

    def compare_solutions(self, exact, test):
        """
        Возвращает точность тестового решения как отношение минимального числа цветов,
        использованных алгоритмами, к максимальному числу цветов, умноженное на 100.
        Результат округляется до двух знаков после запятой.
        """
        exact_colors = len(set(exact.values()))
        test_colors = len(set(test.values()))
        min_colors = min(exact_colors, test_colors)
        max_colors = max(exact_colors, test_colors)
        return round((min_colors / max_colors) * 100, 2) if max_colors != 0 else 0

def generate_random_graph(nodes_count):
    """Генерирует случайный граф с заданным количеством узлов."""
    prob = 0.3
    return nx.gnp_random_graph(nodes_count, prob)

def draw_graph(graph, coloring, filename):
    """Отрисовывает граф с раскраской и сохраняет его в файл.
    Файл сохраняется по заданному пути filename.
    """
    colors = [coloring[node] for node in graph.nodes]
    plt.figure(figsize=(8, 6))
    nx.draw(graph, node_color=colors, with_labels=True, cmap=plt.cm.jet)
    plt.savefig(filename)
    plt.close()
