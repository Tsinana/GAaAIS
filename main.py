import os
import time
import io
import json
import base64
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)

# Директория для сохранения графов
GRAPH_DIR = 'graphs'
os.makedirs(GRAPH_DIR, exist_ok=True)

# Глобальные переменные для накопления истории результатов
global_history_timings = {"Exact": [], "Genetic": [], "Immune": []}
global_history_accuracy = {"Exact": [], "Genetic": [], "Immune": []}

# Алгоритмы раскраски графа
class GraphColoring:
    def exact_coloring(self, graph):
        """Реализация точного алгоритма раскраски графа с использованием жадного алгоритма."""
        coloring = nx.greedy_color(graph, strategy='largest_first')
        return coloring
    
    def genetic_coloring(self, graph, params):
        """Заглушка для генетического алгоритма.
        Здесь можно использовать переданные параметры (например, population_size, mutation_rate и т.д.)
        """
        # Здесь можно добавить обработку параметров из params
        return {node: 0 for node in graph.nodes}
    
    def immune_coloring(self, graph, params):
        """Заглушка для алгоритма иммунной сети.
        Здесь можно использовать переданные параметры (например, количество антител, скорость мутации и т.д.)
        """
        # Здесь можно добавить обработку параметров из params
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

graph_coloring = GraphColoring()

def generate_random_graph(nodes_count):
    """Генерирует случайный граф с заданным количеством узлов."""
    prob = 0.3
    return nx.gnp_random_graph(nodes_count, prob)

def draw_graph(graph, coloring, filename):
    """Отрисовывает граф с раскраской и сохраняет его в файл."""
    colors = [coloring[node] for node in graph.nodes]
    plt.figure(figsize=(8, 6))
    nx.draw(graph, node_color=colors, with_labels=True, cmap=plt.cm.jet)
    file_path = os.path.join(GRAPH_DIR, filename)
    plt.savefig(file_path)
    plt.close()

def generate_bar_chart(data, title, xlabel, ylabel):
    """
    Генерирует бар-чарт по данным словаря data и возвращает изображение в формате base64.
    :param data: словарь (например, {'Exact': 0.01, 'Genetic': 0.51, ...})
    """
    plt.figure()
    keys = list(data.keys())
    values = list(data.values())
    plt.bar(keys, values, color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return chart_data

def generate_line_chart(history_data, title, xlabel, ylabel):
    """
    Генерирует линейный график по накопленным данным из history_data
    и возвращает изображение в формате base64.
    :param history_data: словарь вида {'Exact': [v1, v2, ...], ...}
    """
    plt.figure()
    for algo, values in history_data.items():
        plt.plot(range(1, len(values) + 1), values, marker='o', label=algo)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Graph Coloring Results</title>
</head>
<body>
    <h1>Graph Coloring Results</h1>
    <p><strong>Timings (seconds):</strong> {{ timings }}</p>
    <p><strong>Accuracy (%):</strong> {{ accuracy }}</p>
    <h2>Current Run Charts</h2>
    <h3>Timings Chart</h3>
    <img src="data:image/png;base64,{{ timings_chart }}" alt="Timings Chart">
    <h3>Accuracy Chart</h3>
    <img src="data:image/png;base64,{{ accuracy_chart }}" alt="Accuracy Chart">

    <h2>History Charts</h2>
    <h3>Execution Time History</h3>
    <img src="data:image/png;base64,{{ history_timings_chart }}" alt="History Timings Chart">
    <h3>Accuracy History</h3>
    <img src="data:image/png;base64,{{ history_accuracy_chart }}" alt="History Accuracy Chart">

    {% for alg in timings %}
        <h2>{{ alg }} Algorithm Graph</h2>
        <img src="/graph_image/{{ alg.lower() }}" alt="{{ alg }} graph">
    {% endfor %}
    <br><a href="/">Generate another graph</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nodes_count = int(request.form.get('nodes_count', 10))
        graph = generate_random_graph(nodes_count)
        
        # Получаем параметры для GA и иммунной сети из формы
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
        exact_solution = graph_coloring.exact_coloring(graph)
        timings['Exact'] = round(time.time() - start_time, 4)
        solutions['Exact'] = exact_solution
        
        # Генетический алгоритм (заглушка)
        start_time = time.time()
        genetic_solution = graph_coloring.genetic_coloring(graph, genetic_params)
        timings['Genetic'] = round(time.time() - start_time, 4)
        solutions['Genetic'] = genetic_solution
        
        # Алгоритм иммунной сети (заглушка)
        start_time = time.time()
        immune_solution = graph_coloring.immune_coloring(graph, immune_params)
        timings['Immune'] = round(time.time() - start_time, 4)
        solutions['Immune'] = immune_solution
        
        accuracy = {
            'Exact': 100,
            'Genetic': graph_coloring.compare_solutions(exact_solution, genetic_solution),
            'Immune': graph_coloring.compare_solutions(exact_solution, immune_solution),
        }
        
        # Сохраняем графы для каждого алгоритма
        draw_graph(graph, exact_solution, 'exact_graph.png')
        draw_graph(graph, genetic_solution, 'genetic_graph.png')
        draw_graph(graph, immune_solution, 'immune_graph.png')
        
        # Генерация графиков (бар-чартов) для текущего запуска
        timings_chart = generate_bar_chart(timings, "Execution Time", "Algorithm", "Time (s)")
        accuracy_chart = generate_bar_chart(accuracy, "Accuracy", "Algorithm", "Accuracy (%)")
        
        # Добавляем текущие результаты в историю
        for algo in timings:
            global_history_timings[algo].append(timings[algo])
            global_history_accuracy[algo].append(accuracy[algo])
        
        # Генерация графиков истории
        history_timings_chart = generate_line_chart(global_history_timings, "Execution Time History", "Run", "Time (s)")
        history_accuracy_chart = generate_line_chart(global_history_accuracy, "Accuracy History", "Run", "Accuracy (%)")
        
        return render_template_string(
            HTML_TEMPLATE,
            timings=timings,
            accuracy=accuracy,
            timings_chart=timings_chart,
            accuracy_chart=accuracy_chart,
            history_timings_chart=history_timings_chart,
            history_accuracy_chart=history_accuracy_chart
        )
    
    return '''
    <form method="post">
        Number of nodes: <input type="number" name="nodes_count" value="10"><br>
        Genetic parameters (JSON): <input type="text" name="genetic_params" value="{}"><br>
        Immune parameters (JSON): <input type="text" name="immune_params" value="{}"><br>
        <input type="submit" value="Generate">
    </form>
    '''

@app.route('/graph_image/<algorithm>')
def graph_image(algorithm):
    image_path = os.path.join(GRAPH_DIR, f'{algorithm}_graph.png')
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
