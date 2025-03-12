import networkx as nx

def exact_coloring(graph):
    """
    Реализация точного алгоритма раскраски графа с использованием жадного алгоритма.
    """
    coloring = nx.greedy_color(graph, strategy='largest_first')
    return coloring

def compare_solutions(exact, test):
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
