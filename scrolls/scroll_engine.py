from scrolls.scroll_event import ScrollEvent
from scrolls.trigger_manager import check_scroll_triggers
from scrolls.api_scrolls import execute_api_scroll
from storyrealms.system_mapper import SystemMapper

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
    def __init__(self, world_engine=None, kernel_bridge=None):
        self.world_engine = world_engine
        self.kernel_bridge = kernel_bridge
        self.system_mapper = SystemMapper(world_engine) if world_engine else None
        
        self.scrolls = {
            "optimize self": self._optimize_self,
            "study topic": self._study_topic,
            "trigger api scroll": self._trigger_api_scroll,
            "run task": self._run_task,
            "multi step plan": self._multi_step_plan,
            "change realm": self._change_realm,
            "system status": self._system_status,
            "map system": self._map_system,
            "map runtime": self._map_runtime,
            "analyze system": self._analyze_system,
            "diff systems": self._diff_systems,
            "materialize realm": self._materialize_realm,
            "generate realm": self._generate_realm,
            "generate quest": self._generate_quest,
            "list quests": self._list_quests,
            "scan reality": self._scan_reality,
            "sync reality": self._sync_reality,
            "generate reality quest": self._generate_reality_quest,
            "sentry scan": self._sentry_scan,
            "exorcise": self._exorcise
        }
        self.active_scrolls = []

    def _sentry_scan(self):
        if not self.world_engine: return "[Scroll] No World Engine."
        from guardian.sentry import CyberSentry
        sentry = CyberSentry(self.world_engine)
        results = sentry.scan_and_manifest()
        if results:
            return f"[Sentry] Threats detected and manifested:\n" + "\n".join(results)
        return "[Sentry] The plane is calm. No heavy processes detected."

    def _exorcise(self, target_name):
        if not self.world_engine: return "[Scroll] No World Engine."
        from guardian.sentry import CyberSentry
        sentry = CyberSentry(self.world_engine)
        return sentry.exorcise_entity(target_name)

    def _generate_reality_quest(self, realm_name):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.dungeon_master import DungeonMaster
        dm = DungeonMaster(self.world_engine)
        quest = dm.generate_reality_quest(realm_name)
        if quest:
            return f"[ARG] Reality Quest Linked: {quest.title}\nOrders: {quest.description}"
        return "[ARG] Signal interference. Cannot link quest."

    def _scan_reality(self):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.reality_overlay import RealityOverlay
        overlay = RealityOverlay(self.world_engine)
        encounter = overlay.scan_reality_for_encounter()
        
        # Inject enemy into current realm
        if self.world_engine.current_realm:
            from storyrealms.entities import AgentEntity
            enemy_data = encounter["entity"]
            enemy = AgentEntity(enemy_data["name"], role="Enemy", location="Root", properties=enemy_data["properties"])
            self.world_engine.current_realm.entities.append(enemy.to_dict())
            self.world_engine.save_realm(self.world_engine.current_realm)
            
        return f"[ARG] Scan Complete.\n{encounter['description']}\nEnemy '{encounter['entity']['name']}' manifested."

    def _sync_reality(self):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.reality_overlay import RealityOverlay
        overlay = RealityOverlay(self.world_engine)
        weather = overlay.sync_weather_effects()
        return f"[ARG] Atmosphere Synced: {weather['description']} Effects: {weather['effects']}"

    def _generate_quest(self, realm_name):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.dungeon_master import DungeonMaster
        dm = DungeonMaster(self.world_engine)
        quest = dm.generate_quest(realm_name)
        if quest:
            return f"[Quest] New Quest: {quest.title}\nObjective: {quest.description}"
        return "[Quest] Failed to generate quest."

    def _list_quests(self, realm_name):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.dungeon_master import DungeonMaster
        dm = DungeonMaster(self.world_engine)
        quests = dm.list_active_quests(realm_name)
        if not quests:
            return "No active quests in this realm."
        return "\n".join([f"- {q['title']} ({q['status']})" for q in quests])

    def _generate_realm(self, name, prompt):
        if not self.world_engine: return "[Scroll] No World Engine."
        from storyrealms.builder import RealmBuilder
        builder = RealmBuilder(self.world_engine)
        builder.generate_realm_from_prompt(name, prompt)
        return f"[Scroll] Generated realm '{name}' from prompt: {prompt}"

    def _diff_systems(self, realm_a, realm_b):
        if not self.system_mapper: return "[Scroll] No System Mapper."
        return self.system_mapper.diff_realms(realm_a, realm_b)

    def _materialize_realm(self, realm_name, target_path):
        if not self.system_mapper: return "[Scroll] No System Mapper."
        return self.system_mapper.materialize_realm(realm_name, target_path)

    def _analyze_system(self, realm_name):
        if not self.system_mapper:
            return "[Scroll] System Mapper not available."
        return self.system_mapper.analyze_realm(realm_name)

    def _map_system(self, path):
        if not self.system_mapper:
            return "[Scroll] System Mapper not available (World Engine missing)."
        return self.system_mapper.map_filesystem(path)

    def _map_runtime(self):
        if not self.system_mapper:
            return "[Scroll] System Mapper not available (World Engine missing)."
        return self.system_mapper.map_active_runtime()

    def _system_status(self):
        if self.kernel_bridge:
            stats = self.kernel_bridge.get_system_stats()
            return f"[System] Status: CPU {stats['cpu_percent']}%, MEM {stats['memory_percent']}%, DISK {stats['disk_percent']}%"
        return "[System] Kernel Bridge not available."

    def _change_realm(self, realm_name):
        if not realm_name:
            return "[Realm] No realm name provided."
            
        if self.world_engine:
            if self.world_engine.enter_realm(realm_name):
                return f"[Realm] Entered realm: {realm_name}"
            else:
                return f"[Realm] Could not find realm: {realm_name}"
        else:
            # Fallback if not injected, try to load directly
            from storyrealms.engine import StoryRealmsEngine
            temp_engine = StoryRealmsEngine()
            if temp_engine.enter_realm(realm_name):
                return f"[Realm] Entered realm: {realm_name} (Warning: Temporary Engine Instance)"
            return f"[Realm] Could not find realm: {realm_name}"

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
