# /backend/run.py

from app import create_app, db
from app.models import Agent, Project, Analysis, APIService

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Agent': Agent,
        'Project': Project,
        'Analysis': Analysis,
        'APIService': APIService
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
