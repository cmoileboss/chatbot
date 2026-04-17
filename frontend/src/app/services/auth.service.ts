import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

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
    private readonly apiUrl = environment.apiUrl;
    isLoggedIn = signal(false);
    currentUser = signal<UserResponse | null>(null);

    constructor(private http: HttpClient) {}

    register(credentials: RegisterRequest): Observable<UserResponse> {
        return this.http.post<UserResponse>(`${this.apiUrl}/register`, credentials, {
            withCredentials: true,
        }).pipe(tap(() => this.isLoggedIn.set(true)));
    }

    login(credentials: LoginRequest): Observable<UserResponse> {
        return this.http.post<UserResponse>(`${this.apiUrl}/login`, credentials, {
            withCredentials: true,
        }).pipe(tap((user) => {
            this.isLoggedIn.set(true);
            this.currentUser.set(user);
        }));
    }

    logout(): Observable<void> {
        return this.http.post<void>(`${this.apiUrl}/logout`, {}, { withCredentials: true })
            .pipe(tap(() => {
                this.isLoggedIn.set(false);
                this.currentUser.set(null);
            }));
    }
}
