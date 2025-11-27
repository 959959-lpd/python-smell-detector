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

def analyze_file(file_path):
    pylint_results = run_pylint(file_path)
    
    # Transform results
    results = [map_pylint_to_smell(issue) for issue in pylint_results]
    
    # Enrich with advanced analysis (CFG, Refactoring)
    results = enrich_issues_with_analysis(file_path, results)
    
    return results

def generate_html_report(results, filename):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Smell Report - {filename}</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; padding: 20px; background-color: #f3f4f6; margin: 0; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-top: 0; }}
            .summary {{ margin-bottom: 20px; font-size: 1.1em; color: #4b5563; background-color: #f9fafb; padding: 15px; border-radius: 6px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #e5e7eb; }}
            th {{ background-color: #f9fafb; color: #374151; font-weight: 600; }}
            tr:hover {{ background-color: #f9fafb; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 9999px; font-size: 0.85em; font-weight: 500; }}
            .badge-Error {{ background-color: #fee2e2; color: #991b1b; }}
            .badge-Warning {{ background-color: #fef3c7; color: #92400e; }}
            .badge-Information {{ background-color: #dbeafe; color: #1e40af; }}
            .empty-state {{ text-align: center; padding: 40px; color: #6b7280; font-style: italic; }}
            .action-btn {{ background-color: #3b82f6; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.9em; }}
            .action-btn:hover {{ background-color: #2563eb; }}
            .details-row {{ display: none; background-color: #f8fafc; }}
            .details-content {{ padding: 20px; border-left: 4px solid #3b82f6; }}
            .code-block {{ background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Consolas', 'Monaco', monospace; white-space: pre; }}
            .two-col {{ display: flex; gap: 20px; }}
            .col {{ flex: 1; }}
            h4 {{ margin-top: 0; color: #4b5563; }}
        </style>
        <script>
            function toggleDetails(id) {{
                var x = document.getElementById(id);
                if (x.style.display === "none" || !x.style.display) {{
                    x.style.display = "table-row";
                }} else {{
                    x.style.display = "none";
                }}
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Code Smell Report</h1>
            <div class="summary">
                <div>File: <strong>{filename}</strong></div>
                <div>Total Issues: <strong>{count}</strong></div>
            </div>
            
            {content}
        </div>
    </body>
    </html>
    """
    
    if not results:
        # Use HTML entity for party popper to avoid encoding errors
        content = '<div class="empty-state">&#127881; Great job! No code smells found in this file.</div>'
    else:
        rows = ""
        for i, issue in enumerate(results):
            severity = issue['severity']
            has_suggestion = issue.get('has_suggestion', False)
            
            action_cell = ""
            if has_suggestion:
                # Use HTML entity for wrench icon to avoid encoding errors on Windows consoles
                action_cell = f'<button class="action-btn" onclick="toggleDetails(\'details-{i}\')">Fix It &#128295;</button>'
            
            rows += f"""
            <tr>
                <td>{issue['line']}</td>
                <td><span class="badge badge-{severity}">{severity}</span></td>
                <td>{issue['type']}</td>
                <td>{issue['message']}</td>
                <td>{action_cell}</td>
            </tr>
            """
            
            if has_suggestion:
                cfg = issue.get('cfg', '')
                refactoring = issue.get('refactoring', '')
                rows += f"""
                <tr id="details-{i}" class="details-row">
                    <td colspan="5">
                        <div class="details-content">
                            <div class="two-col">
                                <div class="col">
                                    <h4>Complexity Analysis (CFG)</h4>
                                    <div class="mermaid">
                                    {cfg}
                                    </div>
                                </div>
                                <div class="col">
                                    <h4>Refactoring Preview</h4>
                                    <div class="code-block">{refactoring}</div>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
                """
                
        content = f"""
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px">Line</th>
                        <th style="width: 100px">Severity</th>
                        <th style="width: 150px">Type</th>
                        <th>Message</th>
                        <th style="width: 100px">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        """
    
    return html_template.format(filename=filename, count=len(results), content=content)

def main():
    parser = argparse.ArgumentParser(description='Smelly Python Code Smell Detector')
    parser.add_argument('file', help='File to analyze')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--html', action='store_true', help='Output in HTML format')
    
    args = parser.parse_args()
    
    results = analyze_file(args.file)
    
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
