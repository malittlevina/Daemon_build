# guardian/code_analyzer.py
"""
Code Analyzer - AST-based code analysis and improvement suggestions

Provides:
- Code structure analysis
- Complexity metrics
- Pattern detection
- Improvement recommendations
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import ast
import os
import re


class IssueType(Enum):
    """Types of code issues."""
    COMPLEXITY = "complexity"
    STYLE = "style"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


class Severity(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CodeIssue:
    """A detected code issue."""
    issue_type: IssueType
    severity: Severity
    message: str
    file_path: str
    line_number: int
    code_snippet: str = ""
    suggestion: str = ""
    fix_available: bool = False


@dataclass
class FunctionMetrics:
    """Metrics for a function."""
    name: str
    file_path: str
    line_start: int
    line_end: int
    parameters: int
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    has_docstring: bool
    return_statements: int
    nested_depth: int
    calls: List[str] = field(default_factory=list)


@dataclass
class ClassMetrics:
    """Metrics for a class."""
    name: str
    file_path: str
    line_start: int
    line_end: int
    methods: int
    attributes: int
    inheritance_depth: int
    has_docstring: bool
    public_methods: int
    private_methods: int


@dataclass
class ModuleMetrics:
    """Metrics for a module/file."""
    file_path: str
    lines_of_code: int
    blank_lines: int
    comment_lines: int
    functions: List[FunctionMetrics]
    classes: List[ClassMetrics]
    imports: List[str]
    global_variables: int
    complexity_score: float


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate complexity metrics."""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.max_nesting = 0
        self.return_count = 0
        self.calls = []
    
    def visit_If(self, node):
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._visit_with_nesting(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._visit_with_nesting(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._visit_with_nesting(node)
    
    def visit_Try(self, node):
        self.complexity += len(node.handlers)
        self.cognitive_complexity += 1 + self.nesting_depth
        self._visit_with_nesting(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        self._visit_with_nesting(node)
    
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_Return(self, node):
        self.return_count += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)
    
    def _visit_with_nesting(self, node):
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1


class CodeAnalyzer:
    """
    Analyzes code structure and quality.
    
    Features:
    - AST-based analysis
    - Complexity metrics
    - Pattern detection
    - Issue identification
    """
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.metrics: Dict[str, ModuleMetrics] = {}
        
        # Thresholds for issues
        self.thresholds = {
            "cyclomatic_complexity": 10,
            "cognitive_complexity": 15,
            "function_lines": 50,
            "function_parameters": 5,
            "nesting_depth": 4,
            "class_methods": 20,
            "file_lines": 500
        }
    
    def analyze_file(self, file_path: str) -> ModuleMetrics:
        """Analyze a Python file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        return self.analyze_source(source, file_path)
    
    def analyze_source(self, source: str, file_path: str = "<string>") -> ModuleMetrics:
        """Analyze Python source code."""
        lines = source.split("\n")
        
        # Count line types
        loc = 0
        blank = 0
        comments = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank += 1
            elif stripped.startswith("#"):
                comments += 1
            else:
                loc += 1
        
        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                issue_type=IssueType.STYLE,
                severity=Severity.ERROR,
                message=f"Syntax error: {e}",
                file_path=file_path,
                line_number=e.lineno or 0
            ))
            return ModuleMetrics(
                file_path=file_path,
                lines_of_code=loc,
                blank_lines=blank,
                comment_lines=comments,
                functions=[],
                classes=[],
                imports=[],
                global_variables=0,
                complexity_score=0
            )
        
        # Analyze structure
        functions = []
        classes = []
        imports = []
        global_vars = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_nested_function(node, tree):
                    metrics = self._analyze_function(node, source, file_path)
                    functions.append(metrics)
                    self._check_function_issues(metrics)
            
            elif isinstance(node, ast.ClassDef):
                metrics = self._analyze_class(node, source, file_path)
                classes.append(metrics)
                self._check_class_issues(metrics)
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(self._extract_imports(node))
            
            elif isinstance(node, ast.Assign):
                if all(isinstance(t, ast.Name) for t in node.targets):
                    global_vars += len(node.targets)
        
        # Calculate overall complexity
        total_complexity = sum(f.cyclomatic_complexity for f in functions)
        complexity_score = total_complexity / max(1, len(functions))
        
        # Check module-level issues
        if loc > self.thresholds["file_lines"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.WARNING,
                message=f"File has {loc} lines, consider splitting",
                file_path=file_path,
                line_number=1,
                suggestion="Split into smaller, focused modules"
            ))
        
        metrics = ModuleMetrics(
            file_path=file_path,
            lines_of_code=loc,
            blank_lines=blank,
            comment_lines=comments,
            functions=functions,
            classes=classes,
            imports=imports,
            global_variables=global_vars,
            complexity_score=complexity_score
        )
        
        self.metrics[file_path] = metrics
        return metrics
    
    def _analyze_function(
        self,
        node: ast.FunctionDef,
        source: str,
        file_path: str
    ) -> FunctionMetrics:
        """Analyze a function definition."""
        # Calculate complexity
        visitor = ComplexityVisitor()
        visitor.visit(node)
        
        # Get docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)
        )
        
        return FunctionMetrics(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=len(node.args.args) + len(node.args.kwonlyargs),
            lines_of_code=(node.end_lineno or node.lineno) - node.lineno + 1,
            cyclomatic_complexity=visitor.complexity,
            cognitive_complexity=visitor.cognitive_complexity,
            has_docstring=has_docstring,
            return_statements=visitor.return_count,
            nested_depth=visitor.max_nesting,
            calls=visitor.calls
        )
    
    def _analyze_class(
        self,
        node: ast.ClassDef,
        source: str,
        file_path: str
    ) -> ClassMetrics:
        """Analyze a class definition."""
        methods = 0
        public_methods = 0
        private_methods = 0
        attributes = 0
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods += 1
                if item.name.startswith("_"):
                    private_methods += 1
                else:
                    public_methods += 1
            elif isinstance(item, ast.Assign):
                attributes += len(item.targets)
        
        # Check for docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant)
        )
        
        # Calculate inheritance depth (simplified)
        inheritance_depth = len(node.bases)
        
        return ClassMetrics(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            attributes=attributes,
            inheritance_depth=inheritance_depth,
            has_docstring=has_docstring,
            public_methods=public_methods,
            private_methods=private_methods
        )
    
    def _is_nested_function(self, func_node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if function is nested inside another function."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node is not func_node:
                for child in ast.walk(node):
                    if child is func_node:
                        return True
        return False
    
    def _extract_imports(self, node) -> List[str]:
        """Extract import names."""
        imports = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
        return imports
    
    def _check_function_issues(self, metrics: FunctionMetrics):
        """Check for function-level issues."""
        if metrics.cyclomatic_complexity > self.thresholds["cyclomatic_complexity"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.COMPLEXITY,
                severity=Severity.WARNING,
                message=f"Function '{metrics.name}' has high cyclomatic complexity ({metrics.cyclomatic_complexity})",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Consider breaking into smaller functions"
            ))
        
        if metrics.cognitive_complexity > self.thresholds["cognitive_complexity"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.COMPLEXITY,
                severity=Severity.WARNING,
                message=f"Function '{metrics.name}' has high cognitive complexity ({metrics.cognitive_complexity})",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Reduce nesting and simplify logic"
            ))
        
        if metrics.lines_of_code > self.thresholds["function_lines"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.WARNING,
                message=f"Function '{metrics.name}' is too long ({metrics.lines_of_code} lines)",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Extract helper functions"
            ))
        
        if metrics.parameters > self.thresholds["function_parameters"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.INFO,
                message=f"Function '{metrics.name}' has many parameters ({metrics.parameters})",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Consider using a data class or keyword arguments"
            ))
        
        if not metrics.has_docstring:
            self.issues.append(CodeIssue(
                issue_type=IssueType.DOCUMENTATION,
                severity=Severity.INFO,
                message=f"Function '{metrics.name}' lacks docstring",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Add docstring describing purpose, parameters, and return value"
            ))
    
    def _check_class_issues(self, metrics: ClassMetrics):
        """Check for class-level issues."""
        if metrics.methods > self.thresholds["class_methods"]:
            self.issues.append(CodeIssue(
                issue_type=IssueType.MAINTAINABILITY,
                severity=Severity.WARNING,
                message=f"Class '{metrics.name}' has too many methods ({metrics.methods})",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Consider splitting into smaller classes"
            ))
        
        if not metrics.has_docstring:
            self.issues.append(CodeIssue(
                issue_type=IssueType.DOCUMENTATION,
                severity=Severity.INFO,
                message=f"Class '{metrics.name}' lacks docstring",
                file_path=metrics.file_path,
                line_number=metrics.line_start,
                suggestion="Add docstring describing the class purpose"
            ))
    
    def analyze_directory(
        self,
        directory: str,
        extensions: List[str] = None
    ) -> Dict[str, ModuleMetrics]:
        """Analyze all Python files in a directory."""
        extensions = extensions or [".py"]
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules", "venv", ".venv"}]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        metrics = self.analyze_file(file_path)
                        results[file_path] = metrics
                    except Exception as e:
                        print(f"[CodeAnalyzer] Error analyzing {file_path}: {e}")
        
        return results
    
    def get_issues(
        self,
        severity: Severity = None,
        issue_type: IssueType = None
    ) -> List[CodeIssue]:
        """Get filtered issues."""
        issues = self.issues
        
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        if issue_type:
            issues = [i for i in issues if i.issue_type == issue_type]
        
        return issues
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        total_loc = sum(m.lines_of_code for m in self.metrics.values())
        total_functions = sum(len(m.functions) for m in self.metrics.values())
        total_classes = sum(len(m.classes) for m in self.metrics.values())
        
        issue_counts = {}
        for issue in self.issues:
            key = issue.severity.value
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        avg_complexity = 0
        if total_functions > 0:
            avg_complexity = sum(
                f.cyclomatic_complexity
                for m in self.metrics.values()
                for f in m.functions
            ) / total_functions
        
        return {
            "files_analyzed": len(self.metrics),
            "total_lines_of_code": total_loc,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "average_complexity": round(avg_complexity, 2),
            "issue_counts": issue_counts,
            "total_issues": len(self.issues)
        }
    
    def clear(self):
        """Clear analysis results."""
        self.issues.clear()
        self.metrics.clear()
