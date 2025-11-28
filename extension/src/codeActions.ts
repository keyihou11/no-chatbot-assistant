/**
 * Code Actions provider for displaying and applying AI-generated fixes.
 */
import * as vscode from 'vscode';
import { Issue } from './backendClient';
import * as fs from 'fs';
import * as path from 'path';

export class FixCodeActionProvider implements vscode.CodeActionProvider {
    private issues: Map<string, Issue[]> = new Map();
    private undoStack: Array<{ filePath: string, content: string }> = [];

    public static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix
    ];

    /**
     * Update issues for a file.
     */
    setIssues(filePath: string, issues: Issue[]): void {
        this.issues.set(filePath, issues);
    }

    /**
     * Clear issues for a file.
     */
    clearIssues(filePath: string): void {
        this.issues.delete(filePath);
    }

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): vscode.CodeAction[] | undefined {
        const filePath = document.uri.fsPath;
        const fileIssues = this.issues.get(filePath);

        if (!fileIssues || fileIssues.length === 0) {
            return;
        }

        const codeActions: vscode.CodeAction[] = [];
        const currentLine = range.start.line + 1; // Convert to 1-indexed

        // Find issues on the current line
        for (const issue of fileIssues) {
            if (issue.line === currentLine && issue.fix) {
                const action = this.createFixAction(document, issue);
                codeActions.push(action);
            }
        }

        return codeActions;
    }

    private createFixAction(document: vscode.TextDocument, issue: Issue): vscode.CodeAction {
        const action = new vscode.CodeAction(
            `💡 ${issue.fix!.title}`,
            vscode.CodeActionKind.QuickFix
        );

        action.diagnostics = []; // Could attach diagnostics here
        action.isPreferred = true;

        action.command = {
            command: 'no-chatbot.applyFix',
            title: 'Apply Fix',
            arguments: [document, issue]
        };

        return action;
    }

    /**
     * Apply a fix to the document.
     */
    async applyFix(document: vscode.TextDocument, issue: Issue): Promise<void> {
        if (!issue.fix) {
            return;
        }

        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.uri.toString() !== document.uri.toString()) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        // Save current state for undo
        this.undoStack.push({
            filePath: document.uri.fsPath,
            content: document.getText()
        });

        // Show preview
        const apply = await vscode.window.showInformationMessage(
            `Apply fix: ${issue.fix.title}\n\n${issue.fix.description}\n\n⚠️ ${issue.fix.risks}`,
            { modal: true },
            'Apply',
            'Cancel'
        );

        if (apply !== 'Apply') {
            this.undoStack.pop();
            return;
        }

        try {
            // Parse and apply the unified diff patch
            const success = await this.applyUnifiedDiff(editor, issue.fix.patch);

            if (success) {
                await document.save();
                vscode.window.showInformationMessage(`✅ Applied: ${issue.fix.title}`);

                // Clear this issue
                const filePath = document.uri.fsPath;
                const remainingIssues = this.issues.get(filePath)?.filter(i => i !== issue) || [];
                this.setIssues(filePath, remainingIssues);
            } else {
                vscode.window.showErrorMessage('Failed to apply fix - patch format issue');
                this.undoStack.pop();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to apply fix: ${error}`);
            this.undoStack.pop();
        }
    }

    /**
     * Apply a unified diff patch to the editor.
     */
    private async applyUnifiedDiff(editor: vscode.TextEditor, patch: string): Promise<boolean> {
        const document = editor.document;
        const lines = patch.split('\n');

        // Parse the patch to extract operations
        const operations: Array<{
            type: 'delete' | 'insert' | 'replace',
            searchText?: string,  // For finding the line to modify
            newText?: string,     // For insert/replace
            lineHint?: number     // Hint from @@ header
        }> = [];

        let contextLines: string[] = [];
        let deleteLines: string[] = [];
        let addLines: string[] = [];
        let lineHint = -1;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Parse hunk header
            if (line.startsWith('@@')) {
                const match = line.match(/@@ -(\d+),?\d* \+(\d+),?\d* @@/);
                if (match) {
                    lineHint = parseInt(match[2]) - 1; // 0-indexed
                }
                contextLines = [];
                deleteLines = [];
                addLines = [];
                continue;
            }

            // Skip diff headers
            if (line.startsWith('---') || line.startsWith('+++')) {
                continue;
            }

            // Process diff lines
            if (line.startsWith('-') && !line.startsWith('---')) {
                // Line to delete
                deleteLines.push(line.substring(1).trim());
            } else if (line.startsWith('+') && !line.startsWith('+++')) {
                // Line to add
                addLines.push(line.substring(1));
            } else if (line.startsWith(' ')) {
                // Context line
                contextLines.push(line.substring(1).trim());
            }
        }

        // Determine operation type
        if (deleteLines.length > 0 && addLines.length === 0) {
            // Pure deletion - find and delete the line
            const searchText = deleteLines[0];
            operations.push({
                type: 'delete',
                searchText: searchText,
                lineHint: lineHint
            });
        } else if (deleteLines.length === 0 && addLines.length > 0) {
            // Pure insertion
            operations.push({
                type: 'insert',
                newText: addLines.join('\n'),
                lineHint: lineHint
            });
        } else if (deleteLines.length > 0 && addLines.length > 0) {
            // Replacement
            operations.push({
                type: 'replace',
                searchText: deleteLines[0],
                newText: addLines.join('\n'),
                lineHint: lineHint
            });
        }

        if (operations.length === 0) {
            return false;
        }

        // Apply operations
        return await editor.edit(editBuilder => {
            for (const op of operations) {
                if (op.type === 'delete' && op.searchText) {
                    // Find the line containing this text
                    const lineNumber = this.findLineContaining(document, op.searchText, op.lineHint);
                    if (lineNumber !== -1) {
                        const lineRange = document.lineAt(lineNumber).rangeIncludingLineBreak;
                        editBuilder.delete(lineRange);
                    }
                } else if (op.type === 'insert' && op.newText && op.lineHint !== undefined) {
                    // Insert at the hint position
                    const position = new vscode.Position(op.lineHint, 0);
                    editBuilder.insert(position, op.newText + '\n');
                } else if (op.type === 'replace' && op.searchText && op.newText) {
                    // Find and replace the line
                    const lineNumber = this.findLineContaining(document, op.searchText, op.lineHint);
                    if (lineNumber !== -1) {
                        const lineRange = document.lineAt(lineNumber).range;
                        // Preserve indentation
                        const originalLine = document.lineAt(lineNumber).text;
                        const indent = originalLine.match(/^\s*/)?.[0] || '';
                        const newContent = indent + op.newText.trim();
                        editBuilder.replace(lineRange, newContent);
                    }
                }
            }
        });
    }

    /**
     * Find a line containing the given text, starting from a hint line.
     */
    private findLineContaining(document: vscode.TextDocument, searchText: string, lineHint?: number): number {
        const normalizedSearch = searchText.trim();

        // Try the hint line first (within ±5 lines)
        if (lineHint !== undefined && lineHint >= 0) {
            const searchStart = Math.max(0, lineHint - 5);
            const searchEnd = Math.min(document.lineCount, lineHint + 5);

            for (let i = lineHint; i < searchEnd; i++) {
                if (document.lineAt(i).text.trim().includes(normalizedSearch)) {
                    return i;
                }
            }
            for (let i = lineHint - 1; i >= searchStart; i--) {
                if (document.lineAt(i).text.trim().includes(normalizedSearch)) {
                    return i;
                }
            }
        }

        // Fallback: search entire document
        for (let i = 0; i < document.lineCount; i++) {
            if (document.lineAt(i).text.trim().includes(normalizedSearch)) {
                return i;
            }
        }

        return -1;
    }

    /**
     * Undo the last fix.
     */
    async undoLastFix(): Promise<void> {
        if (this.undoStack.length === 0) {
            vscode.window.showInformationMessage('No fixes to undo');
            return;
        }

        const lastState = this.undoStack.pop()!;
        const document = await vscode.workspace.openTextDocument(lastState.filePath);
        const editor = await vscode.window.showTextDocument(document);

        const fullRange = new vscode.Range(
            document.positionAt(0),
            document.positionAt(document.getText().length)
        );

        await editor.edit(editBuilder => {
            editBuilder.replace(fullRange, lastState.content);
        });

        await document.save();
        vscode.window.showInformationMessage('✅ Fix undone');
    }
}
