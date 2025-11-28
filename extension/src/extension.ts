/**
 * VS Code extension entry point for No-Chatbot.
 */
import * as vscode from 'vscode';
import { BackendClient } from './backendClient';
import { FixCodeActionProvider } from './codeActions';
import { SaveHandler } from './saveHandler';

let backendClient: BackendClient;
let codeActionProvider: FixCodeActionProvider;
let saveHandler: SaveHandler;

export async function activate(context: vscode.ExtensionContext) {
    console.log('No-Chatbot extension is now active');

    // Initialize services
    backendClient = new BackendClient();
    codeActionProvider = new FixCodeActionProvider();
    saveHandler = new SaveHandler(backendClient, codeActionProvider);

    // Check backend health
    const isHealthy = await backendClient.checkHealth();
    if (!isHealthy) {
        vscode.window.showWarningMessage(
            'No-Chatbot backend is not running. Please start the backend server.',
            'Open README'
        ).then(selection => {
            if (selection === 'Open README') {
                vscode.env.openExternal(vscode.Uri.parse('https://github.com/your-repo/no-chatbot#setup'));
            }
        });
    } else {
        vscode.window.showInformationMessage('No-Chatbot is ready! 🚀');
    }

    // Register Code Action Provider
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { language: 'python' },
            codeActionProvider,
            {
                providedCodeActionKinds: FixCodeActionProvider.providedCodeActionKinds
            }
        )
    );

    // Register save event listener
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            await saveHandler.handleSave(document);
        })
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('no-chatbot.undoLastFix', async () => {
            await codeActionProvider.undoLastFix();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('no-chatbot.analyzeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                await saveHandler.handleSave(editor.document);
            } else {
                vscode.window.showErrorMessage('No active editor');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('no-chatbot.applyFix', async (document, issue) => {
            await codeActionProvider.applyFix(document, issue);
        })
    );

    // Cleanup
    context.subscriptions.push(saveHandler);
}

export function deactivate() {
    console.log('No-Chatbot extension deactivated');
}
