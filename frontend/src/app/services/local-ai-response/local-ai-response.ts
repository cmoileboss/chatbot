import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface RagDocument {
  filename: string;
  chunks: number;
}

export interface PullProgress {
  status: string;
  digest?: string;
  total?: number;
  completed?: number;
  error?: string;
}

@Injectable({
  providedIn: 'root',
})
export class LocalAiResponse {
  private readonly apiUrl = `${environment.apiUrl}/ai-response`;

  constructor(private http: HttpClient) {}

  chat(conversationId: number, prompt: string): Observable<string> {
    return this.http.post(`${this.apiUrl}/chat/${conversationId}`, { prompt }, {
      withCredentials: true,
      responseType: 'text',
    });
  }

  generate(prompt: string): Observable<string> {
    return this.http.post(`${this.apiUrl}/generate`, { prompt }, {
      responseType: 'text',
    });
  }

  chatRag(conversationId: number, prompt: string): Observable<string> {
    return this.http.post(`${this.apiUrl}/chat-rag/${conversationId}`, { prompt }, {
      withCredentials: true,
      responseType: 'text',
    });
  }

  uploadDocument(file: File): Observable<{ filename: string; chunks_indexed: number }> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<{ filename: string; chunks_indexed: number }>(`${this.apiUrl}/upload`, form, {
      withCredentials: true,
    });
  }

  getModels(): Observable<{ current: string; available: string[] }> {
    return this.http.get<{ current: string; available: string[] }>(`${this.apiUrl}/models`, {
      withCredentials: true,
    });
  }

  setModel(model: string): Observable<{ model: string }> {
    return this.http.put<{ model: string }>(`${this.apiUrl}/model`, { model }, {
      withCredentials: true,
    });
  }

  resetDocuments(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/documents`, {
      withCredentials: true,
    });
  }

  listDocuments(): Observable<RagDocument[]> {
    return this.http.get<RagDocument[]>(`${this.apiUrl}/documents`, {
      withCredentials: true,
    });
  }

  deleteDocument(filename: string): Observable<{ filename: string; chunks_deleted: number }> {
    return this.http.delete<{ filename: string; chunks_deleted: number }>(
      `${this.apiUrl}/documents/${encodeURIComponent(filename)}`,
      { withCredentials: true },
    );
  }

  pullModel(model: string): Observable<PullProgress> {
    return new Observable(observer => {
      const controller = new AbortController();

      fetch(`${this.apiUrl}/models/pull`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model }),
        signal: controller.signal,
      }).then(async (response) => {
        if (!response.ok || !response.body) {
          try { observer.error(await response.json()); }
          catch { observer.error({ detail: `Erreur HTTP ${response.status}` }); }
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        try {
          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';
            for (const line of lines) {
              if (!line.trim()) continue;
              try {
                const data: PullProgress = JSON.parse(line);
                if (data.error) { observer.error({ detail: data.error }); return; }
                observer.next(data);
                if (data.status === 'success') { observer.complete(); return; }
              } catch { /* ligne malformée, on ignore */ }
            }
          }
          observer.complete();
        } catch (e) {
          observer.error(e);
        }
      }).catch(err => observer.error(err));

      return () => controller.abort();
    });
  }
}
