from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Open the log file with 'errors="replace"' to handle any encoding issues
        with open("agents.log", "r", encoding="utf-8", errors="replace") as f:
            log_content = f.read()
    except FileNotFoundError:
        log_content = "Log file not found."
    except Exception as e:
        log_content = f"Error reading log file: {e}"

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agent Log Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4; }
            h1 { color: #333; }
            pre { background: #fff; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
            .container { max-width: 800px; margin: auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Agent Log Viewer</h1>
            <pre>{{ log_content }}</pre>
        </div>
    </body>
    </html>
    """

    return render_template_string(html_template, log_content=log_content)

if __name__ == '__main__':
    app.run(debug=True)
