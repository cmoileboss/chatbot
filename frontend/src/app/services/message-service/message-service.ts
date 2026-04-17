import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface BackendMessage {
  id: number;
  conversation_id: number;
  role: string;
  content: string;
  timestamp: string;
}

@Injectable({
  providedIn: 'root',
})
export class MessageService {
  private readonly apiUrl = `${environment.apiUrl}/messages`;

  constructor(private http: HttpClient) {}

  getMessagesForConversation(conversationId: number): Observable<BackendMessage[]> {
    return this.http.get<BackendMessage[]>(`${this.apiUrl}/conversation/${conversationId}`, {
      withCredentials: true,
    });
  }
}
