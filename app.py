from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Read the contents of agents.log if it exists
    log_content = ""
    log_file = "agents.log"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
    # A simple HTML template to display the log contents
    template = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Agents Log</title>
        <style>
          body { font-family: monospace; background-color: #f4f4f4; padding: 20px; }
          pre { background-color: #fff; padding: 10px; border: 1px solid #ddd; }
        </style>
      </head>
      <body>
        <h1>Agents Log</h1>
        <pre>{{ log_content }}</pre>
      </body>
    </html>
    """
    return render_template_string(template, log_content=log_content)

if __name__ == '__main__':
    app.run(debug=True)
