from flask import Flask, render_template, request, redirect, flash
import secrets, string

app = Flask(__name__)
app.secret_key = 'simple_secret_key_for_User_project'


def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    chars = ''
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += '!@#$%^&*_+-='
    if not chars:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


@app.route('/', methods=['GET', 'POST'])
def index():
    generated_password = None
    if request.method == 'POST':
        try:
            length = int(request.form.get('length', 12))
            if not (6 <= length <= 64):
                raise ValueError
        except:
            flash('Длина — число от 6 до 64', 'danger')
            return redirect('/')

        u = 'uppercase' in request.form
        l = 'lowercase' in request.form
        d = 'digits' in request.form
        s = 'special' in request.form

        if not (u or l or d or s):
            flash('Выберите хотя бы один тип символов', 'danger')
            return redirect('/')

        generated_password = generate_password(length, u, l, d, s)

    return render_template('dashboard.html', generated_password=generated_password)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)