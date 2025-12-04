import sys
import json
import argparse
import os
import subprocess
import shutil
import ast

def run_pylint(file_path):
    """
    Runs pylint on the given file and returns the raw JSON output.
    """
    # Try to run pylint as a module using the current python interpreter
    # This ensures we use the pylint installed in the same environment
    pylint_cmd = [sys.executable, "-m", "pylint"]

    cmd = pylint_cmd + ["--output-format=json", file_path]
    
    try:
        # Pylint returns non-zero exit codes if issues are found, so we ignore check=True
        # We need to specify encoding='utf-8' to handle potential encoding issues
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, encoding='utf-8')
        
        if result.stderr and not result.stdout:
             # Something went wrong with pylint execution itself (e.g. config error), but not just linting errors
             # However, pylint often prints config info to stderr, so be careful.
             # If stdout is empty, it's suspicious.
             pass
             
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # If output is empty or not JSON
            return []
            
    except Exception as e:
        sys.stderr.write(f"Failed to run pylint: {str(e)}\n")
        return []

def generate_cfg(node):
    """Generates a simple Mermaid flowchart for a function node."""
    lines = ["graph TD"]
    lines.append(f"Start((Start: {node.name}))")
    
    last_node = "Start"
    
    # Simplified CFG: just showing top-level statements in the function body
    for i, child in enumerate(node.body):
        node_id = f"S{i}"
        label = type(child).__name__
        
        if isinstance(child, ast.If):
            label = f"If Condition (Line {child.lineno})"
            shape_start, shape_end = "{", "}"
        elif isinstance(child, (ast.For, ast.While)):
            label = f"Loop (Line {child.lineno})"
            shape_start, shape_end = "((", "))"
        elif isinstance(child, ast.Return):
            label = "Return"
            shape_start, shape_end = "[/", "/]"
        else:
            # Group sequential simple statements? For now just list them
            if hasattr(child, 'lineno'):
                 label = f"{label} (Line {child.lineno})"
            shape_start, shape_end = "[", "]"
            
        lines.append(f'{node_id}{shape_start}"{label}"{shape_end}')
        lines.append(f"{last_node} --> {node_id}")
        last_node = node_id
        
    lines.append(f"{last_node} --> End((End))")
    return "\n".join(lines)

def generate_refactoring(source_code, node):
    """Generates a simulated refactoring preview."""
    # Find the largest block (If/For/While) to extract
    max_lines = 0
    target_child = None
    
    for child in node.body:
        if hasattr(child, 'end_lineno') and hasattr(child, 'lineno'):
            lines = child.end_lineno - child.lineno
            if lines > max_lines and isinstance(child, (ast.If, ast.For, ast.While)):
                max_lines = lines
                target_child = child
    
    if not target_child:
        return "No obvious complex block found to extract automatically."
        
    # Extract code
    lines = source_code.splitlines()
    # AST line numbers are 1-based
    start = target_child.lineno - 1
    end = target_child.end_lineno
    
    extracted_block = "\n".join(lines[start:end])
    
    # Create preview
    new_func_name = f"_extracted_helper_{target_child.lineno}"
    
    # Indentation for the call is tricky without more analysis, assuming 4 spaces
    call_stmt = f"    # REFACTORING SUGGESTION: Complex logic extracted to {new_func_name}\n    {new_func_name}()"
    
    # Reconstruct original function with replacement
    # Note: This is a visual simulation, not valid code generation (indentation might be off)
    
    preview = f"""# ---------------------------------------------------------
# SUGGESTED REFACTORING: EXTRACT METHOD
# ---------------------------------------------------------

def {node.name}(...):
    # ... (previous code) ...
{call_stmt}
    # ... (subsequent code) ...

# ---------------------------------------------------------
# NEW EXTRACTED FUNCTION
# ---------------------------------------------------------
def {new_func_name}():
{extracted_block}
"""
    return preview

