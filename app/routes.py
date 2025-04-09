import os
import time
import json
from flask import Blueprint, request, render_template, send_file

from app.algorithms.genetic import genetic_coloring
from app.algorithms.immune import immune_coloring
from app.exact import exact_coloring, compare_solutions, get_count_colors, null_coloring, greedy_coloring
from app.utils import generate_line_chart
import networkx as nx

main = Blueprint('main', __name__)

# Глобальные переменные для истории результатов
global_history_timings = {}
global_history_accuracy = {}
global_colors_chart = {}
# Глобальная переменная для хранения количества вершин в каждом запуске
global_nodes_count = []

# Директория для сохранения графов (png)
GRAPH_DIR = os.path.join(os.getcwd(), 'graphs')
os.makedirs(GRAPH_DIR, exist_ok=True)

def generate_random_graph(nodes_count):
    """Генерирует случайный граф с заданным количеством узлов."""
    prob = 0.3
    return nx.gnp_random_graph(nodes_count, prob)

def draw_graph(graph, coloring, filename):
    """Отрисовывает граф с раскраской и сохраняет его в файл."""
    import matplotlib.pyplot as plt
    colors = [coloring[node] for node in graph.nodes]
    plt.figure(figsize=(8, 6))
    nx.draw(graph, node_color=colors, with_labels=True, cmap=plt.cm.jet)
    file_path = os.path.join(GRAPH_DIR, filename)
    plt.savefig(file_path)
    plt.close()

def generate_custom_line_chart(history_data, nodes_counts, title, xlabel, ylabel):
    """
    Генерирует линейный график с использованием количества вершин по оси X.
    """
    import matplotlib.pyplot as plt
    import io
    import base64
    
    plt.figure()
    for algo, values in history_data.items():
        if len(values) > 0:  # Проверяем, что массив значений не пустой
            plt.plot(nodes_counts[-len(values):], values, marker='o', label=algo)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def run_coloring_algorithms(nodes_count, use_greedy=False):
    """
    Запускает алгоритмы раскраски графа с заданным количеством вершин.
    Возвращает результаты и обновляет глобальные данные истории.
    
    Args:
        nodes_count (int): Количество вершин в графе.
        use_greedy (bool): Использовать жадный алгоритм вместо точного.
    """
    # Вывод информации о количестве вершин в текущей задаче
    print(f">>> Обработка графа с {nodes_count} вершинами...")
    
    graph = generate_random_graph(nodes_count)
    
    # Пустые параметры для алгоритмов
    genetic_params = {}
    immune_params = {}
    
    solutions = {}
    timings = {}
    
    # Выбор алгоритма раскраски (точный или жадный)
    coloring_algorithm = greedy_coloring if use_greedy else exact_coloring
    algorithm_name = "Greedy" if use_greedy else "Exact"
    
    # Запуск выбранного алгоритма
    start_time = time.time()
    exact_solution = coloring_algorithm(graph)
    timings[algorithm_name] = round(time.time() - start_time, 4)
    solutions[algorithm_name] = exact_solution

    # Генетический алгоритм
    start_time = time.time()
    genetic_solution = genetic_coloring(graph, genetic_params)
    timings['Genetic'] = round(time.time() - start_time, 4)
    solutions['Genetic'] = genetic_solution

    # Алгоритм иммунной сети
    start_time = time.time()
    immune_solution = immune_coloring(graph, immune_params)
    timings['Immune'] = round(time.time() - start_time, 4)
    solutions['Immune'] = immune_solution

    accuracy = {
        algorithm_name: 100,
        'Genetic': compare_solutions(exact_solution, genetic_solution),
        'Immune': compare_solutions(exact_solution, immune_solution)
    }
    
    colors = {
        algorithm_name: get_count_colors(exact_solution),
        'Genetic': get_count_colors(genetic_solution),
        'Immune': get_count_colors(immune_solution)
    }
    
    # Сохранение графов для каждого алгоритма
    draw_graph(graph, exact_solution, f'{algorithm_name.lower()}_graph.png')
    draw_graph(graph, genetic_solution, 'genetic_graph.png')
    draw_graph(graph, immune_solution, 'immune_graph.png')
    
    # Добавление текущих результатов в историю
    for algo in timings:
        if algo not in global_history_timings:
            global_history_timings[algo] = []
            global_history_accuracy[algo] = []
            global_colors_chart[algo] = []
        
        global_history_timings[algo].append(timings[algo])
        global_history_accuracy[algo].append(accuracy[algo])
        global_colors_chart[algo].append(colors[algo])
    
    # Добавляем количество вершин в историю
    global_nodes_count.append(nodes_count)
    
    return timings, accuracy, colors

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        run_mode = request.form.get('run_mode', 'single')
        use_greedy = request.form.get('use_greedy') == 'true'
        
        if use_greedy:
            print(">>> Используется жадный алгоритм вместо точного")
        
        if run_mode == 'single':
            # Режим одиночного запуска
            nodes_count = int(request.form.get('nodes_count', 10))
            print(f">>> Режим одиночного запуска с {nodes_count} вершинами")
            timings, accuracy, colors = run_coloring_algorithms(nodes_count, use_greedy)
        else:
            # Режим с предустановленными значениями вершин
            node_presets = request.form.getlist('node_preset')
            
            # Если ничего не выбрано, используем стандартный набор
            if not node_presets:
                node_presets = ['10', '15', '20']
                
            print(f">>> Режим пресетов. Выбрано {len(node_presets)} графов с вершинами: {', '.join(node_presets)}")
            
            # Запускаем алгоритмы для каждого выбранного количества вершин
            latest_results = None
            for preset in node_presets:
                nodes_count = int(preset)
                latest_results = run_coloring_algorithms(nodes_count, use_greedy)
            
            # Используем результаты последнего запуска для отображения
            if latest_results:
                timings, accuracy, colors = latest_results
            else:
                # Если что-то пошло не так, вернемся на начальную страницу
                return render_template('index.html')
        
        # Генерация графиков истории с использованием количества вершин по оси X
        history_timings_chart = generate_custom_line_chart(
            global_history_timings, 
            global_nodes_count, 
            "Execution Time History", 
            "Number of Nodes", 
            "Time (s)"
        )
        history_accuracy_chart = generate_custom_line_chart(
            global_history_accuracy, 
            global_nodes_count, 
            "Accuracy History", 
            "Number of Nodes", 
            "Accuracy (%)"
        )
        history_colors_chart = generate_custom_line_chart(
            global_colors_chart, 
            global_nodes_count, 
            "Colors History", 
            "Number of Nodes", 
            "Count"
        )
        
        return render_template('index.html',
                               timings=timings,
                               accuracy=accuracy,
                               colors=colors,
                               history_timings_chart=history_timings_chart,
                               history_accuracy_chart=history_accuracy_chart,
                               history_colors_chart=history_colors_chart)
    
    return render_template('index.html')

@main.route('/graph_image/<algorithm>')
def graph_image(algorithm):
    image_path = os.path.join(GRAPH_DIR, f'{algorithm}_graph.png')
    return send_file(image_path, mimetype='image/png')
