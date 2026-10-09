import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { User, AuthResponse } from '../shared/models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private userSignal = signal<User | null>(this.loadStoredUser());

  readonly currentUser = this.userSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.userSignal());
  readonly userRole = computed(() => this.userSignal()?.role || null);

  constructor(private http: HttpClient, private router: Router) {}

  private loadStoredUser(): User | null {
    const saved = localStorage.getItem('sc_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  }

  getToken(): string | null {
    return localStorage.getItem('sc_token');
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/v1/auth/login', { email, password }).pipe(
      tap((res) => {
        localStorage.setItem('sc_token', res.access_token);
        localStorage.setItem('sc_refresh', res.refresh_token);
        localStorage.setItem('sc_user', JSON.stringify(res.user));
        this.userSignal.set(res.user);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('sc_token');
    localStorage.removeItem('sc_refresh');
    localStorage.removeItem('sc_user');
    this.userSignal.set(null);
    this.router.navigate(['/login']);
  }
}
