import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

// Create an output channel for debugging
const outputChannel = vscode.window.createOutputChannel("Python Smell Detector");

export function activate(context: vscode.ExtensionContext) {
    console.log('Congratulations, your extension "python-smell-detector" is now active!');

    const diagnosticCollection = vscode.languages.createDiagnosticCollection('python-smells');
    context.subscriptions.push(diagnosticCollection);

    // Command to show report
    let disposable = vscode.commands.registerCommand('python-smell-detector.showReport', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('Please open a Python file to generate a report.');
            return;
        }
        
        if (editor.document.languageId !== 'python') {
             vscode.window.showErrorMessage('The active file is not a Python file.');
             return;
        }

        const panel = vscode.window.createWebviewPanel(
            'smellReport',
            `Smell Report: ${path.basename(editor.document.fileName)}`,
            vscode.ViewColumn.Beside,
            {
                enableScripts: true
            }
        );

        panel.webview.html = getLoadingContent();

        // Strategy 1: Try to find script relative to the extension installation folder
        // This works if the folder structure (team20/vscode-extension + team20/smelly_python) is preserved
        const extensionRoot = context.extensionUri.fsPath;
        let pythonScriptPath = path.join(extensionRoot, '..', 'smelly_python', 'main.py');

        // Strategy 2: Hardcoded path for this specific environment (Fallback)
        if (!fs.existsSync(pythonScriptPath)) {
            pythonScriptPath = 'C:\\Users\\wjylp\\Desktop\\CUHK\\asoftware\\team20\\smelly_python\\main.py';
        }

        if (!fs.existsSync(pythonScriptPath)) {
            panel.webview.html = getErrorContent(`Could not find 'smelly_python/main.py'.\nSearched at: ${pythonScriptPath}\n\nPlease ensure the 'smelly_python' folder exists.`);
            return;
        }
        
        outputChannel.appendLine(`Analyzing file: ${editor.document.fileName}`);
        outputChannel.appendLine(`Using script: ${pythonScriptPath}`);

        // Use 'python' directly. On Windows, ensure python is in your PATH.
        // Added '-u' for unbuffered output to avoid hanging
        // Hardcoded python path for stability in this specific environment
        const pythonPath = 'C:\\Users\\wjylp\\miniconda3\\python.exe';
        outputChannel.appendLine(`Using python interpreter: ${pythonPath}`);
        
        const pythonProcess = spawn(pythonPath, ['-u', pythonScriptPath, '--html', editor.document.fileName], {
            cwd: path.dirname(pythonScriptPath) // Set working directory to where the script is
        });
        
        let htmlContent = '';
        let errorString = '';

        pythonProcess.stdout.on('data', (data) => {
            const str = data.toString();
            outputChannel.appendLine(`STDOUT: ${str}`);
            htmlContent += str;
        });
        
        pythonProcess.stderr.on('data', (data) => {
            const str = data.toString();
            outputChannel.appendLine(`STDERR: ${str}`);
            errorString += str;
        });

        // Handle process creation errors (e.g. python not found)
        pythonProcess.on('error', (err) => {
            outputChannel.appendLine(`ERROR: ${err.message}`);
            panel.webview.html = getErrorContent(
                `Failed to start 'python' process. \n\nError: ${err.message}\n\nPlease ensure 'python' is installed and added to your system PATH.`
            );
        });

        pythonProcess.on('close', (code) => {
            outputChannel.appendLine(`Process exited with code ${code}`);
            if (code !== 0) {
                panel.webview.html = getErrorContent(errorString || `Process exited with code ${code}. Unknown error.`);
            } else {
                if (!htmlContent) {
                     panel.webview.html = getErrorContent("Python script finished but returned no output. Check the 'Python Smell Detector' output channel for details.");
                } else {
                    panel.webview.html = htmlContent;
                }
            }
        });
    });

    context.subscriptions.push(disposable);

    // Listen for save events
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(document => {
        if (document.languageId === 'python') {
            runSmellDetection(context, document, diagnosticCollection);
        }
    }));

    // Listen for open events
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(document => {
        if (document.languageId === 'python') {
            runSmellDetection(context, document, diagnosticCollection);
        }
    }));

    // Listen for change events with debounce
    let timeout: NodeJS.Timeout | undefined = undefined;
    context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document.languageId === 'python') {
            if (timeout) {
                clearTimeout(timeout);
                timeout = undefined;
            }
            timeout = setTimeout(() => {
                runSmellDetection(context, event.document, diagnosticCollection);
            }, 500); // 500ms debounce
        }
    }));
}

