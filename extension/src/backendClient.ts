/**
 * Backend API client for communicating with the No-Chatbot backend.
 */
import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface AnalyzeRequest {
    file_path: string;
    code_content: string;
    event_type: string;
}

export interface FixSuggestion {
    title: string;
    description: string;
    patch: string;
    risks: string;
}

export interface Issue {
    line: number;
    column: number;
    severity: string;
    message: string;
    rule_id: string;
    fix?: FixSuggestion;
}

export interface AnalyzeResponse {
    issues: Issue[];
    analyzed_with: string;
}

export class BackendClient {
    private client: AxiosInstance;
    private baseUrl: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('no-chatbot');
        this.baseUrl = config.get('backendUrl', 'http://localhost:8000');

        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: 90000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async analyzeCode(filePath: string, codeContent: string): Promise<AnalyzeResponse> {
        try {
            const request: AnalyzeRequest = {
                file_path: filePath,
                code_content: codeContent,
                event_type: 'save'
            };

            const response = await this.client.post<AnalyzeResponse>('/analyze', request);
            return response.data;

        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Backend request failed: ${error.message}`);
            }
            throw error;
        }
    }

    async checkHealth(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        } catch {
            return false;
        }
    }
}
