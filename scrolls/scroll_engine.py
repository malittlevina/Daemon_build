from core.module import Module
from scrolls.scroll_event import ScrollEvent
from scrolls.trigger_manager import check_scroll_triggers
from scrolls.api_scrolls import execute_api_scroll
import concurrent.futures
import threading
import uuid

class ScrollTrigger:
    def __init__(self, name, conditions, actions):
        self.name = name
        self.conditions = conditions  # List of ScrollCondition instances
        self.actions = actions        # List of ScrollAction instances

    def check_and_fire(self, event: ScrollEvent):
        if all(condition.evaluate(event) for condition in self.conditions):
            for action in self.actions:
                action.execute(event)

class ScrollEngine(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.scrolls = {
            "optimize self": self._optimize_self,
            "study topic": self._study_topic,
            "trigger api scroll": self._trigger_api_scroll,
            "run task": self._run_task,
            "multi step plan": self._multi_step_plan
        }
        self.active_scrolls = []
        self.executor = None
        self.running_tasks = {}

    def initialize(self):
        self.kernel.log("ScrollEngine", "Initialized.")
        self.kernel.events.subscribe("scroll:invoke", self.handle_invoke_event)

    def start(self):
        # Initialize thread pool with 3 workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="ScrollWorker")
        self.kernel.log("ScrollEngine", "Started async executor pool.")

    def stop(self):
        if self.executor:
            self.executor.shutdown(wait=False)
            self.kernel.log("ScrollEngine", "Stopped executor pool.")

    def handle_invoke_event(self, event_type, data):
        name = data.get("name")
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        # Dispatch to async handler
        self.invoke_async(name, *args, **kwargs)

    def invoke_async(self, name, *args, **kwargs):
        """Public method to schedule a scroll asynchronously."""
        if not self.executor:
            self.kernel.log("ScrollEngine", "Executor not started, running synchronously.", level="warning")
            return self.invoke(name, *args, **kwargs)

        task_id = str(uuid.uuid4())[:8]
        self.kernel.log("ScrollEngine", f"Scheduling task {task_id}: {name}")
        
        future = self.executor.submit(self.invoke, name, *args, **kwargs)
        self.running_tasks[task_id] = future
        
        # Add done callback
        def task_done(f):
            try:
                result = f.result()
                self.kernel.log("ScrollEngine", f"Task {task_id} completed: {result}")
            except Exception as e:
                self.kernel.log("ScrollEngine", f"Task {task_id} failed: {e}", level="error")
            finally:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]

        future.add_done_callback(task_done)
        return task_id

    def invoke(self, name, *args, **kwargs):
        """Synchronous internal invoke."""
        if name in self.scrolls:
            return self.scrolls[name](*args, **kwargs)
        else:
            return self.invoke_dynamic_scroll(name)

    # ... [Keeping existing scroll methods _optimize_self, _study_topic, etc.] ...
    def _optimize_self(self):
        from optimizer.auto_upgrade import run_auto_optimization
        return run_auto_optimization()

    def _study_topic(self, topic):
        from codex.ingestion import ingest_observation, ingest_web_or_pdf
        # from code_tools.tutor import study_topic  # Optional enhancement hook

        if not topic:
            return "[Study] No topic provided."

        # Record the topic symbolically
        content = f"Scroll triggered self-study of topic: {topic}"
        ingest_observation(content)

        try:
            import os
            import time
            from codex.summarizer import summarize_content  # You need to implement this if not existing

            # Summarize the topic and save to knowledge file
            summary = summarize_content(topic)
            self.kernel.log("Study", f"Knowledge Digest:\n{summary[:100]}...")
            knowledge_path = f"knowledge/{topic.lower().replace(' ', '_')}.md"
            os.makedirs(os.path.dirname(knowledge_path), exist_ok=True)
            with open(knowledge_path, "w") as f:
                f.write(f"# {topic.title()} Summary\n\n{summary}\n")

            self.kernel.log("Study", f"Summary written to: {knowledge_path}")

            # Add a self-quiz line (simulated reflection test)
            quiz_prompt = f"Explain something important about {topic}"
            self.kernel.log("Study", f"Self-quiz prompt: {quiz_prompt}")
            from introspection.personality import respond_to_input
            try:
                answer = respond_to_input(quiz_prompt)
                self.kernel.log("Study", f"Prom's response: {answer}")
                with open(knowledge_path, "a") as f:
                    f.write(f"\n\n## Self-Quiz\n\n**Q:** {quiz_prompt}\n\n**A:** {answer}\n")
                    score = "✔️" if "loop" in answer.lower() or len(answer.split()) > 5 else "❌"
                    f.write(f"\n**Score:** {score}")
                self.kernel.log("Study", f"Quiz result saved to: {knowledge_path}")
                self.kernel.log("Study", f"Self-quiz score: {score}")
            except Exception as e:
                self.kernel.log("Study", f"Failed to quiz Prom: {e}", level="error")

            # Track study history
            os.makedirs("logs", exist_ok=True)
            with open("logs/study_history.log", "a") as log_file:
                log_file.write(f"{time.ctime()} - Studied topic: {topic}\n")

        except Exception as e:
            content += f" (Note: Failed summarization or logging: {str(e)})"

        # Optional: attempt to auto-ingest related public content
        try:
            ingest_web_or_pdf(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
        except Exception as e:
            content += f" (Note: Failed external ingest: {str(e)})"

        return content

    def _trigger_api_scroll(self, *args, **kwargs):
        return execute_api_scroll(*args, **kwargs)

    def register_scroll(self, scroll):
        if scroll not in self.active_scrolls:
            self.active_scrolls.append(scroll)

    def invoke_dynamic_scroll(self, name):
        scroll = next((s for s in self.active_scrolls if s['name'] == name), None)
        if scroll:
            return scroll['action']()
        else:
            raise ValueError(f"Scroll not found: {name}")

    def monitor_scrolls(self):
        check_scroll_triggers(self.active_scrolls)


    def _run_task(self, task_description):
        from codex.ingestion import ingest_observation
        import os
        import time

        if not task_description:
            return "[TaskRunner] No task description provided."

        self.kernel.log("TaskRunner", f"Executing task: {task_description}")
        # Simulate task execution
        time.sleep(2) # Simulate work
        result = f"Task completed: {task_description}"

        # Log memory
        os.makedirs("logs", exist_ok=True)
        with open("logs/task_memory.log", "a") as log_file:
            log_file.write(f"{time.ctime()} - {task_description}\n")

        ingest_observation(f"User asked to run task: {task_description}")
        ingest_observation(result)
        return result

    def _multi_step_plan(self, goal):
        import os
        import time
        from codex.ingestion import ingest_observation
        # from code_tools.planner import generate_plan  # You need to implement this module

        if not goal:
            return "[Planner] No goal provided."

        # Mocking generate_plan for now if it doesn't exist or isn't imported
        try:
            from code_tools.planner import generate_plan
            plan = generate_plan(goal)
        except ImportError:
             plan = f"Plan for {goal}:\n1. Analyze.\n2. Execute.\n3. Verify."

        os.makedirs("logs", exist_ok=True)
        with open("logs/task_memory.log", "a") as log_file:
            log_file.write(f"{time.ctime()} - Goal: {goal}\nPlan: {plan}\n")

        self.kernel.log("Planner", f"Multi-step plan:\n{plan}")
        ingest_observation(f"Generated plan for goal: {goal}\n{plan}")
        return f"[Planner] Plan generated for goal: {goal}"