function runSmellDetection(context: vscode.ExtensionContext, document: vscode.TextDocument, collection: vscode.DiagnosticCollection) {
    // Strategy 1: Try to find script relative to the extension installation folder
    const extensionRoot = context.extensionUri.fsPath;
    let pythonScriptPath = path.join(extensionRoot, '..', 'smelly_python', 'main.py');

    // Strategy 2: Hardcoded path for this specific environment (Fallback)
    if (!fs.existsSync(pythonScriptPath)) {
        pythonScriptPath = 'C:\\Users\\wjylp\\Desktop\\CUHK\\asoftware\\team20\\smelly_python\\main.py';
    }

    if (!fs.existsSync(pythonScriptPath)) {
        outputChannel.appendLine(`[Real-time] Could not find script at: ${pythonScriptPath}`);
        return;
    }

    const pythonPath = 'C:\\Users\\wjylp\\miniconda3\\python.exe';
    
    outputChannel.appendLine(`[Real-time] Analyzing: ${document.fileName}`);

    // Use --stdin to pass content directly, supporting unsaved changes
    const pythonProcess = spawn(pythonPath, ['-u', pythonScriptPath, '--json', '--stdin', document.fileName], {
        cwd: path.dirname(pythonScriptPath)
    });

    // Write document content to stdin
    try {
        pythonProcess.stdin.write(document.getText());
        pythonProcess.stdin.end();
    } catch (e) {
        outputChannel.appendLine(`[Real-time] Error writing to stdin: ${e}`);
    }

    let dataString = '';
    let errorString = '';

    pythonProcess.stdout.on('data', (data) => {
        dataString += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorString += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            outputChannel.appendLine(`[Real-time] Error (code ${code}): ${errorString}`);
            return;
        }

        try {
            const results = JSON.parse(dataString);
            const diagnostics: vscode.Diagnostic[] = [];

            for (const result of results) {
                // Line numbers in VS Code are 0-based, but usually 1-based in tools
                const lineIndex = result.line - 1;
                const range = new vscode.Range(lineIndex, 0, lineIndex, Number.MAX_VALUE);
                
                let severity = vscode.DiagnosticSeverity.Warning;
                if (result.severity === 'Error') {
                    severity = vscode.DiagnosticSeverity.Error;
                } else if (result.severity === 'Information') {
                    severity = vscode.DiagnosticSeverity.Information;
                }

                const diagnostic = new vscode.Diagnostic(range, result.message, severity);
                diagnostic.source = 'Smelly Python';
                diagnostics.push(diagnostic);
            }

            collection.set(document.uri, diagnostics);
            outputChannel.appendLine(`[Real-time] Found ${diagnostics.length} issues.`);

        } catch (e) {
            outputChannel.appendLine(`[Real-time] JSON Parse Error: ${e}`);
            outputChannel.appendLine(`[Real-time] Raw output: ${dataString}`);
        }
    });
}

function getLoadingContent() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loading...</title>
        <style>
            body { display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; color: #666; }
            .loader { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin-right: 10px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <p>Analyzing code smells...</p>
    </body>
    </html>`;
}

function getErrorContent(errorMessage: string) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error</title>
        <style>body { padding: 20px; font-family: sans-serif; color: #d32f2f; }</style>
    </head>
    <body>
        <h1>Analysis Failed</h1>
        <p>An error occurred while running the analysis:</p>
        <pre>${errorMessage}</pre>
    </body>
    </html>`;
}

export function deactivate() {}
