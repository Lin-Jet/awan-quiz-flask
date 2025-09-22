from app import app
from flask import render_template, request, redirect, url_for, session, g, flash
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm, CATEGORY_MAP, CAT_LIST
from app.models import User, Questions, User_Interactions
from app import db
from sqlalchemy import func
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
        session['total_score'] = 0
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
        session['total_score'] = 0
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

# New route to determine the starting question
@app.route('/start_quiz')
def start_quiz():
    if not g.user:
        return redirect(url_for('login'))
    
    # Find the last question the user answered
    last_answered_id = db.session.query(func.max(User_Interactions.question_id)).filter_by(user_id=g.user.id).scalar()
    
    # The next question will be the last one answered's ID + 1.
    # The question() route expects a 1-based index, and our database is 0-based.
    if last_answered_id is not None:
        next_question_id = last_answered_id + 1
    else:
        # For new users, or users who haven't started, begin at the first question (id=0).
        next_question_id = 0
    
    # Check if this question exists.
    question_exists = Questions.query.filter_by(id=next_question_id).first()
    
    if question_exists:
        # Redirect to the question, adjusting for the 1-based URL
        return redirect(url_for('question', id=(next_question_id + 1)))
    else:
        # If no more questions, redirect to the score page.
        return redirect(url_for('score'))


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    id = id-1 # database is zero-index, the questions id will be 1 indexed...
    

    if not g.user:
        return redirect(url_for('login'))
    
    # We will use the form object to render the submit button and the CSRF token.
    form = QuestionForm()

    # # Correctly set the choices for the SelectMultipleField using .items()
    # form.category.choices = list(CATEGORY_MAP.items())
    
    q = Questions.query.filter_by(id=id).first()

    total_questions = Questions.query.count()
    if not q:
        # If no question is found, redirect to the score page.
        return redirect(url_for('score'))
    
    # We need to load the choices from the stored JSON string.
    q_choices = json.loads(q.choices)

    # Correctly set the choices for the SelectMultipleField using .items()
    # It's better to do this here before validation.
    form.options.choices = list(q_choices.items())
    form.category.choices = list(CATEGORY_MAP.items())

    print("is form valid on submit: ", form.validate_on_submit())
    if form.validate_on_submit():
        # Check if the question has a single or multiple correct answers
        is_multi_select = len(q.answer) > 1
        is_correct = False
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
            session['total_score'] = session.get('total_score', 0) + 1
            # flash('Correct! Explanation: {} Your score is now {}'.format(q.explanation, session['total_score']), 'success')
        # else:
            # flash('Incorrect. The correct answer was {} Explanation: {}'.format(q.answer, q.explanation), 'danger')

        # # Save the selected category to the current question's database entry
        # print("Current id: ", id)
        # selected_category = form.category.data
        # print("selected_category: ", selected_category)
        # category_str = CATEGORY_MAP.get(selected_category)
        # print("category_str: ", category_str)
        # q.category = category_str
        # db.session.commit()

        interaction = User_Interactions.query.filter_by(user_id=g.user.id, question_id=q.id).first()
        if not interaction:
            interaction = User_Interactions(user_id=g.user.id, question_id=q.id)
            db.session.add(interaction)
        
        interaction.correctness = 1 if is_correct else 0

        # Retrieve the individual question time from the hidden form field
        individual_question_time = request.form.get('individual_question_time')
        interaction.individual_question_time = float(individual_question_time) if individual_question_time else 0
        
        # Retrieve the stopped for time from the hidden form field
        stopped_for_time = request.form.get('stopped_for_time')
        interaction.stopped_for = float(stopped_for_time) if stopped_for_time else 0 

        selected_categories = request.form.getlist('category')
        category_list_str = ','.join(sorted(selected_categories))
        print("category lsit string: ", category_list_str)
        interaction.selected_category = category_list_str


        print("form.difficulty.data: ", form.difficulty.data)
        interaction.selected_difficulty = form.difficulty.data 

        is_flagged = request.form.get('is_flagged')
        print("is_flagged: ", is_flagged)
        interaction.is_flagged = 1 if is_flagged else 0

        db.session.commit()

        next_question = Questions.query.filter(Questions.id > q.id).order_by(Questions.id).first()
        
        if next_question:
            # return redirect(url_for('question', id=(id + 2)))
            return redirect(url_for('question', id=(next_question.id+1)))
        else:
            return redirect(url_for('score'))

    # Determine if we should render radio buttons or checkboxes
    is_multi_select = len(q.answer) > 1

    is_multi_select_txt = "(多选题)" if is_multi_select else "(单选题)"
    
    print("is_multi_select_txt: ", is_multi_select_txt)

    return render_template('question.html', form=form, score=session['total_score'], total_questions=total_questions, is_multi_select_txt=is_multi_select_txt, q=q, choices=q_choices, is_multi_select=is_multi_select, 
                           title='問題 {}'.format(id), categories=CATEGORY_MAP, descriptions=json.dumps(CAT_LIST))


@app.route('/score')
def score():
    if not g.user:
        return redirect(url_for('login'))
    
    correct_count = User_Interactions.query.filter_by(user_id=g.user.id, correctness=1).count()
    total_answered = User_Interactions.query.filter_by(user_id=g.user.id).count()
    
    total_time = db.session.query(func.sum(User_Interactions.individual_question_time)).filter_by(user_id=g.user.id).scalar()
    
    g.user.total_score = correct_count
    g.user.total_answered = total_answered
    g.user.total_time = total_time
    db.session.commit()

    return render_template('score.html', 
                           title='Final Score',
                           total_score=correct_count,
                           total_answered=total_answered,
                           total_time=total_time)

@app.route('/logout')
def logout():
    if not g.user:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('total_score', None)
    return redirect(url_for('home'))
