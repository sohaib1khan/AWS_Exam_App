# AWS Developer Associate Study Quiz

A simple, containerized web application for studying AWS Developer Associate exam questions built with Python and Flask. This application allows you to:

- Take quizzes with AWS Developer Associate exam questions
- Check your answers with detailed explanations
- Track your progress through the question bank
- Add, edit, and manage custom questions with Markdown support

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Setup](#manual-setup)
4. [Features](#features)
5. [Application Structure](#application-structure)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Quick Start

The easiest way to get started is by using the provided deployment script:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

Once deployed, access the application at: [http://localhost:5019](http://localhost:5019)

## Manual Setup

If you prefer to set up manually or need to customize the installation:

1. **Clone or download the project files**

2. **Build and start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application** at [http://localhost:5019](http://localhost:5019)

4. **View logs (if needed)**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Features

- **Interactive Quiz Interface**: Clean, responsive UI for answering questions
- **Markdown Support**: Add rich formatting to questions and explanations
- **Progress Tracking**: Monitor which questions you've answered correctly/incorrectly
- **Question Management**: Add, edit, and delete questions through the web interface
- **Persistent Storage**: Questions data persists between container restarts

## Application Structure

```
aws-study-app/
├── main.py              # Flask application code
├── questions.json       # Question database
├── requirements.txt     # Python dependencies
├── static/              # CSS and static assets
│   └── css/
│       └── style.css    # Application styling
├── templates/           # HTML templates
│   ├── add_question.html
│   ├── base.html
│   ├── edit_question.html
│   ├── index.html
│   ├── manage_questions.html
│   ├── quiz.html
│   └── result.html
├── Dockerfile           # Container definition
├── docker-compose.yml   # Container orchestration
└── deploy.sh            # Deployment automation script
```

## Customization

### Changing the Port

To change the default port (5019), edit the `docker-compose.yml` file:

```yaml
ports:
  - "8080:5019"  # Change 8080 to your desired port
```

### Adding Custom Questions

You can add custom questions either:

1. Through the web interface: Go to "Add Question" in the navigation
2. Directly editing the `questions.json` file before deployment

### Styling

To customize the appearance, edit the `static/css/style.css` file.

## Troubleshooting

### Container Won't Start

Check the logs for errors:

```bash
docker-compose logs
```

Common issues:
- Port conflicts: Change the port in `docker-compose.yml`
- Permission issues: Make sure `questions.json` is writable

### Reset Quiz Progress

If you want to reset your progress:
1. Click the "Reset Progress" button on the quiz page, or
2. Clear your browser's local storage

### Container Updates

If you've made changes to the code and need to update the container:

```bash
docker-compose down
docker-compose up -d --build
```

---

Happy studying for your AWS Developer Associate exam!