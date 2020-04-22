import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, Response, send_from_directory, abort, send_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user, logout_user
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
load_dotenv()


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USERNAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("No SECRETS set for Flask application")

users = {USERNAME: {'password': PASSWORD}}

login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    user.is_authenticated = request.form['password'] == users[email]['password']

    return user

# check if uploaded filetype is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
@login_required
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

# redirect if user not logged in
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/<path:req_path>')
@login_required
def dir_listing(req_path):

    # Joining the base and the requested path
    abs_path = os.path.join(UPLOAD_FOLDER, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)


@app.route('/uploads', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        # if user does not select file, browser also submits an empty part without filename
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Unsupported file type')
                return redirect(request.url)
        flash('File(s) uploaded successfully')
        return redirect(url_for('index'))
    
    return render_template('uploads.html')


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        login_user(user)
        return redirect(url_for('index'))
    else:
        flash('Incorrect username or password')
        return redirect(url_for('login'))


app.secret_key = os.getenv("SECRET")
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

