import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

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
}
