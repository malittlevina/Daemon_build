from scrolls.scroll_event import ScrollEvent
from scrolls.trigger_manager import check_scroll_triggers
from scrolls.api_scrolls import execute_api_scroll

# Import robot scrolls for integration
try:
    from scrolls.robot_scrolls import register_robot_scrolls, RobotScrolls
    ROBOT_SCROLLS_AVAILABLE = True
except ImportError:
    ROBOT_SCROLLS_AVAILABLE = False
    print("[ScrollEngine] Robot scrolls not available")

class ScrollTrigger:
    def __init__(self, name, conditions, actions):
        self.name = name
        self.conditions = conditions  # List of ScrollCondition instances
        self.actions = actions        # List of ScrollAction instances

    def check_and_fire(self, event: ScrollEvent):
        if all(condition.evaluate(event) for condition in self.conditions):
            for action in self.actions:
                action.execute(event)

class ScrollEngine:
    def __init__(self):
        self.scrolls = {
            "optimize self": self._optimize_self,
            "study topic": self._study_topic,
            "trigger api scroll": self._trigger_api_scroll,
            "run task": self._run_task,
            "multi step plan": self._multi_step_plan
        }
        self.active_scrolls = []
        
        # Register robot scrolls if available
        if ROBOT_SCROLLS_AVAILABLE:
            register_robot_scrolls(self)
            print("[ScrollEngine] Robot scrolls registered")

    def invoke(self, name, *args, **kwargs):
        if name in self.scrolls:
            return self.scrolls[name](*args, **kwargs)
        else:
            return self.invoke_dynamic_scroll(name)

    def _optimize_self(self):
        from optimizer.auto_upgrade import run_auto_optimization
        return run_auto_optimization()

    def _study_topic(self, topic):
        from codex.ingestion import ingest_observation, ingest_web_or_pdf
        from code_tools.tutor import study_topic  # Optional enhancement hook

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
            print(f"[Study] Knowledge Digest:\n{summary[:500]}...\n")
            knowledge_path = f"knowledge/{topic.lower().replace(' ', '_')}.md"
            os.makedirs(os.path.dirname(knowledge_path), exist_ok=True)
            with open(knowledge_path, "w") as f:
                f.write(f"# {topic.title()} Summary\n\n{summary}\n")

            print(f"[Study] Summary written to: {knowledge_path}")

            # Add a self-quiz line (simulated reflection test)
            quiz_prompt = f"Explain something important about {topic}"
            print(f"[Study] Self-quiz prompt: {quiz_prompt}")
            from introspection.personality import respond_to_input
            try:
                answer = respond_to_input(quiz_prompt)
                print(f"[Study] Prom's response: {answer}")
                with open(knowledge_path, "a") as f:
                    f.write(f"\n\n## Self-Quiz\n\n**Q:** {quiz_prompt}\n\n**A:** {answer}\n")
                    score = "✔️" if "loop" in answer.lower() or len(answer.split()) > 5 else "❌"
                    f.write(f"\n**Score:** {score}")
                print(f"[Study] Quiz result saved to: {knowledge_path}")
                print(f"[Study] Self-quiz score: {score}")
            except Exception as e:
                print(f"[Study] Failed to quiz Prom: {e}")

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

        print(f"[TaskRunner] Executing task: {task_description}")
        # Simulate task execution
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
        from code_tools.planner import generate_plan  # You need to implement this module

        if not goal:
            return "[Planner] No goal provided."

        plan = generate_plan(goal)
        os.makedirs("logs", exist_ok=True)
        with open("logs/task_memory.log", "a") as log_file:
            log_file.write(f"{time.ctime()} - Goal: {goal}\nPlan: {plan}\n")

        print(f"[Planner] Multi-step plan:\n{plan}")
        ingest_observation(f"Generated plan for goal: {goal}\n{plan}")
        return f"[Planner] Plan generated for goal: {goal}"
