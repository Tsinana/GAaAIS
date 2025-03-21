from itertools import permutations

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

def get_count_colors(graph):
    return len(set(graph.values()))

def null_coloring(graph):
    return {node: 0 for node in graph.nodes}

def exact_coloring(graph):
    """
    Реализация точного переборного алгоритма раскраски графа для нахождения минимальной
    расскраски. Алгоритм перебирает возможные варианты раскраски с 1 до N цветов (где N —
    количество вершин) с использованием рекурсивного алгоритма backtracking.

    Алгоритм работает следующим образом:
    1. Использует рекурсивную функцию backtracking для назначения цвета каждой вершине.
    2. Проверяет, что выбранный цвет не конфликтует с цветами соседних вершин.
    3. Итеративно увеличивает количество используемых цветов, пока не будет найдено
       корректное решение с минимальным числом цветов.

    Args:
        graph (networkx.Graph): Граф, который необходимо раскрасить.

    Returns:
        dict: Словарь, где ключ — вершина, а значение — назначенный ей цвет (целое число).

    Raises:
        Exception: Если не удалось найти корректную раскраску графа.
    """
    try:
        # Получение списка вершин
        nodes = list(graph.nodes())
        
        def is_valid_assignment(node, color, current_assignment):
            """
            Проверяет, можно ли назначить вершине 'node' цвет 'color'
            без конфликта с соседями.

            Args:
                node: Текущая вершина.
                color (int): Предполагаемый цвет для вершины.
                current_assignment (dict): Текущее частичное назначение цветов.

            Returns:
                bool: True, если назначение допустимо, иначе False.
            """
            for neighbor in graph.neighbors(node):
                if neighbor in current_assignment and current_assignment[neighbor] == color:
                    return False
            return True
        
        def backtrack(current_assignment, max_colors):
            """
            Рекурсивная функция backtracking для назначения цветов вершинам.

            Args:
                current_assignment (dict): Текущее частичное назначение цветов.
                max_colors (int): Максимальное число цветов, доступных для назначения.

            Returns:
                dict or None: Полное назначение, если найдено корректное решение, иначе None.
            """
            # Если все вершины раскрашены, возвращаем найденное решение.
            if len(current_assignment) == len(nodes):
                return current_assignment
            
            # Выбираем следующую незакрашенную вершину.
            for node in nodes:
                if node not in current_assignment:
                    current_node = node
                    break
            
            # Перебор возможных цветов для текущей вершины.
            for color in range(max_colors):
                if is_valid_assignment(current_node, color, current_assignment):
                    current_assignment[current_node] = color  # Назначаем цвет.
                    result = backtrack(current_assignment, max_colors)
                    if result is not None:
                        return result
                    # Отмена назначения цвета в случае неудачи (backtracking).
                    del current_assignment[current_node]
            return None
        
        # Итеративный перебор количества цветов от 1 до количества вершин.
        for num_colors in range(1, len(nodes) + 1):
            print(num_colors)
            assignment = {}
            result = backtrack(assignment, num_colors)
            if result is not None:
                # Возвращаем раскраску, использующую минимальное число цветов.
                return result
        
        raise Exception("Не удалось найти корректную раскраску графа.")
    
    except Exception as error:
        # Обработка исключений с информативным сообщением об ошибке.
        raise Exception(f"Ошибка в функции exact_coloring: {error}")