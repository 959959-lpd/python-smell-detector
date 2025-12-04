import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as cp from 'child_process';

suite('IPC Communication Test Suite', () => {
	vscode.window.showInformationMessage('Start IPC tests.');

	test('Python Script Returns Valid JSON', async () => {
        // Locate the python script
        const scriptPath = path.resolve(__dirname, '../../../../smelly_python/main.py');
        const pythonPath = 'python'; // Assuming python is in PATH

        // Create a dummy python file to analyze
        const dummyFile = path.resolve(__dirname, 'temp_test.py');
        // We are not actually creating the file here for simplicity, 
        // assuming the script handles non-existent files gracefully or we use an existing one.
        // Let's use the script itself as the target to analyze
        
        const args = [scriptPath, scriptPath, '--json'];

        const result = await new Promise<string>((resolve, reject) => {
            cp.execFile(pythonPath, args, (error, stdout, stderr) => {
                if (error) {
                    // If pylint finds issues, it might exit with non-zero, which is fine for us
                    // But if it fails to run, that's an error.
                    // For this test, we just want to check stdout is JSON.
                }
                resolve(stdout);
            });
        });

        try {
            const jsonResult = JSON.parse(result);
            assert.ok(Array.isArray(jsonResult), 'Output should be a JSON array');
            
            if (jsonResult.length > 0) {
                const issue = jsonResult[0];
                assert.ok(issue.hasOwnProperty('line'), 'Issue object must have line property');
                assert.ok(issue.hasOwnProperty('message'), 'Issue object must have message property');
                assert.ok(issue.hasOwnProperty('severity'), 'Issue object must have severity property');
            }
        } catch (e) {
            assert.fail('Failed to parse Python output as JSON: ' + result);
        }
	});
});
