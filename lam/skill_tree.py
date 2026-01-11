# lam/skill_tree.py
# Skill Tree System - Hierarchical skill representation and progression

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


class SkillCategory(Enum):
    """Categories of skills."""
    COGNITIVE = "cognitive"         # Reasoning, analysis, problem-solving
    LANGUAGE = "language"           # Natural language understanding
    ACTION = "action"               # Task execution
    KNOWLEDGE = "knowledge"         # Domain knowledge
    SOCIAL = "social"               # Interaction and communication
    CREATIVE = "creative"           # Creative generation
    TECHNICAL = "technical"         # Technical/coding skills
    XR = "xr"                       # AR/VR/XR skills
    META = "meta"                   # Meta-learning skills


class SkillLevel(Enum):
    """Skill proficiency levels."""
    NOVICE = "novice"               # 0-20%
    BEGINNER = "beginner"           # 20-40%
    INTERMEDIATE = "intermediate"   # 40-60%
    ADVANCED = "advanced"           # 60-80%
    EXPERT = "expert"               # 80-95%
    MASTER = "master"               # 95-100%
    
    @staticmethod
    def from_proficiency(proficiency: float) -> "SkillLevel":
        if proficiency < 0.2:
            return SkillLevel.NOVICE
        elif proficiency < 0.4:
            return SkillLevel.BEGINNER
        elif proficiency < 0.6:
            return SkillLevel.INTERMEDIATE
        elif proficiency < 0.8:
            return SkillLevel.ADVANCED
        elif proficiency < 0.95:
            return SkillLevel.EXPERT
        else:
            return SkillLevel.MASTER


@dataclass
class Skill:
    """Represents a single skill in the tree."""
    skill_id: str
    name: str
    description: str
    category: SkillCategory
    
    # Hierarchy
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    
    # Progress
    proficiency: float = 0.0        # 0.0 to 1.0
    experience_points: int = 0
    level: int = 1
    
    # Requirements
    prerequisites: List[str] = field(default_factory=list)
    xp_per_level: int = 100
    max_level: int = 10
    
    # Training
    training_sources: List[str] = field(default_factory=list)
    practice_count: int = 0
    last_practiced: str = ""
    
    # Performance
    success_rate: float = 0.0
    average_confidence: float = 0.5
    
    def get_level(self) -> SkillLevel:
        """Get the skill level enum."""
        return SkillLevel.from_proficiency(self.proficiency)
    
    def add_experience(self, xp: int, success: bool = True):
        """Add experience points to the skill."""
        self.experience_points += xp
        self.practice_count += 1
        self.last_practiced = datetime.now().isoformat()
        
        # Update proficiency based on XP
        xp_for_max = self.xp_per_level * self.max_level
        self.proficiency = min(1.0, self.experience_points / xp_for_max)
        
        # Update level
        self.level = min(self.max_level, 1 + self.experience_points // self.xp_per_level)
        
        # Update success rate (exponential moving average)
        outcome = 1.0 if success else 0.0
        self.success_rate = 0.95 * self.success_rate + 0.05 * outcome
        
    def prerequisites_met(self, skill_tree: "SkillTree") -> bool:
        """Check if prerequisites are met."""
        for prereq_id in self.prerequisites:
            prereq = skill_tree.get_skill(prereq_id)
            if not prereq or prereq.proficiency < 0.5:
                return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "proficiency": self.proficiency,
            "experience_points": self.experience_points,
            "level": self.level,
            "max_level": self.max_level,
            "skill_level": self.get_level().value,
            "prerequisites": self.prerequisites,
            "practice_count": self.practice_count,
            "success_rate": self.success_rate
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "Skill":
        skill = Skill(
            skill_id=data["skill_id"],
            name=data["name"],
            description=data["description"],
            category=SkillCategory(data["category"]),
            parent_id=data.get("parent_id"),
            child_ids=data.get("child_ids", []),
            proficiency=data.get("proficiency", 0.0),
            experience_points=data.get("experience_points", 0),
            level=data.get("level", 1),
            prerequisites=data.get("prerequisites", []),
            xp_per_level=data.get("xp_per_level", 100),
            max_level=data.get("max_level", 10),
            practice_count=data.get("practice_count", 0),
            success_rate=data.get("success_rate", 0.0)
        )
        return skill


@dataclass
class SkillPath:
    """A learning path through multiple skills."""
    path_id: str
    name: str
    description: str
    skill_sequence: List[str]       # Ordered skill IDs
    estimated_hours: int = 10
    difficulty: int = 1             # 1-5
    current_position: int = 0
    completed: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "path_id": self.path_id,
            "name": self.name,
            "description": self.description,
            "skill_sequence": self.skill_sequence,
            "estimated_hours": self.estimated_hours,
            "difficulty": self.difficulty,
            "current_position": self.current_position,
            "progress_percent": (self.current_position / len(self.skill_sequence) * 100) if self.skill_sequence else 0,
            "completed": self.completed
        }


