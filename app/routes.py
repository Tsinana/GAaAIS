import os
import time
import json
from flask import Blueprint, request, render_template, send_file

from app.algorithms.genetic import genetic_coloring
from app.algorithms.immune import immune_coloring
from app.exact import exact_coloring, compare_solutions
from app.utils import generate_bar_chart, generate_line_chart
import networkx as nx

main = Blueprint('main', __name__)

# Глобальные переменные для истории результатов
global_history_timings = {"Exact": [], "Genetic": [], "Immune": []}
global_history_accuracy = {"Exact": [], "Genetic": [], "Immune": []}

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

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nodes_count = int(request.form.get('nodes_count', 10))
        graph = generate_random_graph(nodes_count)
        
        # Получение параметров для GA и иммунной сети из формы (в формате JSON)
        genetic_params_str = request.form.get('genetic_params', '{}')
        immune_params_str = request.form.get('immune_params', '{}')
        try:
            genetic_params = json.loads(genetic_params_str)
        except Exception:
            genetic_params = {}
        try:
            immune_params = json.loads(immune_params_str)
        except Exception:
            immune_params = {}
        
        solutions = {}
        timings = {}
        
        # Точный алгоритм
        start_time = time.time()
        exact_solution = exact_coloring(graph)
        timings['Exact'] = round(time.time() - start_time, 4)
        solutions['Exact'] = exact_solution
        
        # Генетический алгоритм (заглушка)
        start_time = time.time()
        genetic_solution = genetic_coloring(graph, genetic_params)
        timings['Genetic'] = round(time.time() - start_time, 4)
        solutions['Genetic'] = genetic_solution
        
        # Алгоритм иммунной сети (заглушка)
        start_time = time.time()
        immune_solution = immune_coloring(graph, immune_params)
        timings['Immune'] = round(time.time() - start_time, 4)
        solutions['Immune'] = immune_solution
        
        accuracy = {
            'Exact': 100,
            'Genetic': compare_solutions(exact_solution, genetic_solution),
            'Immune': compare_solutions(exact_solution, immune_solution)
        }
        
        # Сохранение графов для каждого алгоритма
        draw_graph(graph, exact_solution, 'exact_graph.png')
        draw_graph(graph, genetic_solution, 'genetic_graph.png')
        draw_graph(graph, immune_solution, 'immune_graph.png')
        
        # Генерация графиков (бар-чартов) для текущего запуска
        timings_chart = generate_bar_chart(timings, "Execution Time", "Algorithm", "Time (s)")
        accuracy_chart = generate_bar_chart(accuracy, "Accuracy", "Algorithm", "Accuracy (%)")
        
        # Добавление текущих результатов в историю
        for algo in timings:
            global_history_timings[algo].append(timings[algo])
            global_history_accuracy[algo].append(accuracy[algo])
        
        history_timings_chart = generate_line_chart(global_history_timings, "Execution Time History", "Run", "Time (s)")
        history_accuracy_chart = generate_line_chart(global_history_accuracy, "Accuracy History", "Run", "Accuracy (%)")
        
        return render_template('index.html',
                               timings=timings,
                               accuracy=accuracy,
                               timings_chart=timings_chart,
                               accuracy_chart=accuracy_chart,
                               history_timings_chart=history_timings_chart,
                               history_accuracy_chart=history_accuracy_chart)
    
    return render_template('index.html')

@main.route('/graph_image/<algorithm>')
def graph_image(algorithm):
    image_path = os.path.join(GRAPH_DIR, f'{algorithm}_graph.png')
    return send_file(image_path, mimetype='image/png')
