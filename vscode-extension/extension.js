/**
 * LuckyD Code — VSCode Extension
 *
 * Wraps the Python coding agent as a VS Code chat panel.
 * DeepSeek-powered agentic coding with multi-agent swarms, LSP, and autonomous tool execution.
 */

const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// ─── State ──────────────────────────────────────────────────────────

let chatPanel = null;
let agentProcess = null;
let thinking = false;
let currentModel = 'auto';

// ─── Activation ─────────────────────────────────────────────────────

function activate(context) {
    console.log('LuckyD Code Agent activated');

    context.subscriptions.push(
        vscode.commands.registerCommand('luckyd-code.openChat', openChat),
        vscode.commands.registerCommand('luckyd-code.fixThis', fixThis),
        vscode.commands.registerCommand('luckyd-code.explainThis', explainThis),
        vscode.commands.registerCommand('luckyd-code.generateTests', generateTests)
    );

    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(hubot) LuckyD';
    statusBar.tooltip = 'LuckyD Code Agent — Click to chat';
    statusBar.command = 'luckyd-code.openChat';
    statusBar.show();
    context.subscriptions.push(statusBar);
}

// ─── Chat Panel ─────────────────────────────────────────────────────

function openChat() {
    if (chatPanel) {
        chatPanel.reveal(vscode.ViewColumn.Two);
        return;
    }

    chatPanel = vscode.window.createWebviewPanel(
        'luckydCodeChat',
        'LuckyD Code Agent',
        vscode.ViewColumn.Two,
        {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: []
        }
    );

    chatPanel.webview.html = getWebviewContent();
    chatPanel.onDidDispose(() => { chatPanel = null; killAgent(); });

    // Handle messages FROM webview
    chatPanel.webview.onDidReceiveMessage(async (msg) => {
        switch (msg.type) {
            case 'query':
                await handleUserMessage(msg.text, msg.thinking, msg.model);
                break;
            case 'cancel':
                killAgent();
                break;
            case 'set_mode':
                thinking = msg.thinking;
                break;
            case 'set_model':
                currentModel = msg.model;
                break;
        }
    });

    // Initial context
    sendContext();
}

// ─── Message Handling ───────────────────────────────────────────────

async function handleUserMessage(userText, useThinking, modelOverride) {
    if (!chatPanel) return;

    const config = vscode.workspace.getConfiguration('luckyd-code');
    const pythonCmd = config.get('pythonCommand', 'python');
    const agentPath = config.get('agentPath') || getDefaultAgentPath();
    const model = modelOverride || currentModel || config.get('model', 'auto');
    const useThink = useThinking !== undefined ? useThinking : thinking;

    const fullPrompt = await buildPrompt(userText);

    // Spawn agent
    const args = [];
    if (model && model !== 'auto') args.push('--model', model);
    if (useThink) args.push('--thinking');

    killAgent();

    let streamedContent = '';

    try {
        agentProcess = spawn(pythonCmd, ['main.py', ...args], {
            cwd: agentPath,
            env: { ...process.env, PYTHONUNBUFFERED: '1', TERM: 'dumb' },
            stdio: ['pipe', 'pipe', 'pipe']
        });

        agentProcess.stdin.write(fullPrompt + '\n');
        agentProcess.stdin.end();

        agentProcess.stdout.on('data', (data) => {
            const text = data.toString();
            const lines = text.split('\n');
            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const parsed = JSON.parse(line);
                    if (parsed.type === 'tool_call') {
                        chatPanel.webview.postMessage({
                            type: 'tool_call',
                            name: parsed.name,
                            args: parsed.args || {}
                        });
                        continue;
                    }
                    if (parsed.type === 'tool_result') {
                        chatPanel.webview.postMessage({
                            type: 'tool_result',
                            text: parsed.text || ''
                        });
                        continue;
                    }
                } catch (e) {
                    // Not JSON — stream as text
                }
                streamedContent += line + '\n';
                chatPanel.webview.postMessage({
                    type: 'stream',
                    text: line + '\n'
                });
            }
        });

        agentProcess.stderr.on('data', (data) => {
            console.error('[LuckyD Agent]', data.toString());
        });

        agentProcess.on('close', (code) => {
            if (streamedContent) {
                chatPanel.webview.postMessage({
                    type: 'thinking_end',
                    content: streamedContent
                });
            }
            chatPanel.webview.postMessage({ type: 'done' });
            agentProcess = null;
        });

        agentProcess.on('error', (err) => {
            chatPanel.webview.postMessage({
                type: 'error',
                text: 'Failed to start agent: ' + err.message +
                    '\n\nMake sure Python is installed and the agent path is set correctly.' +
                    '\nExpected path: ' + agentPath
            });
            chatPanel.webview.postMessage({ type: 'done' });
            agentProcess = null;
        });

    } catch (err) {
        chatPanel.webview.postMessage({
            type: 'error',
            text: 'Error: ' + err.message
        });
        chatPanel.webview.postMessage({ type: 'done' });
    }
}

// ─── Quick Commands ─────────────────────────────────────────────────

