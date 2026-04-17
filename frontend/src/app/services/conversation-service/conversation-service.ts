import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Conversation {
  id: number;
  title: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class ConversationService {
  private readonly apiUrl = `${environment.apiUrl}/conversations`;

  constructor(private http: HttpClient) {}

  getConversationsForUser(userId: number): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${this.apiUrl}/user/${userId}`, { withCredentials: true });
  }

  createConversation(title: string): Observable<Conversation> {
    return this.http.post<Conversation>(`${this.apiUrl}/`, { title }, { withCredentials: true });
  }

  renameConversation(id: number, title: string): Observable<Conversation> {
    return this.http.patch<Conversation>(`${this.apiUrl}/${id}`, { title }, { withCredentials: true });
  }

  deleteConversation(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { withCredentials: true });
  }
}
