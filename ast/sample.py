import datetime

class Task:
    def __init__(self, title, due_date=None):
        self.title = title
        self.created_at = datetime.datetime.now()
        self.due_date = due_date
        self.completed = False

    def mark_complete(self):
        self.completed = True

    def is_overdue(self):
        if self.due_date:
            return datetime.datetime.now() > self.due_date
        return False

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"[{status}] {self.title} (Due: {self.due_date})"

def list_overdue_tasks(tasks):
    return [task for task in tasks if task.is_overdue() and not task.completed]

# Example usage
if __name__ == "__main__":
    tasks = [
        Task("Write documentation", datetime.datetime(2023, 5, 1)),
        Task("Refactor code"),
        Task("Submit pull request", datetime.datetime(2023, 5, 3)),
    ]
    tasks[0].mark_complete()
    for t in list_overdue_tasks(tasks):
        print(t)
