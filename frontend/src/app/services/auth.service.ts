import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: string;
}

@Injectable({
    providedIn: 'root',
})
export class AuthService {
    private readonly apiUrl = 'http://localhost:8000';

    constructor(private http: HttpClient) {}

    register(credentials: RegisterRequest): Observable<UserResponse> {
        return this.http.post<UserResponse>(`${this.apiUrl}/register`, credentials, {
            withCredentials: true,
        });
    }

    login(credentials: LoginRequest): Observable<UserResponse> {
        return this.http.post<UserResponse>(`${this.apiUrl}/login`, credentials, {
            withCredentials: true,
        });
    }

    logout(): Observable<void> {
        return this.http.post<void>(`${this.apiUrl}/logout`, {}, { withCredentials: true });
    }
}
