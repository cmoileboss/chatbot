import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LocalAiResponse, RagDocument } from '../../services/local-ai-response/local-ai-response';
import { AuthService } from '../../services/auth.service';
import { ConversationsList } from '../../components/conversations-list/conversations-list';
import { ConversationService, Conversation } from '../../services/conversation-service/conversation-service';

import { MessageService } from '../../services/message-service/message-service';

interface Message {
  id: number | null;
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
  ragEnabled = false;
  uploadStatus = signal<string | null>(null);
  ragDocuments = signal<RagDocument[]>([]);
  showDocuments = false;
  selectedModel = '';
  availableModels = signal<string[]>([]);
  isPulling = signal(false);
  pullStatus = signal<string | null>(null);
  showPullInput = false;
  pullModelName = '';

  readonly suggestedModels = [
    'llama3.2', 'llama3.2:1b', 'llama3.1:8b',
    'mistral', 'mistral:7b',
    'gemma3:4b', 'gemma3:12b',
    'phi4-mini', 'phi4',
    'qwen2.5:7b', 'qwen2.5:14b',
    'deepseek-r1:8b',
    'codellama',
  ];

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
    this.loadModels();
  }

  loadModels(): void {
    this.localAiResponse.getModels().subscribe({
      next: (res) => {
        this.availableModels.set(res.available);
        this.selectedModel = res.current;
      },
    });
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
        msgs.map(m => ({ id: m.id, role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
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

    this.messages.update((msgs) => [...msgs, { id: null, role: 'user', content: text }]);
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
    const call = this.ragEnabled
      ? this.localAiResponse.chatRag(this.conversationId!, text)
      : this.localAiResponse.chat(this.conversationId!, text);

    call.subscribe({
      next: () => {
        // Reload to get message IDs from server
        this.messageService.getMessagesForConversation(this.conversationId!).subscribe({
          next: (msgs) => this.messages.set(
            msgs.map(m => ({ id: m.id, role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
          ),
        });
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail ?? 'Une erreur est survenue.');
        this.isLoading.set(false);
      },
    });
  }

  onFileUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.uploadStatus.set('Indexation en cours...');
    this.localAiResponse.uploadDocument(file).subscribe({
      next: (res) => {
        this.uploadStatus.set(`✓ ${res.filename} — ${res.chunks_indexed} chunks indexés`);
        this.loadRagDocuments();
      },
      error: (err) => this.uploadStatus.set(`Erreur : ${err.error?.detail ?? 'Upload échoué'}`),
    });
    input.value = '';
  }

  loadRagDocuments(): void {
    this.localAiResponse.listDocuments().subscribe({
      next: (docs) => this.ragDocuments.set(docs),
    });
  }

  onDeleteRagDocument(filename: string): void {
    this.localAiResponse.deleteDocument(filename).subscribe({
      next: () => this.ragDocuments.update(docs => docs.filter(d => d.filename !== filename)),
      error: (err) => this.uploadStatus.set(`Erreur : ${err.error?.detail ?? 'Suppression échouée'}`),
    });
  }

  onResetDocuments(): void {
    if (!confirm('Supprimer tous les documents indexés pour le RAG ?')) return;
    this.localAiResponse.resetDocuments().subscribe({
      next: () => {
        this.uploadStatus.set('Documents RAG supprimés.');
        this.ragDocuments.set([]);
      },
      error: (err) => this.uploadStatus.set(`Erreur : ${err.error?.detail ?? 'Réinitialisation échouée'}`),
    });
  }

  onDeleteMessageFrom(messageId: number): void {
    this.messageService.deleteMessagesFrom(messageId).subscribe({
      next: () => {
        this.messages.update(msgs => {
          const idx = msgs.findIndex(m => m.id === messageId);
          return idx >= 0 ? msgs.slice(0, idx) : msgs;
        });
      },
      error: (err) => this.errorMessage.set(err.error?.detail ?? 'Erreur lors de la suppression.'),
    });
  }

  onModelChange(model: string): void {
    this.localAiResponse.setModel(model).subscribe({
      next: (res) => this.selectedModel = res.model,
      error: () => this.errorMessage.set('Erreur lors du changement de modèle.'),
    });
  }

  onPullModel(): void {
    const model = this.pullModelName.trim();
    if (!model) return;
    this.isPulling.set(true);
    this.pullStatus.set(`Connexion au registre Ollama...`);
    this.localAiResponse.pullModel(model).subscribe({
      next: (progress) => {
        if (progress.total && progress.completed) {
          const pct = Math.round((progress.completed / progress.total) * 100);
          const done = (progress.completed / 1e9).toFixed(1);
          const total = (progress.total / 1e9).toFixed(1);
          this.pullStatus.set(`⬇ ${pct}% — ${done} Go / ${total} Go`);
        } else {
          this.pullStatus.set(progress.status);
        }
      },
      complete: () => {
        this.pullStatus.set(`✓ ${model} téléchargé.`);
        this.isPulling.set(false);
        this.pullModelName = '';
        this.showPullInput = false;
        this.loadModels();
      },
      error: (err) => {
        this.pullStatus.set(`Erreur : ${err?.detail ?? 'Téléchargement échoué'}`);
        this.isPulling.set(false);
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
