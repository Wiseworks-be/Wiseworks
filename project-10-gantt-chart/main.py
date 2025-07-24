# main.py projrect-10-gantt-chart

from flask import Flask, render_template, jsonify
import datetime

# Initialize the Flask App
main = Flask(__name__)

# --- Sample Dataset ---
# In a real application, you would get this from a database, a file, or an API.
# The format for Google Charts is specific:
# [Task ID, Task Name, Start Date, End Date, Duration, Percent Complete, Dependencies]
#
# - Task ID: A unique string for the task.
# - Dependencies: The ID of the task that this task depends on. Can be null.
def get_task_data():
    """Defines our project plan."""
    tasks = [
        # Task ID, Task Name, Start Date, End Date, Duration(ms), % Complete, Dependencies
        ['research', 'Find Sources', datetime.date(2024, 1, 1), datetime.date(2024, 1, 5), None, 100, None],
        ['write', 'Write Paper', None, None, 3 * 24*60*60*1000, 25, 'research'], # Depends on 'research'
        ['cite', 'Create Bibliography', None, None, 1 * 24*60*60*1000, 20, 'write'],    # Depends on 'write'
        ['review', 'Review Paper', None, None, 2 * 24*60*60*1000, 75, 'write'],    # also depends on 'write'
        ['submit', 'Submit Paper', None, None, 1 * 24*60*60*1000, 0, 'cite,review'], # Depends on both 'cite' AND 'review'
        
        # A separate, independent task line
        ['design_sprint', 'Design New Feature', datetime.date(2024, 1, 8), datetime.date(2024, 1, 12), None, 100, None],
        ['dev_sprint', 'Develop Feature', None, None, 10 * 24*60*60*1000, 50, 'design_sprint'],
    ]
    return tasks

@main.route('/')
def index():
    """Serves the main HTML page that will contain the chart."""
    return render_template('index.html')

@main.route('/data')
def get_data():
    """This is the JSON endpoint that provides data to the Google Chart."""
    tasks = get_task_data()
    
    # Google Charts expects dates as 'Date(YYYY, M, D)' in JS.
    # We will format the dates as strings and handle them in the frontend.
    # Note: JavaScript months are 0-indexed (Jan=0, Feb=1, etc.)
    formatted_tasks = []
    for task in tasks:
        # Unpack the task
        task_id, task_name, start, end, duration, percent, deps = task
        
        # Format dates, handling None for start/end
        start_str = start.isoformat() if start else None
        end_str = end.isoformat() if end else None

        formatted_tasks.append([task_id, task_name, start_str, end_str, duration, percent, deps])

    return jsonify(formatted_tasks)


if __name__ == '__main__':
    main.run(debug=True)