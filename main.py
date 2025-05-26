from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import random  
import json
import os
import markdown
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'  # Change this in production!

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'

# Create templates and static directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Sample questions data structure
QUESTIONS = [
    {
        "id": 1,
        "question": "Which AWS service is primarily used for storing static files?",
        "options": ["EC2", "S3", "DynamoDB", "RDS"],
        "correct_answer": "S3",
        "explanation": "Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance for storing static files."
    },
    {
        "id": 2,
        "question": "Which AWS service would you use to run containers?",
        "options": ["EC2", "S3", "ECS/EKS", "Lambda"],
        "correct_answer": "ECS/EKS",
        "explanation": "Amazon ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) are services designed specifically for running containers in AWS."
    }
]

# Save questions to a JSON file if it doesn't exist
if not os.path.exists('questions.json'):
    with open('questions.json', 'w') as f:
        json.dump(QUESTIONS, f)

# Initialize progress.json if it doesn't exist
if not os.path.exists('progress.json'):
    with open('progress.json', 'w') as f:
        json.dump({}, f)

def load_users():
    """Load users from users.json"""
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_progress():
    """Load user progress from progress.json"""
    try:
        with open('progress.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_progress(progress):
    """Save user progress to progress.json"""
    with open('progress.json', 'w') as f:
        json.dump(progress, f, indent=2)

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_questions():
    with open('questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('questions.json', 'w') as f:
        json.dump(questions, f)

def convert_markdown(text):
    """Convert markdown text to HTML"""
    return markdown.markdown(text)

def get_user_progress(username):
    """Get progress for a specific user"""
    progress = load_progress()
    return progress.get(username, {})

def save_user_progress(username, question_id, is_correct):
    """Save progress for a specific user and question"""
    progress = load_progress()
    
    if username not in progress:
        progress[username] = {}
    
    progress[username][str(question_id)] = {
        'completed': True,
        'correct': is_correct,
        'timestamp': str(json.dumps(None))  # You can add proper timestamp if needed
    }
    
    save_progress(progress)

def initialize_quiz_session():
    """Initialize a new quiz session with shuffled questions"""
    questions = load_questions()
    random.shuffle(questions)
    
    # Store shuffled question IDs in session
    session['quiz_questions'] = [q['id'] for q in questions]
    session['current_question_index'] = 0
    session['quiz_active'] = True
    
    return questions

def get_current_question():
    """Get the current question based on session state"""
    if 'quiz_questions' not in session or 'current_question_index' not in session:
        return None
    
    questions = load_questions()
    question_ids = session['quiz_questions']
    current_index = session['current_question_index']
    
    if current_index >= len(question_ids):
        return None
    
    current_question_id = question_ids[current_index]
    current_question = next((q for q in questions if q['id'] == current_question_id), None)
    
    return current_question

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        
        if username in users and users[username] == password:
            session['username'] = username
            flash(f'Welcome back, {username}!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('username', None)
    # Clear quiz session data
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)
    flash(f'You have been logged out. Goodbye!')
    return redirect(url_for('login'))

@app.route('/reset_progress', methods=['POST'])
@login_required
def reset_progress():
    """Reset progress for the current user"""
    username = session.get('username')
    progress = load_progress()
    
    # Remove user's progress
    if username in progress:
        del progress[username]
        save_progress(progress)
        flash('Your progress has been reset successfully!')
    else:
        flash('No progress found to reset.')
    
    return jsonify({'success': True})

# Main Routes (now with authentication)
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/question_stats')
@login_required
def question_stats():
    """Return the total number of questions and user progress for progress tracking"""
    questions = load_questions()
    username = session.get('username')
    user_progress = get_user_progress(username)
    
    return jsonify({
        'total': len(questions),
        'ids': [q['id'] for q in questions],
        'completed': len(user_progress),
        'progress': user_progress
    })

# Updated Quiz Routes - Single Question Per Page
@app.route('/quiz')
@login_required
def quiz():
    """Redirect to quiz start - maintains backward compatibility"""
    return redirect(url_for('quiz_start'))

@app.route('/quiz/start')
@login_required
def quiz_start():
    """Start a new quiz session"""
    # Clear any existing quiz session
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)
    
    # Initialize new quiz
    initialize_quiz_session()
    
    return redirect(url_for('quiz_question'))

@app.route('/quiz/question')
@login_required
def quiz_question():
    """Display the current question"""
    if 'quiz_questions' not in session:
        flash('Please start the quiz first.')
        return redirect(url_for('quiz_start'))
    
    current_question = get_current_question()
    
    if current_question is None:
        # Quiz completed
        return redirect(url_for('quiz_complete'))
    
    # Convert markdown to HTML
    current_question['question_html'] = convert_markdown(current_question['question'])
    current_question['explanation_html'] = convert_markdown(current_question['explanation'])
    
    # Get user progress for this question
    username = session.get('username')
    user_progress = get_user_progress(username)
    question_id = str(current_question['id'])
    
    if question_id in user_progress:
        current_question['completed'] = True
        current_question['user_correct'] = user_progress[question_id]['correct']
    else:
        current_question['completed'] = False
        current_question['user_correct'] = False
    
    # Calculate progress
    current_index = session['current_question_index']
    total_questions = len(session['quiz_questions'])
    
    quiz_info = {
        'current_number': current_index + 1,
        'total_questions': total_questions,
        'progress_percentage': ((current_index + 1) / total_questions) * 100
    }
    
    return render_template('quiz.html', 
                          question=current_question, 
                          quiz_info=quiz_info,
                          single_question=True)

@app.route('/quiz/complete')
@login_required
def quiz_complete():
    """Show quiz completion summary"""
    if 'quiz_questions' not in session:
        flash('No quiz session found.')
        return redirect(url_for('index'))
    
    username = session.get('username')
    user_progress = get_user_progress(username)
    question_ids = session['quiz_questions']
    
    # Calculate results
    total_questions = len(question_ids)
    answered_questions = 0
    correct_answers = 0
    
    for question_id in question_ids:
        if str(question_id) in user_progress:
            answered_questions += 1
            if user_progress[str(question_id)]['correct']:
                correct_answers += 1
    
    results = {
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'score_percentage': (correct_answers / total_questions * 100) if total_questions > 0 else 0
    }
    
    # Clear quiz session
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)
    
    return render_template('quiz_complete.html', results=results)

