from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets, string
from database import init_db, register_user, verify_user, save_password, get_user_passwords, get_all_users, get_all_passwords

app = Flask(__name__)
app.secret_key = 'simple_secret_key_for_student_project'

init_db()

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    chars = ''
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += '!@#$%^&*_+-='
    if not chars:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        c = request.form['confirm_password']
        if not u or not p:
            flash('Все поля обязательны', 'danger')
        elif len(u) < 3:
            flash('Имя не короче 3 символов', 'danger')
        elif p != c:
            flash('Пароли не совпадают', 'danger')
        elif len(p) < 6:
            flash('Пароль не короче 6 символов', 'danger')
        elif register_user(u, p):
            flash('Успешная регистрация!', 'success')
            return redirect('/login')
        else:
            flash('Такой пользователь уже есть', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        if verify_user(u, p):
            session['username'] = u
            flash('Вход успешен', 'success')
            return redirect('/dashboard')
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        service = request.form['service'].strip()
        if not service:
            flash('Укажите сервис', 'danger')
            return redirect('/dashboard')
        try:
            length = int(request.form.get('length', 12))
            if not (6 <= length <= 64):
                raise ValueError
        except:
            flash('Длина — число от 6 до 64', 'danger')
            return redirect('/dashboard')
        u = 'uppercase' in request.form
        l = 'lowercase' in request.form
        d = 'digits' in request.form
        s = 'special' in request.form
        if not (u or l or d or s):
            flash('Выберите хотя бы один тип символов', 'danger')
            return redirect('/dashboard')
        parts = []
        if u: parts.append('A-Z')
        if l: parts.append('a-z')
        if d: parts.append('0-9')
        if s: parts.append('!@#')
        complexity = ','.join(parts)
        pwd = generate_password(length, u, l, d, s)
        save_password(session['username'], service, pwd, length, complexity)
        flash(f'Пароль для {service} сохранён!', 'success')
        return redirect('/dashboard')
    passwords = get_user_passwords(session['username'])
    return render_template('dashboard.html', passwords=passwords)

@app.route('/admin')
def admin_panel():
    if 'username' not in session or session['username'] != 'admin':
        flash('Только для админа', 'danger')
        return redirect('/dashboard')
    users = get_all_users()
    all_passwords = get_all_passwords()
    return render_template('admin.html', users=users, all_passwords=all_passwords)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)