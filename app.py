from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import datetime
import matplotlib.pyplot as plt
import uuid
import tkinter as tk
from PIL import Image, ImageDraw
from multiprocessing import Process, Manager

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

STATS_FILE = 'stats.txt'

executors1 = {
    'js': 'node {file}',
    'py': 'python {file}',
    'py3': 'python3 {file}',
    'rb': 'ruby {file}',
    'java': 'javac {file} && java TempCode',
    'go': 'go run {file}',
    'php': 'php {file}',
    'pl': 'perl {file}',
}

executors = {
    'Node.js': 'node --version',
    'Python': 'python --version',
    'Python3': 'python3 --version',
    'Ruby': 'ruby --version',
    'Java': 'java -version',
    'Go': 'go version',
    'PHP': 'php --version',
    'Perl': 'perl -v',
}

def read_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w') as f:
            f.write('start_date=2024-07-01\ndays_running=0\nvisits=0\nexecutions=0\n')
    stats = {}
    with open(STATS_FILE, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            stats[key] = value
    return stats

def write_stats(stats):
    with open(STATS_FILE, 'w') as f:
        for key, value in stats.items():
            f.write(f'{key}={value}\n')

def update_stats(stat_name):
    stats = read_stats()
    stats[stat_name] = str(int(stats[stat_name]) + 1)
    stats['days_running'] = str((datetime.date.today() - datetime.datetime.strptime(stats['start_date'], '%Y-%m-%d').date()).days)
    write_stats(stats)

def check_executor(name, command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            return result.stdout.strip() or result.stderr.strip()
        else:
            return None
    except Exception as e:
        return None

def create_plot(shared_dict):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    plt.savefig(filepath)
    plt.close(fig)
    shared_dict['filename'] = filename

def create_tkinter_plot(shared_dict):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    width, height = 200, 200
    image = Image.new('RGB', (width, height), color = 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle([50, 50, 150, 150], outline='black', fill='blue')
    draw.ellipse([50, 50, 150, 150], outline='red', fill='green')
    
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    shared_dict['filename'] = filename

@app.route('/')
def index():
    update_stats('visits')
    return render_template('index.html')

@app.route('/check_executors', methods=['GET'])
def check_executors():
    results = {}
    for name, command in executors.items():
        version = check_executor(name.split()[0], command.format(file=''))
        if version:
            results[name] = version.split('\n')[0]  # 只显示第一行
    return jsonify(results)

@app.route('/execute_code', methods=['POST'])
def execute_code():
    data = request.get_json()
    language = data['language']
    code = data['code']
    
    temp_file = f'temp_code.{language}'
    if language == 'python':
        temp_file = 'temp_code.py'
        run_command = f'python {temp_file}'
    elif language == 'node':
        temp_file = 'temp_code.js'
        run_command = f'node {temp_file}'
    elif language == 'java':
        temp_file = 'TempCode.java'
        run_command = f'javac {temp_file} && java TempCode'
    elif language == 'php':
        temp_file = 'temp_code.php'
        run_command = f'php {temp_file}'
    else:
        return jsonify({'error': 'Unsupported language'}), 400
    
    with open(temp_file, 'w', encoding='utf-8') as file:
        file.write(code)
    
    try:
        result = subprocess.run(run_command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout if result.returncode == 0 else result.stderr
        filename = None

        if 'import matplotlib' in code or 'from matplotlib' in code:
            with Manager() as manager:
                shared_dict = manager.dict()
                p = Process(target=create_plot, args=(shared_dict,))
                p.start()
                p.join()
                filename = shared_dict.get('filename')
        elif 'import tkinter' in code or 'from tkinter' in code:
            with Manager() as manager:
                shared_dict = manager.dict()
                p = Process(target=create_tkinter_plot, args=(shared_dict,))
                p.start()
                p.join()
                filename = shared_dict.get('filename')
    except Exception as e:
        output = str(e)
        filename = None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    update_stats('executions')
    return jsonify({'output': output, 'filename': filename})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_ext = file.filename.rsplit('.', 1)[-1].lower()
    if file_ext not in executors1:
        return jsonify({'error': f'Unsupported file type: .{file_ext}'}), 400

    temp_file = f'temp_code.{file_ext}'
    file.save(temp_file)

    run_command = executors1[file_ext].format(file=temp_file)
    
    try:
        result = subprocess.run(run_command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout if result.returncode == 0 else result.stderr
        filename = None

        if 'import matplotlib' in file.read().decode('utf-8') or 'from matplotlib' in file.read().decode('utf-8'):
            with Manager() as manager:
                shared_dict = manager.dict()
                p = Process(target=create_plot, args=(shared_dict,))
                p.start()
                p.join()
                filename = shared_dict.get('filename')
        elif 'import tkinter' in file.read().decode('utf-8') or 'from tkinter' in file.read().decode('utf-8'):
            with Manager() as manager:
                shared_dict = manager.dict()
                p = Process(target=create_tkinter_plot, args=(shared_dict,))
                p.start()
                p.join()
                filename = shared_dict.get('filename')
    except Exception as e:
        output = str(e)
        filename = None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    update_stats('executions')
    return jsonify({'output': output, 'filename': filename})

@app.route('/stats', methods=['GET'])
def get_stats():
    stats = read_stats()
    return jsonify(stats)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except SystemExit:
        pass