def enrich_issues_with_analysis(file_path, issues):
    """
    Parses the file to find function definitions and enriches issues 
    with CFG and refactoring suggestions if applicable.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Map line numbers to FunctionDef nodes
        func_map = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_map[node.lineno] = node
                
        for issue in issues:
            # Check if issue is related to complexity or size
            msg = issue['message'].lower()
            # Pylint codes: R0915 (too many statements), R0912 (branches), R0914 (locals), R0913 (args)
            is_complexity_issue = any(x in msg for x in ['too many', 'statements', 'branches', 'complexity'])
            
            if is_complexity_issue:
                line = issue['line']
                # Find the function containing this line or starting at this line
                target_node = func_map.get(line)
                
                # If not found exactly, search upwards nearby
                if not target_node:
                    for l in range(line, max(0, line-5), -1):
                        if l in func_map:
                            target_node = func_map[l]
                            break
                
                if target_node:
                    issue['has_suggestion'] = True
                    issue['cfg'] = generate_cfg(target_node)
                    issue['refactoring'] = generate_refactoring(source, target_node)
                    
    except Exception as e:
        # Fail silently on AST errors
        pass
        
    return issues

def map_pylint_to_smell(pylint_issue):
    """
    Maps a Pylint issue to the format expected by the VS Code extension.
    """
    pylint_type = pylint_issue.get("type", "warning")
    
    # Map Pylint types to our severity levels
    severity_map = {
        "error": "Error",
        "fatal": "Error",
        "warning": "Warning",
        "convention": "Information",
        "refactor": "Information"
    }
    
    severity = severity_map.get(pylint_type, "Warning")
    
    return {
        "file": pylint_issue.get("path", ""),
        "line": pylint_issue.get("line", 1),
        "message": f"{pylint_issue.get('message')} ({pylint_issue.get('symbol')})",
        "type": pylint_type,
        "severity": severity
    }

def analyze_file(file_path, content=None):
    if content is not None:
        # If content is provided (e.g. from stdin), we need to write it to a temp file
        # because pylint works best with files.
        # However, for simplicity in this demo, we might just analyze the file on disk
        # OR we can try to pass stdin to pylint if supported.
        # Pylint supports reading from stdin if we pass --from-stdin (in newer versions)
        # or we can write to a temp file.
        
        # Let's try writing to a temporary file to ensure stability
        import tempfile
        
        # Create a temp file with the same extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        try:
            pylint_results = run_pylint(tmp_path)
            # Fix paths in results to point back to original file
            for issue in pylint_results:
                issue['path'] = file_path
        finally:
            try:
                os.remove(tmp_path)
            except:
                pass
    else:
        pylint_results = run_pylint(file_path)
    
    # Transform results
    results = [map_pylint_to_smell(issue) for issue in pylint_results]
    
    # Enrich with advanced analysis (CFG, Refactoring)
    # Note: For enrichment, we need the source code. 
    # If content was provided, we should use that, otherwise read from file.
    if content:
        # We need to modify enrich_issues_with_analysis to accept content string
        # But for now, let's just skip enrichment for live preview to keep it fast
        # OR we can refactor enrich_issues_with_analysis.
        pass 
    else:
        results = enrich_issues_with_analysis(file_path, results)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Smelly Python Code Smell Detector')
    parser.add_argument('file', help='File to analyze')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--html', action='store_true', help='Output in HTML format')
    parser.add_argument('--stdin', action='store_true', help='Read content from stdin')
    
    args = parser.parse_args()
    
    content = None
    if args.stdin:
        # Read from stdin
        content = sys.stdin.read()
    
    results = analyze_file(args.file, content)
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.html:
        print(generate_html_report(results, os.path.basename(args.file)))
    else:
        # Legacy text output
        print(f"Found {len(results)} issues in {args.file}")
        for issue in results:
            print(f"{issue['line']}: [{issue['severity']}] {issue['message']}")

if __name__ == "__main__":
    # Ensure stdout uses UTF-8 encoding to handle special characters in output
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass # Python < 3.7, ignore
            
    main()
