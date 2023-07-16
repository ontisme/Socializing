import queue
import threading


class TaskExecutor(threading.Thread):
    def __init__(self, max_concurrent_tasks):
        threading.Thread.__init__(self)
        self.task_queue = queue.Queue()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = 0
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            if self.running_tasks < self.max_concurrent_tasks:
                # Get a task from the queue
                try:
                    task = self.task_queue.get(timeout=1)  # Timeout to allow checking for stop signal
                except queue.Empty:
                    continue

                # Execute the task
                self.execute_task(task)
                self.task_queue.task_done()

    def execute_task(self, task):
        print("execute_task",task)
        pass

    def stop(self):
        self.stop_event.set()


class TaskManager:
    def __init__(self, max_concurrent_tasks):
        self.task_executor = TaskExecutor(max_concurrent_tasks)
        self.task_executor.start()

    def add_task(self, task):
        self.task_executor.task_queue.put(task)

    def stop(self):
        self.task_executor.stop()
        self.task_executor.join()
