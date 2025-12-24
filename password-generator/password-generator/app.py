from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets, string
from functools import wraps
from database import init_db, register_user, verify_user, save_password, get_user_passwords, get_all_users, get_all_passwords

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
ADMIN_USERNAME = 'admin'

init_db()

def generate_password(length=12, use_uppercase=True, use_lowercase=True, use_digits=True, use_special=True):
    chars = ''
    if use_uppercase: chars += string.ascii_uppercase
    if use_lowercase: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += '!@#$%^&*_+-='
    if not chars:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Требуется вход в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Требуется вход в систему', 'warning')
            return redirect(url_for('login'))
        if session['username'] != ADMIN_USERNAME:
            flash('Доступно только администратору', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return redirect(url_for('dashboard' if 'username' in session else 'login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not username or not password:
            flash('Все поля обязательны', 'danger')
        elif len(username) < 3:
            flash('Имя должно содержать не менее 3 символов', 'danger')
        elif password != confirm:
            flash('Пароли не совпадают', 'danger')
        elif len(password) < 6:
            flash('Пароль должен быть не короче 6 символов', 'danger')
        elif register_user(username, password):
            flash('Аккаунт успешно создан', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким именем уже существует', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if verify_user(username, password):
            session['username'] = username
            flash('Вход выполнен успешно', 'success')
            return redirect(url_for('dashboard'))
        flash('Неверное имя или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        service = request.form.get('service', '').strip()
        if not service:
            flash('Укажите название сервиса', 'danger')
            return redirect(url_for('dashboard'))
        try:
            length = int(request.form.get('length', 12))
            if not (6 <= length <= 64):
                raise ValueError
        except:
            flash('Длина пароля должна быть от 6 до 64', 'danger')
            return redirect(url_for('dashboard'))
        use_upper = 'uppercase' in request.form
        use_lower = 'lowercase' in request.form
        use_digits = 'digits' in request.form
        use_special = 'special' in request.form
        if not (use_upper or use_lower or use_digits or use_special):
            flash('Выберите хотя бы один набор символов', 'danger')
            return redirect(url_for('dashboard'))
        parts = []
        if use_upper: parts.append('A-Z')
        if use_lower: parts.append('a-z')
        if use_digits: parts.append('0-9')
        if use_special: parts.append('!@#')
        complexity = ','.join(parts) if parts else 'обычный'
        password = generate_password(length, use_upper, use_lower, use_digits, use_special)
        save_password(session['username'], service, password, length, complexity)
        flash(f'Учётные данные для «{service}» созданы и сохранены', 'success')
        return redirect(url_for('dashboard'))
    passwords = get_user_passwords(session['username'])
    return render_template('dashboard.html', passwords=passwords, username=session['username'])

@app.route('/admin')
@admin_required
def admin_panel():
    users = get_all_users()
    all_passwords = get_all_passwords()
    return render_template('admin.html', users=users, all_passwords=all_passwords, username=session['username'])

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.2', port=5000)