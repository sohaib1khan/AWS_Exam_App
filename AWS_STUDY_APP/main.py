from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import markdown

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # for flash messages

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

def load_questions():
    with open('questions.json', 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open('questions.json', 'w') as f:
        json.dump(questions, f)

def convert_markdown(text):
    """Convert markdown text to HTML"""
    return markdown.markdown(text)

@app.route('/question_stats')
def question_stats():
    """Return the total number of questions for progress tracking"""
    questions = load_questions()
    return jsonify({
        'total': len(questions),
        'ids': [q['id'] for q in questions]
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    questions = load_questions()
    
    # Convert markdown to HTML for questions
    for question in questions:
        question['question_html'] = convert_markdown(question['question'])
        question['explanation_html'] = convert_markdown(question['explanation'])
        
    return render_template('quiz.html', questions=questions)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    question_id = int(request.form.get('question_id'))
    selected_answer = request.form.get('answer')
    
    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    # Convert markdown to HTML
    question['question_html'] = convert_markdown(question['question'])
    question['explanation_html'] = convert_markdown(question['explanation'])
    
    is_correct = selected_answer == question['correct_answer']
    
    return render_template('result.html', 
                          question=question, 
                          selected_answer=selected_answer, 
                          is_correct=is_correct)

@app.route('/add_question', methods=['GET', 'POST'])
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
def manage_questions():
    questions = load_questions()
    return render_template('manage_questions.html', questions=questions)

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
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
def delete_question(question_id):
    questions = load_questions()
    questions = [q for q in questions if q['id'] != question_id]
    save_questions(questions)
    flash('Question deleted successfully!')
    return redirect(url_for('manage_questions'))

@app.route('/markdown_preview', methods=['POST'])
def markdown_preview():
    """API endpoint for previewing markdown"""
    text = request.form.get('text', '')
    html = convert_markdown(text)
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5019, debug=True)