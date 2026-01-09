import abc

class Specialty(abc.ABC):
    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def description(self):
        pass

    @abc.abstractmethod
    def can_handle(self, task):
        pass

    @abc.abstractmethod
    def execute(self, task):
        pass

class SoftwareSpecialty(Specialty):
    def name(self):
        return "Software Engineering"
        
    def description(self):
        return "Proficient in Python, Rust, JS, Julia, and system architecture."
        
    def can_handle(self, task):
        keywords = ["code", "debug", "python", "script", "program"]
        return any(k in task.lower() for k in keywords)
        
    def execute(self, task):
        return f"[Software] Analyzing codebase for task: {task}"

class ResearchSpecialty(Specialty):
    def name(self):
        return "Academic Research"
        
    def description(self):
        return "Synthesizes information from texts and logs."
        
    def can_handle(self, task):
        return "research" in task.lower() or "study" in task.lower()
        
    def execute(self, task):
        return f"[Research] Querying Codex for: {task}"

class PrometheusSpecialties:
    def __init__(self):
        self.specialties = {}
        self._register_defaults()
        print(f"[Prometheus] Initialized with {len(self.specialties)} specialties.")

    def _register_defaults(self):
        self.register(SoftwareSpecialty())
        self.register(ResearchSpecialty())

    def register(self, specialty: Specialty):
        self.specialties[specialty.name()] = specialty

    def get_specialty(self, name):
        return self.specialties.get(name)

    def find_capable(self, task):
        """Finds the best specialty for a given task."""
        for spec in self.specialties.values():
            if spec.can_handle(task):
                return spec
        return None

    def specialize(self, topic):
        # Backward compatibility for old string-based dict lookups
        # If topic matches a specialty name, return description
        # Otherwise return a generic string if in old list (simulated)
        for name, spec in self.specialties.items():
            if topic.lower() in name.lower():
                print(f"[Prometheus] Activating domain: {name}")
                return spec.description()
        
        # Fallback for old hardcoded keys if not migrated to classes yet
        old_domains = {
            "mechanical": "Knows CAD, control systems, sensors",
            "philosophy": "Understands logic, ethics, dialectic reasoning",
            "video": "Capable of editing with FFMPEG, Shotcut, etc.",
            "3D_animation": "Can render/export with Blender or symbolic engine",
            "modeling": "Knows symbolic primitives and geometry tools",
            "storytelling": "Skilled at plot development and game writing"
        }
        if topic in old_domains:
             print(f"[Prometheus] Activating domain: {topic}")
             return old_domains[topic]
             
        print(f"[Prometheus] No specific module for: {topic}")
        return None
