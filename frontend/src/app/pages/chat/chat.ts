import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LocalAiResponse } from '../../services/local-ai-response/local-ai-response';
import { AuthService } from '../../services/auth.service';
import { ConversationsList } from '../../components/conversations-list/conversations-list';
import { ConversationService, Conversation } from '../../services/conversation-service/conversation-service';

import { MessageService } from '../../services/message-service/message-service';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-chat',
  imports: [FormsModule, ConversationsList],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class ChatComponent implements OnInit {
  messages = signal<Message[]>([]);
  conversations = signal<Conversation[]>([]);
  inputValue = '';
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  conversationId: number | null = null;

  constructor(
    private localAiResponse: LocalAiResponse,
    public authService: AuthService,
    private conversationService: ConversationService,
    private messageService: MessageService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    this.loadConversations();
  }

  loadConversations(): void {
    const user = this.authService.currentUser();
    if (!user) return;
    this.conversationService.getConversationsForUser(user.id).subscribe({
      next: (convs) => this.conversations.set(convs),
    });
  }

  selectConversation(conversation: Conversation): void {
    this.conversationId = conversation.id;
    this.messages.set([]);
    this.errorMessage.set(null);
    this.messageService.getMessagesForConversation(conversation.id).subscribe({
      next: (msgs) => this.messages.set(
        msgs.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
      ),
    });
  }

  newConversation(): void {
    this.conversationId = null;
    this.messages.set([]);
    this.errorMessage.set(null);
  }

  sendMessage(): void {
    const text = this.inputValue.trim();
    if (!text || this.isLoading()) return;

    this.messages.update((msgs) => [...msgs, { role: 'user', content: text }]);
    this.inputValue = '';
    this.errorMessage.set(null);
    this.isLoading.set(true);

    if (this.conversationId === null) {
      const titlePrompt = `Résume en 5 mots maximum ce message pour en faire un titre de conversation. Réponds uniquement avec le titre, sans ponctuation ni guillemets : ${text}`;
      this.localAiResponse.generate(titlePrompt).subscribe({
        next: (title) => {
          const cleanTitle = title.trim().slice(0, 100);
          this.conversationService.createConversation(cleanTitle).subscribe({
            next: (conversation) => {
              this.conversationId = conversation.id;
              this.conversations.update((convs) => [conversation, ...convs]);
              this.sendToAi(text);
            },
            error: (err) => {
              this.errorMessage.set(err.error?.detail ?? 'Une erreur est survenue.');
              this.isLoading.set(false);
            },
          });
        },
        error: () => {
          const fallback = text.length > 100 ? text.slice(0, 97) + '...' : text;
          this.conversationService.createConversation(fallback).subscribe({
            next: (conversation) => {
              this.conversationId = conversation.id;
              this.conversations.update((convs) => [conversation, ...convs]);
              this.sendToAi(text);
            },
            error: (err) => {
              this.errorMessage.set(err.error?.detail ?? 'Une erreur est survenue.');
              this.isLoading.set(false);
            },
          });
        },
      });
      return;
    }

    this.sendToAi(text);
  }

  private sendToAi(text: string): void {
    this.localAiResponse.chat(this.conversationId!, text).subscribe({
      next: (response) => {
        this.messages.update((msgs) => [...msgs, { role: 'assistant', content: response }]);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail ?? 'Une erreur est survenue.');
        this.isLoading.set(false);
      },
    });
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  onDeleteConversation(conv: Conversation): void {
    this.conversationService.deleteConversation(conv.id).subscribe({
      next: () => {
        this.conversations.update((convs) => convs.filter(c => c.id !== conv.id));
        if (this.conversationId === conv.id) {
          this.conversationId = null;
          this.messages.set([]);
        }
      },
      error: (err) => this.errorMessage.set(err.error?.detail ?? 'Erreur lors de la suppression.'),
    });
  }

  onRenameConversation(event: { conversation: Conversation; title: string }): void {
    this.conversationService.renameConversation(event.conversation.id, event.title).subscribe({
      next: (updated) => {
        this.conversations.update((convs) =>
          convs.map(c => c.id === updated.id ? updated : c)
        );
      },
      error: (err) => this.errorMessage.set(err.error?.detail ?? 'Erreur lors du renommage.'),
    });
  }

  logout(): void {
    this.authService.logout().subscribe({
      next: () => this.router.navigate(['/login']),
    });
  }
}
