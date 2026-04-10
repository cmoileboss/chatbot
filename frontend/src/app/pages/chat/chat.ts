import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class ChatComponent {
  messages = signal<Message[]>([]);
  inputValue = '';

  sendMessage(): void {
    const text = this.inputValue.trim();
    if (!text) return;

    this.messages.update((msgs) => [...msgs, { role: 'user', content: text }]);
    this.inputValue = '';
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
