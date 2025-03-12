import os
import time
import json
from flask import Blueprint, request, render_template, send_file
from app.graph_coloring import GraphColoring, generate_random_graph, draw_graph
from app.utils import generate_bar_chart, generate_line_chart

main = Blueprint('main', __name__)

# Глобальные переменные для истории результатов
global_history_timings = {"Exact": [], "Genetic": [], "Immune": []}
global_history_accuracy = {"Exact": [], "Genetic": [], "Immune": []}

# Директория для сохранения графов (png)
GRAPH_DIR = os.path.join(os.getcwd(), 'graphs')
os.makedirs(GRAPH_DIR, exist_ok=True)

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
        
        gc = GraphColoring()
        solutions = {}
        timings = {}
        
        # Точный алгоритм
        start_time = time.time()
        exact_solution = gc.exact_coloring(graph)
        timings['Exact'] = round(time.time() - start_time, 4)
        solutions['Exact'] = exact_solution
        
        # Генетический алгоритм (заглушка)
        start_time = time.time()
        genetic_solution = gc.genetic_coloring(graph, genetic_params)
        timings['Genetic'] = round(time.time() - start_time, 4)
        solutions['Genetic'] = genetic_solution
        
        # Алгоритм иммунной сети (заглушка)
        start_time = time.time()
        immune_solution = gc.immune_coloring(graph, immune_params)
        timings['Immune'] = round(time.time() - start_time, 4)
        solutions['Immune'] = immune_solution
        
        accuracy = {
            'Exact': 100,
            'Genetic': gc.compare_solutions(exact_solution, genetic_solution),
            'Immune': gc.compare_solutions(exact_solution, immune_solution)
        }
        
        # Сохранение графов в директории GRAPH_DIR
        draw_graph(graph, exact_solution, os.path.join(GRAPH_DIR, 'exact_graph.png'))
        draw_graph(graph, genetic_solution, os.path.join(GRAPH_DIR, 'genetic_graph.png'))
        draw_graph(graph, immune_solution, os.path.join(GRAPH_DIR, 'immune_graph.png'))
        
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
