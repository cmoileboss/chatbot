import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { ChatComponent } from './pages/chat/chat';

export const routes: Routes = [
  { path: '', component: ChatComponent },
  { path: 'login', component: LoginComponent },
  { path: '**', redirectTo: '' },
];
