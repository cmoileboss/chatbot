import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Conversation } from '../../services/conversation-service/conversation-service';

@Component({
  selector: 'app-conversations-list',
  imports: [FormsModule],
  templateUrl: './conversations-list.html',
  styleUrl: './conversations-list.css',
})
export class ConversationsList {
  @Input() conversations: Conversation[] = [];
  @Input() selectedId: number | null = null;
  @Output() conversationSelected = new EventEmitter<Conversation>();
  @Output() newConversation = new EventEmitter<void>();
  @Output() deleteConversation = new EventEmitter<Conversation>();
  @Output() renameConversation = new EventEmitter<{ conversation: Conversation; title: string }>();

  openMenuId = signal<number | null>(null);
  renamingId = signal<number | null>(null);
  renameValue = '';

  select(conversation: Conversation): void {
    if (this.renamingId() === conversation.id) return;
    this.conversationSelected.emit(conversation);
  }

  onNew(): void {
    this.newConversation.emit();
  }

  toggleMenu(event: MouseEvent, convId: number): void {
    event.stopPropagation();
    this.openMenuId.set(this.openMenuId() === convId ? null : convId);
  }

  closeMenu(): void {
    this.openMenuId.set(null);
  }

  startRename(event: MouseEvent, conv: Conversation): void {
    event.stopPropagation();
    this.openMenuId.set(null);
    this.renamingId.set(conv.id);
    this.renameValue = conv.title;
  }

  confirmRename(conv: Conversation): void {
    const title = this.renameValue.trim();
    if (title && title !== conv.title) {
      this.renameConversation.emit({ conversation: conv, title });
    }
    this.renamingId.set(null);
  }

  cancelRename(): void {
    this.renamingId.set(null);
  }

  onDelete(event: MouseEvent, conv: Conversation): void {
    event.stopPropagation();
    this.openMenuId.set(null);
    this.deleteConversation.emit(conv);
  }

  onRenameKeydown(event: KeyboardEvent, conv: Conversation): void {
    if (event.key === 'Enter') this.confirmRename(conv);
    if (event.key === 'Escape') this.cancelRename();
  }
}
