import io
import base64
import matplotlib.pyplot as plt

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
    return base64.b64encode(buf.getvalue()).decode("utf-8")

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