async function fixThis() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return vscode.window.showWarningMessage('No active editor');

    const selection = editor.selection;
    const text = selection.isEmpty
        ? editor.document.getText()
        : editor.document.getText(selection);

    const range = selection.isEmpty
        ? new vscode.Range(0, 0, editor.document.lineCount - 1, 0)
        : selection;

    openChat();
    await handleUserMessage(
        'Fix the following code. Apply fixes directly to the file.\n\n' +
        'File: ' + editor.document.fileName + '\n' +
        'Lines: ' + (range.start.line + 1) + '-' + (range.end.line + 1) +
        '\n\n```\n' + text + '\n```'
    );
}

async function explainThis() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return vscode.window.showWarningMessage('No active editor');

    const selection = editor.selection;
    const text = selection.isEmpty
        ? editor.document.getText()
        : editor.document.getText(selection);

    openChat();
    await handleUserMessage('Explain this code:\n\n```\n' + text + '\n```');
}

async function generateTests() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return vscode.window.showWarningMessage('No active editor');

    const text = editor.document.getText();
    const fileName = path.basename(editor.document.fileName);

    openChat();
    await handleUserMessage(
        'Generate comprehensive tests for this file. Write them to a new file named ' +
        '"test_' + fileName + '" in the appropriate test directory.\n\n' +
        'File: ' + editor.document.fileName + '\n\n```\n' + text + '\n```'
    );
}

// ─── Context ────────────────────────────────────────────────────────

async function sendContext() {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
        const doc = editor.document;
        const sel = editor.selection;
        let text = path.basename(doc.fileName) + ' (' + doc.languageId + ')';
        if (!sel.isEmpty) {
            text += ' [L' + (sel.start.line + 1) + '-' + (sel.end.line + 1) + ']';
        }
        chatPanel.webview.postMessage({ type: 'context', text });
    } else {
        chatPanel.webview.postMessage({ type: 'context', text: '' });
    }
}

vscode.window.onDidChangeActiveTextEditor(() => sendContext());
vscode.window.onDidChangeTextEditorSelection(() => sendContext());

async function refreshContext() {
    const editor = vscode.window.activeTextEditor;
    const ctx = {
        activeFile: null,
        selection: null,
        diagnostics: [],
        workspaceFolder: null
    };

    if (!vscode.workspace.workspaceFolders || !vscode.workspace.workspaceFolders.length) return ctx;

    const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
    ctx.workspaceFolder = root;

    if (editor) {
        const doc = editor.document;
        const sel = editor.selection;
        ctx.activeFile = {
            path: doc.fileName,
            relative: path.relative(root, doc.fileName),
            language: doc.languageId,
            lineCount: doc.lineCount
        };
        if (!sel.isEmpty) {
            ctx.selection = {
                start: { line: sel.start.line + 1, col: sel.start.character },
                end: { line: sel.end.line + 1, col: sel.end.character },
                text: doc.getText(sel)
            };
        }
        const diags = vscode.languages.getDiagnostics(doc.uri);
        ctx.diagnostics = diags.slice(0, 10).map(d => ({
            line: d.range.start.line + 1,
            col: d.range.start.character,
            severity: ['error', 'warning', 'info', 'hint'][d.severity] || 'unknown',
            message: d.message
        }));
    }
    return ctx;
}

async function buildPrompt(userText) {
    const ctx = await refreshContext();
    let prompt = '';

    if (ctx.workspaceFolder) {
        prompt += '# Workspace: ' + ctx.workspaceFolder + '\n\n';
    }
    if (ctx.activeFile) {
        prompt += '# Current file: ' + ctx.activeFile.relative + '\n';
        prompt += '# Language: ' + ctx.activeFile.language + '\n\n';
    }
    if (ctx.selection) {
        prompt += '# Selected code (lines ' + ctx.selection.start.line + '-' + ctx.selection.end.line + '):\n';
        prompt += '```\n' + ctx.selection.text + '\n```\n\n';
    }
    if (ctx.diagnostics.length) {
        prompt += '# Current errors/warnings:\n';
        for (const d of ctx.diagnostics) {
            prompt += '#  [' + d.severity + '] Line ' + d.line + ': ' + d.message + '\n';
        }
        prompt += '\n';
    }

    prompt += userText;
    return prompt;
}

// ─── Helpers ────────────────────────────────────────────────────────

function getDefaultAgentPath() {
    const candidates = [
        path.join(require('os').homedir(), 'OneDrive', 'Desktop', 'coding-agent'),
        path.join(require('os').homedir(), 'coding-agent'),
    ];
    for (const p of candidates) {
        if (fs.existsSync(path.join(p, 'main.py'))) return p;
    }
    return candidates[0];
}

function killAgent() {
    if (agentProcess) {
        try { agentProcess.kill('SIGTERM'); } catch (e) { /* ignore */ }
        agentProcess = null;
    }
}

// ─── Webview HTML ───────────────────────────────────────────────────

function getWebviewContent() {
    const htmlPath = path.join(__dirname, 'media', 'chat.html');
    try {
        return fs.readFileSync(htmlPath, 'utf8');
    } catch (e) {
        return '<!DOCTYPE html><html><body style="font-family:sans-serif;padding:20px;background:#1e1e1e;color:#d4d4d4;"><h2>LuckyD Code</h2><p>Chat UI not found at: ' + htmlPath + '</p></body></html>';
    }
}

module.exports = { activate, deactivate: function() { killAgent(); } };