@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    question_id = int(request.form.get('question_id'))
    selected_answer = request.form.get('answer')
    username = session.get('username')
    
    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    # Convert markdown to HTML
    question['question_html'] = convert_markdown(question['question'])
    question['explanation_html'] = convert_markdown(question['explanation'])
    
    is_correct = selected_answer == question['correct_answer']
    
    # Save user progress
    save_user_progress(username, question_id, is_correct)
    
    return render_template('result.html', 
                          question=question, 
                          selected_answer=selected_answer, 
                          is_correct=is_correct)

@app.route('/quiz/next', methods=['POST'])
@login_required
def quiz_next():
    """Move to next question"""
    if 'current_question_index' in session:
        session['current_question_index'] += 1
    
    return redirect(url_for('quiz_question'))

@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        questions = load_questions()
        
        # Generate new ID (max ID + 1)
        new_id = max([q['id'] for q in questions], default=0) + 1
        
        # Get form data
        question_text = request.form.get('question')
        options = [
            request.form.get('option1'),
            request.form.get('option2'),
            request.form.get('option3'),
            request.form.get('option4')
        ]
        correct_answer = request.form.get('correct_answer')
        explanation = request.form.get('explanation')
        
        # Create new question
        new_question = {
            "id": new_id,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        }
        
        # Add to questions list
        questions.append(new_question)
        save_questions(questions)
        
        flash('Question added successfully!')
        return redirect(url_for('add_question'))
    
    return render_template('add_question.html')

@app.route('/manage_questions')
@login_required
def manage_questions():
    questions = load_questions()
    return render_template('manage_questions.html', questions=questions)

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if question is None:
        flash('Question not found!')
        return redirect(url_for('manage_questions'))
    
    if request.method == 'POST':
        # Update question data
        question['question'] = request.form.get('question')
        question['options'] = [
            request.form.get('option1'),
            request.form.get('option2'),
            request.form.get('option3'),
            request.form.get('option4')
        ]
        question['correct_answer'] = request.form.get('correct_answer')
        question['explanation'] = request.form.get('explanation')
        
        save_questions(questions)
        flash('Question updated successfully!')
        return redirect(url_for('manage_questions'))
    
    return render_template('edit_question.html', question=question)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    questions = load_questions()
    questions = [q for q in questions if q['id'] != question_id]
    save_questions(questions)
    flash('Question deleted successfully!')
    return redirect(url_for('manage_questions'))

@app.route('/markdown_preview', methods=['POST'])
@login_required
def markdown_preview():
    """API endpoint for previewing markdown"""
    text = request.form.get('text', '')
    html = convert_markdown(text)
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5019, debug=True)