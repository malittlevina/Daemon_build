from scrolls.scroll_event import ScrollEvent
from scrolls.trigger_manager import check_scroll_triggers
from scrolls.api_scrolls import execute_api_scroll

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
            "multi step plan": self._multi_step_plan,
            # XR-related scrolls
            "start xr session": self._start_xr_session,
            "end xr session": self._end_xr_session,
            "start xr training": self._start_xr_training,
            "end xr training": self._end_xr_training,
            "create ar overlay": self._create_ar_overlay,
            "clear ar overlays": self._clear_ar_overlays,
            "place spatial anchor": self._place_spatial_anchor,
            "show training scenarios": self._show_training_scenarios,
            "xr status": self._xr_status
        }
        self.active_scrolls = []
        self.xr_engine = None
        self.xr_overlay_manager = None
        self.xr_anchor_system = None
        self.xr_training_module = None

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

    # ===== XR Scrolls =====
    
    def set_xr_subsystems(self, xr_engine=None, overlay_manager=None, anchor_system=None, training_module=None):
        """Register XR subsystems with the scroll engine."""
        self.xr_engine = xr_engine
        self.xr_overlay_manager = overlay_manager
        self.xr_anchor_system = anchor_system
        self.xr_training_module = training_module
        print("[ScrollEngine] XR subsystems registered.")

    def _start_xr_session(self, mode="ar", device="simulated"):
        """Start an XR session."""
        if not self.xr_engine:
            return "[XR Scroll] XR engine not available."
        
        try:
            session = self.xr_engine.start_session(mode=mode, device_type=device)
            
            # Update symbolic state
            from lam.symbolic_state import update_xr_state
            update_xr_state({
                "active": True,
                "mode": mode,
                "device": device,
                "session_id": session.session_id
            })
            
            return f"[XR Scroll] Started {mode} session on {device} device. Session ID: {session.session_id}"
        except Exception as e:
            return f"[XR Scroll] Failed to start session: {e}"

    def _end_xr_session(self):
        """End the current XR session."""
        if not self.xr_engine:
            return "[XR Scroll] XR engine not available."
        
        try:
            summary = self.xr_engine.end_session()
            
            # Update symbolic state
            from lam.symbolic_state import update_xr_state
            update_xr_state({
                "active": False,
                "mode": None,
                "device": None,
                "session_id": None
            })
            
            if summary:
                return f"[XR Scroll] Session ended. Duration: {summary.get('event_count', 0)} events logged."
            return "[XR Scroll] No active session to end."
        except Exception as e:
            return f"[XR Scroll] Failed to end session: {e}"

    def _start_xr_training(self, scenario_id=None, mode="guided"):
        """Start an XR training session."""
        if not self.xr_training_module:
            return "[XR Scroll] XR training module not available."
        
        try:
            # List available scenarios if none specified
            if not scenario_id:
                scenarios = self.xr_training_module.list_scenarios()
                scenario_list = "\n".join([f"  - {s['scenario_id']}: {s['title']}" for s in scenarios[:5]])
                return f"[XR Scroll] Available training scenarios:\n{scenario_list}\n\nUse 'start xr training <scenario_id>' to begin."
            
            session = self.xr_training_module.start_training(scenario_id=scenario_id, mode=mode)
            
            if session:
                # Update symbolic state
                from lam.symbolic_state import update_xr_state
                update_xr_state({
                    "training_active": True,
                    "training_scenario": scenario_id
                })
                
                return f"[XR Scroll] Started training: {session.scenario.title}\nMode: {mode}\nSteps: {len(session.scenario.steps)}"
            return f"[XR Scroll] Scenario not found: {scenario_id}"
        except Exception as e:
            return f"[XR Scroll] Failed to start training: {e}"

    def _end_xr_training(self):
        """End the current XR training session."""
        if not self.xr_training_module:
            return "[XR Scroll] XR training module not available."
        
        try:
            result = self.xr_training_module.end_training()
            
            # Update symbolic state
            from lam.symbolic_state import update_xr_state
            update_xr_state({
                "training_active": False,
                "training_scenario": None
            })
            
            if result:
                progress = result.get("scenario", {}).get("progress", {})
                return f"[XR Scroll] Training ended. Progress: {progress.get('completed_steps', 0)}/{progress.get('total_steps', 0)} steps."
            return "[XR Scroll] No active training session."
        except Exception as e:
            return f"[XR Scroll] Failed to end training: {e}"

    def _create_ar_overlay(self, text, title=None, position=None):
        """Create an AR overlay/info panel."""
        if not self.xr_overlay_manager:
            return "[XR Scroll] AR overlay manager not available."
        
        try:
            pos = tuple(position) if position else (0, 1.5, 2)
            overlay = self.xr_overlay_manager.create_info_panel(
                text=text,
                title=title,
                position=pos
            )
            return f"[XR Scroll] Created AR overlay: {overlay.overlay_id}"
        except Exception as e:
            return f"[XR Scroll] Failed to create overlay: {e}"

    def _clear_ar_overlays(self, group=None):
        """Clear AR overlays."""
        if not self.xr_overlay_manager:
            return "[XR Scroll] AR overlay manager not available."
        
        try:
            if group:
                count = self.xr_overlay_manager.clear_group(group)
                return f"[XR Scroll] Cleared {count} overlays from group '{group}'."
            else:
                count = self.xr_overlay_manager.clear_all()
                return f"[XR Scroll] Cleared all {count} overlays."
        except Exception as e:
            return f"[XR Scroll] Failed to clear overlays: {e}"

    def _place_spatial_anchor(self, label, position, persistent=False):
        """Place a spatial anchor."""
        if not self.xr_anchor_system:
            return "[XR Scroll] Spatial anchor system not available."
        
        try:
            pos = tuple(position) if position else (0, 0, 0)
            anchor = self.xr_anchor_system.create_semantic_anchor(
                semantic_label=label,
                position=pos,
                persistent=persistent
            )
            return f"[XR Scroll] Placed anchor '{label}' at {pos}. ID: {anchor.anchor_id}"
        except Exception as e:
            return f"[XR Scroll] Failed to place anchor: {e}"

    def _show_training_scenarios(self, domain=None):
        """List available training scenarios."""
        if not self.xr_training_module:
            return "[XR Scroll] XR training module not available."
        
        try:
            scenarios = self.xr_training_module.list_scenarios(domain_filter=domain)
            
            if not scenarios:
                return "[XR Scroll] No training scenarios available."
            
            output = "[XR Scroll] Available Training Scenarios:\n"
            for s in scenarios:
                output += f"\n  📚 {s['title']} (ID: {s['scenario_id']})\n"
                output += f"     Domain: {s['domain']} | Difficulty: {'⭐' * s['difficulty']}\n"
                output += f"     Skills: {', '.join(s['skills'][:3])}\n"
            
            return output
        except Exception as e:
            return f"[XR Scroll] Failed to list scenarios: {e}"

    def _xr_status(self):
        """Get current XR subsystem status."""
        status = "[XR Scroll] XR Subsystem Status:\n"
        
        # XR Engine status
        if self.xr_engine:
            session_status = self.xr_engine.get_session_status()
            if session_status["status"] == "active":
                session = session_status["session"]
                status += f"  🥽 XR Session: Active ({session['mode']})\n"
                status += f"     Device: {session['device_type']}\n"
                status += f"     Overlays: {session['overlays_count']} | Anchors: {session['anchors_count']}\n"
            else:
                status += "  🥽 XR Session: Inactive\n"
        else:
            status += "  🥽 XR Engine: Not initialized\n"
        
        # Training status
        if self.xr_training_module:
            if self.xr_training_module.active_session:
                session = self.xr_training_module.active_session
                progress = session.scenario.get_progress()
                status += f"  📚 Training: {session.scenario.title}\n"
                status += f"     Progress: {progress['completed_steps']}/{progress['total_steps']} steps\n"
            else:
                status += f"  📚 Training: Not active\n"
                stats = self.xr_training_module.get_training_stats()
                status += f"     Sessions completed: {stats['sessions_completed']}\n"
        else:
            status += "  📚 Training Module: Not initialized\n"
        
        # Overlay status
        if self.xr_overlay_manager:
            overlays = self.xr_overlay_manager.list_overlays()
            visible = sum(1 for o in overlays if o.get("is_visible"))
            status += f"  🖼️ Overlays: {visible} visible / {len(overlays)} total\n"
        
        # Anchor status
        if self.xr_anchor_system:
            anchors = self.xr_anchor_system.list_anchors()
            status += f"  📍 Spatial Anchors: {len(anchors)} placed\n"
        
        return status
