from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets, string, os, datetime

app = Flask(__name__)
app.secret_key = 'simple_secret_key_for_User_project'

USERS_FILE = 'users.txt'
PASSWORDS_FILE = 'passwords.txt'

# ==================== РАБОТА С .txt ФАЙЛАМИ ====================
def init_txt_db():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            f.write('admin|admin\n')
    if not os.path.exists(PASSWORDS_FILE):
        open(PASSWORDS_FILE, 'w', encoding='utf-8').close()

def read_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    u, p = line.split('|', 1)
                    users[u] = p
    return users

def register_user(username, password):
    users = read_users()
    if username in users:
        return False
    users[username] = password
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        for u, p in users.items():
            f.write(f"{u}|{p}\n")
    return True

def verify_user(username, password):
    return read_users().get(username) == password

def read_passwords(username=None):
    passwords = []
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split('|')
                if len(parts) == 6:
                    entry = {
                        'username': parts[0], 'service': parts[1],
                        'password': parts[2], 'length': parts[3],
                        'complexity': parts[4], 'timestamp': parts[5]
                    }
                    if username is None or entry['username'] == username:
                        passwords.append(entry)
    return passwords

def save_password(username, service, password, length, complexity):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PASSWORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}|{service}|{password}|{length}|{complexity}|{timestamp}\n")

def get_all_users():
    return list(read_users().keys())

def get_all_passwords():
    return read_passwords()

# ==================== ГЕНЕРАТОР ====================
def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    chars = ''
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += '!@#$%^&*_+-='
    if not chars: chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# ==================== РОУТЫ ====================
@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
        c = request.form.get('confirm_password', '')
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
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
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
        service = request.form.get('service', '').strip()
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

    passwords = read_passwords(session['username'])
    passwords.reverse() # Новейшие сверху, как в оригинале
    return render_template('dashboard.html', passwords=passwords)

@app.route('/admin')
def admin_panel():
    if 'username' not in session or session['username'] != 'admin':
        flash('Только для админа', 'danger')
        return redirect('/dashboard')
    users = get_all_users()
    all_passwords = get_all_passwords()
    all_passwords.reverse()
    return render_template('admin.html', users=users, all_passwords=all_passwords)

if __name__ == '__main__':
    init_txt_db()
    app.run(host='0.0.0.0', port=5000, debug=True)