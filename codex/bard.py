import os
import ast

class TheBard:
    def __init__(self):
        pass

    def scribe_legend(self, target_path, output_path="LEGENDS.md"):
        """
        Reads python files in target_path and generates a Mythological Documentation file.
        """
        if not os.path.exists(target_path):
            return "Path not found."

        legends = ["# The Chronicles of Code\n"]
        
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, target_path)
                    
                    try:
                        with open(full_path, "r") as f:
                            tree = ast.parse(f.read())
                            
                        file_legend = self._interpret_file(rel_path, tree)
                        legends.append(file_legend)
                    except Exception as e:
                        print(f"[Bard] Could not sing of {file}: {e}")

        with open(output_path, "w") as f:
            f.write("\n".join(legends))
            
        return f"Legends written to {output_path}"

    def _interpret_file(self, filename, tree):
        lines = [f"\n## The Scroll of {filename}\n"]
        
        doc = ast.get_docstring(tree)
        if doc:
            lines.append(f"> *{doc.strip()}*\n")

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                lines.append(f"### The Temple of **{node.name}**")
                class_doc = ast.get_docstring(node)
                if class_doc:
                    lines.append(f"_{class_doc.strip()}_\n")
                
                # Methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith("__"): continue
                        lines.append(f"- **Ritual {item.name}**: {self._describe_args(item.args)}")
                        
            elif isinstance(node, ast.FunctionDef):
                lines.append(f"### The Spell **{node.name}**")
                func_doc = ast.get_docstring(node)
                if func_doc:
                    lines.append(f"_{func_doc.strip()}_\n")
                lines.append(f"Invoked with: {self._describe_args(node.args)}")

        return "\n".join(lines)

    def _describe_args(self, args):
        arg_names = [a.arg for a in args.args if a.arg != "self"]
        if not arg_names:
            return "No offerings required."
        return ", ".join([f"_{a}_" for a in arg_names])
