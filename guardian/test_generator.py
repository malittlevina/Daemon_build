# guardian/test_generator.py
"""
Test Generator - Automatic test case generation

Provides:
- Unit test scaffolding
- Property-based test suggestions
- Edge case detection
- Test coverage analysis
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import ast
import os
import re


@dataclass
class TestCase:
    """A generated test case."""
    name: str
    function_under_test: str
    test_type: str  # unit, property, edge_case
    description: str
    code: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_behavior: str = ""
    priority: int = 1


@dataclass
class TestSuite:
    """Collection of test cases for a module."""
    module_name: str
    file_path: str
    test_cases: List[TestCase]
    imports: List[str]
    setup_code: str = ""
    teardown_code: str = ""


class TestGenerator:
    """
    Generates test cases from code analysis.
    
    Features:
    - Function signature analysis
    - Type hint extraction
    - Edge case identification
    - Test template generation
    """
    
    def __init__(self):
        self.type_examples = {
            "str": ['""', '"test"', '"hello world"', 'None'],
            "int": ["0", "1", "-1", "1000000", "None"],
            "float": ["0.0", "1.0", "-1.0", "float('inf')", "None"],
            "bool": ["True", "False"],
            "list": ["[]", "[1, 2, 3]", '["a", "b"]', "None"],
            "dict": ["{}", '{"key": "value"}', "None"],
            "Optional": ["None"],
        }
        
        self.edge_case_patterns = {
            "str": ["empty string", "very long string", "unicode characters", "special characters"],
            "int": ["zero", "negative", "very large", "boundary values"],
            "float": ["zero", "negative", "infinity", "NaN"],
            "list": ["empty list", "single element", "many elements", "nested lists"],
            "dict": ["empty dict", "nested dict", "missing keys"],
        }
    
    def generate_tests(
        self,
        file_path: str,
        output_path: str = None
    ) -> TestSuite:
        """Generate tests for a Python file."""
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        module_name = os.path.basename(file_path).replace(".py", "")
        
        test_cases = []
        imports = self._extract_imports(tree, module_name, file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions and test functions
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                if node.name.startswith("test_"):
                    continue
                
                cases = self._generate_function_tests(node, module_name)
                test_cases.extend(cases)
            
            elif isinstance(node, ast.ClassDef):
                cases = self._generate_class_tests(node, module_name)
                test_cases.extend(cases)
        
        suite = TestSuite(
            module_name=module_name,
            file_path=file_path,
            test_cases=test_cases,
            imports=imports
        )
        
        if output_path:
            self._write_test_file(suite, output_path)
        
        return suite
    
    def _generate_function_tests(
        self,
        node: ast.FunctionDef,
        module_name: str
    ) -> List[TestCase]:
        """Generate tests for a function."""
        cases = []
        func_name = node.name
        
        # Extract parameter info
        params = self._extract_parameters(node)
        return_type = self._extract_return_type(node)
        
        # Get docstring for understanding
        docstring = ast.get_docstring(node) or ""
        
        # 1. Basic functionality test
        cases.append(self._generate_basic_test(func_name, params, docstring, module_name))
        
        # 2. Edge case tests
        edge_cases = self._generate_edge_case_tests(func_name, params, module_name)
        cases.extend(edge_cases)
        
        # 3. Type validation test (if type hints present)
        if params:
            cases.append(self._generate_type_test(func_name, params, module_name))
        
        # 4. Error handling test
        cases.append(self._generate_error_test(func_name, params, module_name))
        
        return cases
    
    def _generate_class_tests(
        self,
        node: ast.ClassDef,
        module_name: str
    ) -> List[TestCase]:
        """Generate tests for a class."""
        cases = []
        class_name = node.name
        
        # Test class instantiation
        cases.append(TestCase(
            name=f"test_{class_name.lower()}_instantiation",
            function_under_test=class_name,
            test_type="unit",
            description=f"Test that {class_name} can be instantiated",
            code=self._generate_class_instantiation_test(class_name, node, module_name)
        ))
        
        # Test each public method
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                method_cases = self._generate_method_tests(class_name, item, module_name)
                cases.extend(method_cases)
        
        return cases
    
    def _generate_method_tests(
        self,
        class_name: str,
        node: ast.FunctionDef,
        module_name: str
    ) -> List[TestCase]:
        """Generate tests for a class method."""
        cases = []
        method_name = node.name
        params = self._extract_parameters(node)
        
        # Remove 'self' from params
        params = [(n, t, d) for n, t, d in params if n != "self"]
        
        cases.append(TestCase(
            name=f"test_{class_name.lower()}_{method_name}",
            function_under_test=f"{class_name}.{method_name}",
            test_type="unit",
            description=f"Test {class_name}.{method_name} method",
            code=self._generate_method_test_code(class_name, method_name, params, module_name)
        ))
        
        return cases
    
    def _extract_parameters(
        self,
        node: ast.FunctionDef
    ) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """Extract parameter info: (name, type_hint, default)."""
        params = []
        
        # Get type annotations
        for arg in node.args.args:
            name = arg.arg
            type_hint = None
            
            if arg.annotation:
                type_hint = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else None
            
            params.append((name, type_hint, None))
        
        # Add defaults
        defaults = node.args.defaults
        num_defaults = len(defaults)
        num_params = len(params)
        
        for i, default in enumerate(defaults):
            param_idx = num_params - num_defaults + i
            if param_idx >= 0:
                name, type_hint, _ = params[param_idx]
                default_val = ast.unparse(default) if hasattr(ast, 'unparse') else "..."
                params[param_idx] = (name, type_hint, default_val)
        
        return params
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else None
        return None
    
    def _extract_imports(
        self,
        tree: ast.Module,
        module_name: str,
        file_path: str
    ) -> List[str]:
        """Generate import statements for test file."""
        imports = [
            "import pytest",
            "import unittest",
        ]
        
        # Import the module under test
        # Construct relative import based on file path
        rel_path = os.path.relpath(file_path, start=os.getcwd())
        module_path = rel_path.replace(os.sep, ".").replace(".py", "")
        imports.append(f"from {module_path} import *")
        
        return imports
    
    def _generate_basic_test(
        self,
        func_name: str,
        params: List[Tuple[str, Optional[str], Optional[str]]],
        docstring: str,
        module_name: str
    ) -> TestCase:
        """Generate a basic functionality test."""
        # Generate sample arguments
        args = self._generate_sample_args(params)
        args_str = ", ".join(f"{k}={v}" for k, v in args.items())
        
        code = f'''def test_{func_name}_basic():
    """Test basic functionality of {func_name}."""
    # Arrange
    {self._generate_arrange_section(params)}
    
    # Act
    result = {func_name}({args_str})
    
    # Assert
    assert result is not None  # TODO: Add specific assertions
'''
        
        return TestCase(
            name=f"test_{func_name}_basic",
            function_under_test=func_name,
            test_type="unit",
            description=f"Test basic functionality of {func_name}",
            code=code,
            inputs=args
        )
    
    def _generate_edge_case_tests(
        self,
        func_name: str,
        params: List[Tuple[str, Optional[str], Optional[str]]],
        module_name: str
    ) -> List[TestCase]:
        """Generate edge case tests."""
        cases = []
        
        for param_name, type_hint, default in params:
            if type_hint and type_hint in self.edge_case_patterns:
                for edge_case in self.edge_case_patterns[type_hint][:2]:
                    case_name = f"test_{func_name}_{param_name}_{edge_case.replace(' ', '_')}"
                    
                    cases.append(TestCase(
                        name=case_name,
                        function_under_test=func_name,
                        test_type="edge_case",
                        description=f"Test {func_name} with {edge_case} for {param_name}",
                        code=self._generate_edge_case_code(func_name, param_name, type_hint, edge_case),
                        priority=2
                    ))
        
        return cases
    
    def _generate_type_test(
        self,
        func_name: str,
        params: List[Tuple[str, Optional[str], Optional[str]]],
        module_name: str
    ) -> TestCase:
        """Generate type validation test."""
        code = f'''def test_{func_name}_type_validation():
    """Test that {func_name} handles incorrect types appropriately."""
    with pytest.raises((TypeError, ValueError)):
        {func_name}(None)  # TODO: Adjust based on function signature
'''
        
        return TestCase(
            name=f"test_{func_name}_type_validation",
            function_under_test=func_name,
            test_type="unit",
            description=f"Test type validation for {func_name}",
            code=code
        )
    
    def _generate_error_test(
        self,
        func_name: str,
        params: List[Tuple[str, Optional[str], Optional[str]]],
        module_name: str
    ) -> TestCase:
        """Generate error handling test."""
        code = f'''def test_{func_name}_error_handling():
    """Test that {func_name} handles errors gracefully."""
    # TODO: Add tests for error conditions
    pass
'''
        
        return TestCase(
            name=f"test_{func_name}_error_handling",
            function_under_test=func_name,
            test_type="unit",
            description=f"Test error handling for {func_name}",
            code=code,
            priority=3
        )
    
    def _generate_class_instantiation_test(
        self,
        class_name: str,
        node: ast.ClassDef,
        module_name: str
    ) -> str:
        """Generate class instantiation test code."""
        # Find __init__ method
        init_params = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_params = self._extract_parameters(item)
                init_params = [(n, t, d) for n, t, d in init_params if n != "self"]
                break
        
        args = self._generate_sample_args(init_params)
        args_str = ", ".join(f"{k}={v}" for k, v in args.items())
        
        return f'''def test_{class_name.lower()}_instantiation():
    """Test that {class_name} can be instantiated."""
    instance = {class_name}({args_str})
    assert instance is not None
    assert isinstance(instance, {class_name})
'''
    
    def _generate_method_test_code(
        self,
        class_name: str,
        method_name: str,
        params: List[Tuple[str, Optional[str], Optional[str]]],
        module_name: str
    ) -> str:
        """Generate method test code."""
        args = self._generate_sample_args(params)
        args_str = ", ".join(f"{k}={v}" for k, v in args.items())
        
        return f'''def test_{class_name.lower()}_{method_name}():
    """Test {class_name}.{method_name} method."""
    # Arrange
    instance = {class_name}()  # TODO: Add constructor args if needed
    
    # Act
    result = instance.{method_name}({args_str})
    
    # Assert
    assert result is not None  # TODO: Add specific assertions
'''
    
    def _generate_arrange_section(
        self,
        params: List[Tuple[str, Optional[str], Optional[str]]]
    ) -> str:
        """Generate the arrange section of a test."""
        lines = []
        for name, type_hint, default in params:
            if default:
                lines.append(f"# {name} has default: {default}")
            elif type_hint:
                example = self._get_type_example(type_hint)
                lines.append(f"{name} = {example}")
        
        return "\n    ".join(lines) if lines else "# No parameters to arrange"
    
    def _generate_sample_args(
        self,
        params: List[Tuple[str, Optional[str], Optional[str]]]
    ) -> Dict[str, str]:
        """Generate sample arguments for function call."""
        args = {}
        for name, type_hint, default in params:
            if name in ("self", "cls"):
                continue
            
            if default:
                continue  # Skip parameters with defaults
            
            args[name] = self._get_type_example(type_hint or "str")
        
        return args
    
    def _get_type_example(self, type_hint: str) -> str:
        """Get example value for a type."""
        # Handle Optional types
        if type_hint.startswith("Optional["):
            inner = type_hint[9:-1]
            return self._get_type_example(inner)
        
        # Handle List types
        if type_hint.startswith("List["):
            return "[]"
        
        # Handle Dict types
        if type_hint.startswith("Dict["):
            return "{}"
        
        # Basic types
        if type_hint in self.type_examples:
            return self.type_examples[type_hint][1]  # Return first non-empty example
        
        return '""'  # Default to empty string
    
    def _generate_edge_case_code(
        self,
        func_name: str,
        param_name: str,
        type_hint: str,
        edge_case: str
    ) -> str:
        """Generate edge case test code."""
        edge_values = {
            "empty string": '""',
            "very long string": '"a" * 10000',
            "unicode characters": '"こんにちは"',
            "special characters": '"!@#$%^&*()"',
            "zero": "0",
            "negative": "-1",
            "very large": "10**18",
            "boundary values": "sys.maxsize",
            "infinity": "float('inf')",
            "NaN": "float('nan')",
            "empty list": "[]",
            "single element": "[1]",
            "many elements": "list(range(1000))",
            "nested lists": "[[1, 2], [3, 4]]",
            "empty dict": "{}",
            "nested dict": '{"a": {"b": 1}}',
            "missing keys": "{}",
        }
        
        value = edge_values.get(edge_case, '""')
        
        return f'''def test_{func_name}_{param_name}_{edge_case.replace(" ", "_")}():
    """Test {func_name} with {edge_case} for {param_name}."""
    {param_name} = {value}
    # TODO: Add test logic
    try:
        result = {func_name}({param_name}={param_name})
        # Assert expected behavior
    except Exception as e:
        # Document expected exception behavior
        pass
'''
    
    def _write_test_file(self, suite: TestSuite, output_path: str):
        """Write test suite to file."""
        lines = [
            f'"""Generated tests for {suite.module_name}."""',
            "",
        ]
        
        # Add imports
        lines.extend(suite.imports)
        lines.append("")
        lines.append("")
        
        # Add test cases
        for case in suite.test_cases:
            lines.append(case.code)
            lines.append("")
        
        # Add main block
        lines.append('if __name__ == "__main__":')
        lines.append('    pytest.main([__file__, "-v"])')
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"[TestGenerator] Generated {len(suite.test_cases)} tests to {output_path}")
