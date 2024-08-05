from flask import Flask, request, redirect, url_for, render_template
import requests
import re, ast

app = Flask(__name__)

# Regular expression pattern to match the components
pattern = re.compile(r"\[(.*?)\] \[(.*?)\] \[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})\] (.*?): (.*)")

def convert_to_dict(dict_string):
    try:
        # Attempt to convert the string to a dictionary
        result = ast.literal_eval(dict_string)
        if isinstance(result, dict):
            return result
        else:
            return False
    except (ValueError, SyntaxError):
        # Return False if there's a ValueError or SyntaxError
        return False

def process_string(string):
    match = pattern.match(string)
    if match:
        components = list(match.groups())
        user_field = components[4].split('#')[0]
        components[4] = user_field
        convert = convert_to_dict(components[5])
        if convert:
            components[5] = f':{convert['name']}:'
        return {
            "channel": components[0],
            "id": components[1],
            "date": components[2],
            "time": components[3],
            "user": components[4],
            "message": components[5]
        }
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if 'zeppelin.gg' in url:
            return redirect(url_for('display_messages', url=url))
        else:
            return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    return render_template('index.html')

@app.route('/messages')
def display_messages():
    url = request.args.get('url')
    if not url:
        return redirect(url_for('index'))

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch data from the URL: {e}"

    data = response.text.split('\n')[2:-3]
    creation_date = response.text.split('\n')[-2]
    processed_data = [process_string(d) for d in data if process_string(d)]

    return render_template('display.html', data=processed_data, channel_name=processed_data[0]['channel'], creation_date=creation_date)

if __name__ == '__main__':
    app.run(debug=True)
