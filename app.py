from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form.get('empcode').strip().lower()
        filename = f"{code}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(filepath):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            return render_template('index.html', error="No file found for this employee code.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)