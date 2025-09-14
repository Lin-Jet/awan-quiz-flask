from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions
from app import db
import json

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

@app.route('/')
def home():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['marks'] = 0
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    if g.user:
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['marks'] = 0
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    if not g.user:
        return redirect(url_for('login'))
    
    # We will use the form object to render the submit button and the CSRF token.
    form = QuestionForm()


    q = Questions.query.filter_by(id=id).first()
    if not q:
        # If no question is found, redirect to the score page.
        return redirect(url_for('score'))
    
    # We need to load the choices from the stored JSON string.
    q_choices = json.loads(q.choices)

    if request.method == 'POST':
        # Check if the question has a single or multiple correct answers
        is_multi_select = len(q.answer) > 1

        if is_multi_select:
            # For multiple-choice questions, `request.form.getlist` gets a list of selected values
            user_options = request.form.getlist('options')
            user_options.sort() # Sort to ensure consistent comparison
            correct_options = sorted(list(q.answer)) # Sort the correct answer string

            is_correct = (user_options == correct_options)
        else:
            # For single-choice questions, `request.form['options']` gets the single selected value
            user_option = request.form['options']
            is_correct = (user_option == q.answer)

        if is_correct:
            session['marks'] = session.get('marks', 0) + 1
            flash('Correct! Your score is now {}'.format(session['marks']), 'success')
        else:
            flash('Incorrect. The correct answer was {}'.format(q.answer), 'danger')

        return redirect(url_for('question', id=(id + 1)))

    # Determine if we should render radio buttons or checkboxes
    is_multi_select = len(q.answer) > 1
    
    return render_template('question.html', form=form, q=q, choices=q_choices, is_multi_select=is_multi_select, title='Question {}'.format(id))


@app.route('/score')
def score():
    if not g.user:
        return redirect(url_for('login'))
    g.user.marks = session['marks']
    # db.session.commit()
    return render_template('score.html', title='Final Score')

@app.route('/logout')
def logout():
    if not g.user:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('marks', None)
    return redirect(url_for('home'))
