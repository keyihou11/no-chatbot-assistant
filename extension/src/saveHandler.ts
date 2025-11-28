/**
 * Save event handler for triggering analysis when files are saved.
 */
import * as vscode from 'vscode';
import { BackendClient } from './backendClient';
import { FixCodeActionProvider } from './codeActions';

export class SaveHandler {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private analyzing: Set<string> = new Set();

    constructor(
        private backendClient: BackendClient,
        private codeActionProvider: FixCodeActionProvider
    ) {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('no-chatbot');
    }

    async handleSave(document: vscode.TextDocument): Promise<void> {
        // Only handle Python files
        if (document.languageId !== 'python') {
            return;
        }

        const config = vscode.workspace.getConfiguration('no-chatbot');
        if (!config.get('autoAnalyzeOnSave', true)) {
            return;
        }

        const filePath = document.uri.fsPath;

        // Avoid duplicate analysis
        if (this.analyzing.has(filePath)) {
            return;
        }

        this.analyzing.add(filePath);

        try {
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "No-Chatbot analyzing...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });

                const codeContent = document.getText();
                const response = await this.backendClient.analyzeCode(filePath, codeContent);

                progress.report({ increment: 50 });

                // Clear previous diagnostics
                this.diagnosticCollection.delete(document.uri);
                this.codeActionProvider.clearIssues(filePath);

                if (response.issues.length > 0) {
                    // Create diagnostics
                    const diagnostics: vscode.Diagnostic[] = [];

                    for (const issue of response.issues) {
                        const line = issue.line - 1; // Convert to 0-indexed
                        const range = new vscode.Range(
                            new vscode.Position(line, issue.column),
                            new vscode.Position(line, 1000) // End of line
                        );

                        const severity = this.mapSeverity(issue.severity);
                        const diagnostic = new vscode.Diagnostic(
                            range,
                            `${issue.message} (${issue.rule_id})${issue.fix ? ' - AI fix available' : ''}`,
                            severity
                        );

                        diagnostic.source = 'no-chatbot';
                        diagnostics.push(diagnostic);
                    }

                    this.diagnosticCollection.set(document.uri, diagnostics);
                    this.codeActionProvider.setIssues(filePath, response.issues);

                    progress.report({ increment: 100 });

                    const issuesWithFixes = response.issues.filter(i => i.fix).length;
                    vscode.window.showInformationMessage(
                        `No-Chatbot: Found ${response.issues.length} issue(s), ${issuesWithFixes} with AI fixes`
                    );
                } else {
                    progress.report({ increment: 100 });
                    vscode.window.showInformationMessage('No-Chatbot: No issues found ✨');
                }
            });

        } catch (error) {
            vscode.window.showErrorMessage(`No-Chatbot analysis failed: ${error}`);
        } finally {
            this.analyzing.delete(filePath);
        }
    }

    private mapSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
            default:
                return vscode.DiagnosticSeverity.Information;
        }
    }

    dispose(): void {
        this.diagnosticCollection.dispose();
    }
}
