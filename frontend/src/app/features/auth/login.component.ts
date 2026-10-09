import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-h-[85vh] flex items-center justify-center px-4">
      <div class="glass-panel w-full max-w-md p-8 rounded-2xl shadow-2xl border border-slate-700/60">
        <div class="text-center mb-8">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30">
            <span class="text-white text-2xl">🤖</span>
          </div>
          <h1 class="text-2xl font-bold text-white tracking-tight">Support Copilot</h1>
          <p class="text-slate-400 text-sm mt-1">Multi-Agent Customer Support Platform</p>
        </div>

        @if (errorMessage()) {
          <div class="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-300 text-xs">
            {{ errorMessage() }}
          </div>
        }

        <form (ngSubmit)="onSubmit()" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Email Address</label>
            <input
              type="email"
              [(ngModel)]="email"
              name="email"
              required
              class="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-sm"
              placeholder="user@example.com"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Password</label>
            <input
              type="password"
              [(ngModel)]="password"
              name="password"
              required
              class="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-sm"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            [disabled]="loading()"
            class="w-full btn-primary py-3 rounded-lg font-semibold flex items-center justify-center gap-2 mt-2 shadow-lg shadow-blue-600/30"
          >
            @if (loading()) {
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Signing In...</span>
            } @else {
              <span>Sign In</span>
            }
          </button>
        </form>

        <div class="mt-8 pt-6 border-t border-slate-800">
          <p class="text-xs text-slate-400 text-center mb-3 font-medium">Quick Demo Accounts (Password: Password&#64;123)</p>
          <div class="grid grid-cols-3 gap-2">
            <button (click)="quickLogin('aditya.sharma@example.com')" class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-blue-400 border border-slate-700 transition-colors text-center">
              Customer
            </button>
            <button (click)="quickLogin('agent@supportcopilot.local')" class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-amber-400 border border-slate-700 transition-colors text-center">
              Agent
            </button>
            <button (click)="quickLogin('admin@supportcopilot.local')" class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-purple-400 border border-slate-700 transition-colors text-center">
              Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class LoginComponent {
  authService = inject(AuthService);
  router = inject(Router);

  email = 'aditya.sharma@example.com';
  password = 'Password@123';
  loading = signal(false);
  errorMessage = signal<string | null>(null);

  onSubmit(): void {
    this.loading.set(true);
    this.errorMessage.set(null);

    this.authService.login(this.email, this.password).subscribe({
      next: (res) => {
        this.loading.set(false);
        if (res.user.role === 'agent') {
          this.router.navigate(['/agent/escalations']);
        } else if (res.user.role === 'admin') {
          this.router.navigate(['/admin/analytics']);
        } else {
          this.router.navigate(['/chat']);
        }
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.error?.message || 'Invalid email or password');
      }
    });
  }

  quickLogin(demoEmail: string): void {
    this.email = demoEmail;
    this.password = 'Password@123';
    this.onSubmit();
  }
}