class SkillTree:
    """
    Hierarchical skill tree for the daemon.
    
    Provides:
    - Skill registration and hierarchy
    - Experience and leveling system
    - Skill prerequisites and unlocking
    - Learning paths and recommendations
    - Skill transfer between domains
    """
    
    def __init__(self, data_path: str = "data/lam/skills"):
        self.data_path = data_path
        self.skills: Dict[str, Skill] = {}
        self.paths: Dict[str, SkillPath] = {}
        self.category_roots: Dict[str, List[str]] = {}  # category -> root skill IDs
        
        os.makedirs(data_path, exist_ok=True)
        self._load_tree()
        self._initialize_base_skills()
        print("[SkillTree] Initialized.")
        
    def _load_tree(self):
        """Load skill tree from disk."""
        tree_file = os.path.join(self.data_path, "skill_tree.json")
        if os.path.exists(tree_file):
            try:
                with open(tree_file, "r") as f:
                    data = json.load(f)
                    for s in data.get("skills", []):
                        skill = Skill.from_dict(s)
                        self.skills[skill.skill_id] = skill
                        
                    for p in data.get("paths", []):
                        path = SkillPath(
                            path_id=p["path_id"],
                            name=p["name"],
                            description=p["description"],
                            skill_sequence=p["skill_sequence"],
                            estimated_hours=p.get("estimated_hours", 10),
                            difficulty=p.get("difficulty", 1),
                            current_position=p.get("current_position", 0)
                        )
                        self.paths[path.path_id] = path
                        
                print(f"[SkillTree] Loaded {len(self.skills)} skills, {len(self.paths)} paths")
            except Exception as e:
                print(f"[SkillTree] Error loading tree: {e}")
                
    def _save_tree(self):
        """Save skill tree to disk."""
        tree_file = os.path.join(self.data_path, "skill_tree.json")
        data = {
            "skills": [s.to_dict() for s in self.skills.values()],
            "paths": [p.to_dict() for p in self.paths.values()],
            "saved_at": datetime.now().isoformat()
        }
        with open(tree_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _initialize_base_skills(self):
        """Initialize base skill tree structure."""
        base_skills = [
            # Cognitive root and children
            Skill("cog_root", "Cognitive Processing", "Core reasoning and analysis", SkillCategory.COGNITIVE),
            Skill("cog_logic", "Logical Reasoning", "Formal logic and deduction", SkillCategory.COGNITIVE, parent_id="cog_root"),
            Skill("cog_analysis", "Analysis", "Breaking down complex problems", SkillCategory.COGNITIVE, parent_id="cog_root"),
            Skill("cog_planning", "Planning", "Multi-step planning", SkillCategory.COGNITIVE, parent_id="cog_root"),
            Skill("cog_learning", "Meta-Learning", "Learning to learn", SkillCategory.COGNITIVE, parent_id="cog_root"),
            
            # Language root and children
            Skill("lang_root", "Language Understanding", "Natural language processing", SkillCategory.LANGUAGE),
            Skill("lang_intent", "Intent Recognition", "Understanding user intent", SkillCategory.LANGUAGE, parent_id="lang_root"),
            Skill("lang_context", "Context Understanding", "Contextual interpretation", SkillCategory.LANGUAGE, parent_id="lang_root"),
            Skill("lang_generation", "Text Generation", "Generating coherent text", SkillCategory.LANGUAGE, parent_id="lang_root"),
            
            # Action root and children
            Skill("act_root", "Action Execution", "Executing tasks and actions", SkillCategory.ACTION),
            Skill("act_scroll", "Scroll Invocation", "Triggering scrolls and rituals", SkillCategory.ACTION, parent_id="act_root"),
            Skill("act_task", "Task Execution", "General task execution", SkillCategory.ACTION, parent_id="act_root"),
            Skill("act_sequence", "Action Sequencing", "Multi-step action execution", SkillCategory.ACTION, parent_id="act_root"),
            
            # Knowledge root and children
            Skill("know_root", "Knowledge Management", "Managing and applying knowledge", SkillCategory.KNOWLEDGE),
            Skill("know_retrieval", "Knowledge Retrieval", "Finding relevant knowledge", SkillCategory.KNOWLEDGE, parent_id="know_root"),
            Skill("know_integration", "Knowledge Integration", "Combining knowledge sources", SkillCategory.KNOWLEDGE, parent_id="know_root"),
            Skill("know_application", "Knowledge Application", "Applying knowledge to problems", SkillCategory.KNOWLEDGE, parent_id="know_root"),
            
            # Technical root and children
            Skill("tech_root", "Technical Skills", "Programming and technical abilities", SkillCategory.TECHNICAL),
            Skill("tech_python", "Python Programming", "Python coding skills", SkillCategory.TECHNICAL, parent_id="tech_root"),
            Skill("tech_code_gen", "Code Generation", "Generating code from descriptions", SkillCategory.TECHNICAL, parent_id="tech_root"),
            Skill("tech_debug", "Debugging", "Finding and fixing bugs", SkillCategory.TECHNICAL, parent_id="tech_root"),
            
            # XR root and children
            Skill("xr_root", "XR Capabilities", "AR/VR/MR skills", SkillCategory.XR),
            Skill("xr_spatial", "Spatial Understanding", "3D spatial awareness", SkillCategory.XR, parent_id="xr_root"),
            Skill("xr_gesture", "Gesture Recognition", "Hand and body gesture understanding", SkillCategory.XR, parent_id="xr_root"),
            Skill("xr_overlay", "AR Overlay Management", "Creating and managing AR content", SkillCategory.XR, parent_id="xr_root"),
            Skill("xr_training", "XR Training Delivery", "Delivering training in XR", SkillCategory.XR, parent_id="xr_root"),
            
            # Creative root and children
            Skill("create_root", "Creative Abilities", "Creative generation skills", SkillCategory.CREATIVE),
            Skill("create_writing", "Creative Writing", "Story and content generation", SkillCategory.CREATIVE, parent_id="create_root"),
            Skill("create_design", "Design Thinking", "Creative problem solving", SkillCategory.CREATIVE, parent_id="create_root"),
        ]
        
        # Add base skills if not already present
        for skill in base_skills:
            if skill.skill_id not in self.skills:
                self.skills[skill.skill_id] = skill
                
                # Update parent's child list
                if skill.parent_id and skill.parent_id in self.skills:
                    parent = self.skills[skill.parent_id]
                    if skill.skill_id not in parent.child_ids:
                        parent.child_ids.append(skill.skill_id)
                        
        # Build category roots index
        for skill in self.skills.values():
            if skill.parent_id is None:
                cat = skill.category.value
                if cat not in self.category_roots:
                    self.category_roots[cat] = []
                if skill.skill_id not in self.category_roots[cat]:
                    self.category_roots[cat].append(skill.skill_id)
                    
        # Initialize learning paths
        self._initialize_paths()
        self._save_tree()
        
    def _initialize_paths(self):
        """Initialize default learning paths."""
        default_paths = [
            SkillPath(
                path_id="path_core",
                name="Core Competencies",
                description="Foundation skills for the daemon",
                skill_sequence=["cog_logic", "lang_intent", "act_task", "know_retrieval"],
                estimated_hours=20,
                difficulty=1
            ),
            SkillPath(
                path_id="path_xr",
                name="XR Mastery",
                description="Complete AR/VR/XR skill development",
                skill_sequence=["xr_spatial", "xr_gesture", "xr_overlay", "xr_training"],
                estimated_hours=30,
                difficulty=2
            ),
            SkillPath(
                path_id="path_technical",
                name="Technical Excellence",
                description="Advanced technical and coding skills",
                skill_sequence=["tech_python", "tech_code_gen", "tech_debug", "cog_analysis"],
                estimated_hours=40,
                difficulty=3
            ),
            SkillPath(
                path_id="path_learning",
                name="Self-Improvement",
                description="Meta-learning and self-optimization",
                skill_sequence=["cog_learning", "know_integration", "cog_planning", "act_sequence"],
                estimated_hours=25,
                difficulty=2
            ),
        ]
        
        for path in default_paths:
            if path.path_id not in self.paths:
                self.paths[path.path_id] = path
                
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        return self.skills.get(skill_id)
    
    def add_skill(
        self,
        name: str,
        description: str,
        category: str,
        parent_id: Optional[str] = None,
        prerequisites: Optional[List[str]] = None
    ) -> Skill:
        """Add a new skill to the tree."""
        skill_id = f"skill_{name.lower().replace(' ', '_')}"
        
        skill = Skill(
            skill_id=skill_id,
            name=name,
            description=description,
            category=SkillCategory(category),
            parent_id=parent_id,
            prerequisites=prerequisites or []
        )
        
        self.skills[skill_id] = skill
        
        # Update parent's child list
        if parent_id and parent_id in self.skills:
            parent = self.skills[parent_id]
            if skill_id not in parent.child_ids:
                parent.child_ids.append(skill_id)
                
        self._save_tree()
        print(f"[SkillTree] Added skill: {name}")
        return skill
    
    def train_skill(
        self,
        skill_id: str,
        xp_earned: int,
        success: bool = True,
        source: str = "practice"
    ) -> Optional[Dict]:
        """
        Train a skill by adding experience.
        
        Args:
            skill_id: Skill to train
            xp_earned: Experience points earned
            success: Whether the training was successful
            source: Source of training (practice, demonstration, etc.)
            
        Returns:
            Training result with level changes
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return None
            
        old_level = skill.level
        old_proficiency = skill.proficiency
        
        skill.add_experience(xp_earned, success)
        skill.training_sources.append(source)
        
        # Propagate partial XP to parent skill
        if skill.parent_id and skill.parent_id in self.skills:
            parent = self.skills[skill.parent_id]
            parent.add_experience(xp_earned // 4, success)  # 25% XP to parent
            
        self._save_tree()
        
        result = {
            "skill_id": skill_id,
            "skill_name": skill.name,
            "xp_earned": xp_earned,
            "success": success,
            "old_level": old_level,
            "new_level": skill.level,
            "level_up": skill.level > old_level,
            "old_proficiency": old_proficiency,
            "new_proficiency": skill.proficiency,
            "skill_level": skill.get_level().value
        }
        
        if skill.level > old_level:
            print(f"[SkillTree] Level up! {skill.name}: {old_level} -> {skill.level}")
            
        return result
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category."""
        return [s for s in self.skills.values() if s.category.value == category]
    
    def get_skill_hierarchy(self, root_id: str) -> Dict:
        """Get hierarchical representation of skills under a root."""
        skill = self.skills.get(root_id)
        if not skill:
            return {}
            
        def build_tree(skill_id: str) -> Dict:
            s = self.skills.get(skill_id)
            if not s:
                return {}
            return {
                "id": s.skill_id,
                "name": s.name,
                "level": s.level,
                "proficiency": s.proficiency,
                "children": [build_tree(cid) for cid in s.child_ids]
            }
            
        return build_tree(root_id)
    
    def get_available_skills(self) -> List[Skill]:
        """Get skills that can be trained (prerequisites met)."""
        available = []
        for skill in self.skills.values():
            if skill.prerequisites_met(self):
                available.append(skill)
        return available
    
    def get_locked_skills(self) -> List[Tuple[Skill, List[str]]]:
        """Get skills that are locked and what's needed to unlock them."""
        locked = []
        for skill in self.skills.values():
            if not skill.prerequisites_met(self):
                missing = []
                for prereq_id in skill.prerequisites:
                    prereq = self.get_skill(prereq_id)
                    if prereq and prereq.proficiency < 0.5:
                        missing.append(prereq.name)
                locked.append((skill, missing))
        return locked
    
    def get_recommended_training(self, top_k: int = 5) -> List[Skill]:
        """Get recommended skills to train next."""
        available = self.get_available_skills()
        
        # Score skills by various factors
        scored = []
        for skill in available:
            score = 0
            
            # Prefer skills with low proficiency
            score += (1 - skill.proficiency) * 0.3
            
            # Prefer skills with more children (more foundational)
            score += min(len(skill.child_ids) * 0.1, 0.2)
            
            # Prefer skills not recently practiced
            if skill.last_practiced:
                last = datetime.fromisoformat(skill.last_practiced)
                days_ago = (datetime.now() - last).days
                score += min(days_ago * 0.05, 0.2)
            else:
                score += 0.2  # Never practiced
                
            # Prefer skills with good success rate (not too frustrating)
            if skill.practice_count > 0:
                score += skill.success_rate * 0.2
            else:
                score += 0.1  # New skill
                
            scored.append((skill, score))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:top_k]]
    
    def get_learning_path(self, path_id: str) -> Optional[SkillPath]:
        """Get a learning path."""
        return self.paths.get(path_id)
    
    def advance_path(self, path_id: str) -> Optional[Dict]:
        """Advance to the next skill in a learning path."""
        path = self.paths.get(path_id)
        if not path or path.completed:
            return None
            
        if path.current_position < len(path.skill_sequence):
            current_skill_id = path.skill_sequence[path.current_position]
            current_skill = self.skills.get(current_skill_id)
            
            if current_skill and current_skill.proficiency >= 0.6:  # 60% to advance
                path.current_position += 1
                
                if path.current_position >= len(path.skill_sequence):
                    path.completed = True
                    print(f"[SkillTree] Path completed: {path.name}")
                    
                self._save_tree()
                
                return {
                    "path": path.name,
                    "advanced": True,
                    "new_position": path.current_position,
                    "completed": path.completed,
                    "next_skill": path.skill_sequence[path.current_position] if not path.completed else None
                }
            else:
                return {
                    "path": path.name,
                    "advanced": False,
                    "current_skill": current_skill_id,
                    "required_proficiency": 0.6,
                    "current_proficiency": current_skill.proficiency if current_skill else 0
                }
                
        return None
    
    def transfer_skill(
        self,
        source_skill_id: str,
        target_skill_id: str,
        transfer_rate: float = 0.3
    ) -> Optional[Dict]:
        """
        Transfer learning from one skill to a related skill.
        
        Args:
            source_skill_id: Skill to transfer from
            target_skill_id: Skill to transfer to
            transfer_rate: How much XP transfers (0-1)
            
        Returns:
            Transfer result
        """
        source = self.skills.get(source_skill_id)
        target = self.skills.get(target_skill_id)
        
        if not source or not target:
            return None
            
        # Calculate transferable XP
        transfer_xp = int(source.experience_points * transfer_rate)
        
        if transfer_xp > 0:
            old_level = target.level
            target.add_experience(transfer_xp, success=True)
            
            self._save_tree()
            
            return {
                "source": source.name,
                "target": target.name,
                "xp_transferred": transfer_xp,
                "target_old_level": old_level,
                "target_new_level": target.level,
                "level_up": target.level > old_level
            }
            
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get skill tree statistics."""
        total_xp = sum(s.experience_points for s in self.skills.values())
        avg_proficiency = sum(s.proficiency for s in self.skills.values()) / len(self.skills) if self.skills else 0
        
        level_distribution = {}
        for skill in self.skills.values():
            level = skill.get_level().value
            level_distribution[level] = level_distribution.get(level, 0) + 1
            
        category_proficiency = {}
        for cat in SkillCategory:
            skills = self.get_skills_by_category(cat.value)
            if skills:
                category_proficiency[cat.value] = sum(s.proficiency for s in skills) / len(skills)
                
        return {
            "total_skills": len(self.skills),
            "total_xp": total_xp,
            "average_proficiency": avg_proficiency,
            "level_distribution": level_distribution,
            "category_proficiency": category_proficiency,
            "paths_completed": sum(1 for p in self.paths.values() if p.completed),
            "total_paths": len(self.paths)
        }
    
    def export_tree(self) -> Dict:
        """Export the skill tree."""
        return {
            "skills": [s.to_dict() for s in self.skills.values()],
            "paths": [p.to_dict() for p in self.paths.values()],
            "statistics": self.get_statistics()
        }
