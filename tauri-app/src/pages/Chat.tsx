import { useState, useRef, useEffect, useCallback } from "react";
import { Plus, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/i18n";
import { ChatProvider, useChatContext } from "@/hooks/chatCtx";
import { groupChatsByDate } from "@/lib/chat-utils";
import { ChatWelcome } from "@/components/chat/ChatWelcome";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { ChatInput } from "@/components/chat/ChatInput";
import { SidePanel } from "@/components/layout/SidePanel";
import { ChatListItem } from "@/components/chat/ChatListItem";
import { useDragRegion } from "@/hooks/useDragRegion";
import { useSSE } from "@/hooks/useSSE";
import { getApiClient } from "@/lib/api";
import type { Attachment, Message } from "@/hooks/useChat";
import type { ChatItem } from "@/lib/chat-utils";
import type { SidecarStatus } from "@/types";
import { useChatStore } from "@/stores/chat";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

// Inner component that uses chat context
function ChatContent() {
  const { t } = useI18n();
  const {
    chatId,
    timelineItems,
    streamingText,
    isProcessing,
    pendingToolUse,
    chatStatus,
    send,
    stop,
    agents,
    agentId,
    setAgentId,
    chatList,
    loadChat,
    newChat,
    deleteChat,
    updateChat,
    searchQuery,
    setSearchQuery,
  } = useChatContext();

  const isNewChat = !chatId && timelineItems.length === 0;
  const status = chatStatus === "ready" ? "ready" : chatStatus;
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const drag = useDragRegion();

  useEffect(() => {
    if (searchOpen) {
      searchInputRef.current?.focus();
    } else {
      setSearchQuery("");
    }
  }, [searchOpen, setSearchQuery]);

  const filteredChats = searchQuery
    ? chatList.filter((c) =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : chatList;

  const chatGroups = groupChatsByDate(filteredChats, {
    today: t.chat.today,
    yesterday: t.chat.yesterday,
    older: t.chat.older,
  });

  const handleDeleteConfirm = async () => {
    if (deleteTarget) {
      await deleteChat(deleteTarget);
      setDeleteTarget(null);
    }
  };

  const handleSend = async (msg: { text: string; files: Array<{ id: string; filename: string; mediaType: string; filePath?: string }> }) => {
    await send(msg.text);
  };

  return (
    <div className="flex h-full">
      {/* Left side: Chat list */}
      <SidePanel>
        <div className="h-12 shrink-0 px-3 border-b border-[var(--subtle-border)] flex items-center justify-between" {...drag}>
          <h2 className="font-semibold text-sm">{t.nav.chat}</h2>
          <div className="flex items-center gap-0.5">
            <button
              data-testid="chat-search-toggle"
              onClick={() => setSearchOpen((v) => !v)}
              className={cn(
                "flex items-center gap-1 px-2 py-1 text-xs rounded-lg transition-all duration-200 ease-[var(--ease-soft)]",
                searchOpen
                  ? "text-foreground bg-[var(--surface-hover)]"
                  : "text-muted-foreground hover:bg-[var(--surface-hover)] hover:text-accent-foreground",
              )}
              title={t.sidebar.search}
            >
              <Search className="h-3.5 w-3.5" />
            </button>
            <button
              data-testid="chat-new"
              onClick={() => newChat()}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg text-muted-foreground hover:bg-[var(--surface-hover)] hover:text-accent-foreground transition-all duration-200 ease-[var(--ease-soft)]"
              title={t.sidebar.newChat}
            >
              <Plus className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Search (expand/collapse) */}
        <div
          className={cn(
            "overflow-hidden transition-all duration-200 ease-[var(--ease-soft)]",
            searchOpen ? "max-h-12 opacity-100" : "max-h-0 opacity-0",
          )}
        >
          <div className="px-3 py-2">
            <div className="relative">
              <input
                ref={searchInputRef}
                type="text"
                data-testid="chat-search"
                className="w-full bg-[var(--surface-raised)] border border-[var(--subtle-border)] rounded-xl px-3 py-1.5 pr-7 text-sm transition-all duration-200 ease-[var(--ease-soft)] focus:outline-none focus:border-primary/40 focus:shadow-[0_0_0_3px_oklch(0.55_0.2_25/0.1)]"
                placeholder={t.sidebar.search}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Escape") setSearchOpen(false);
                }}
              />
              {searchQuery && (
                <button
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  onClick={() => setSearchQuery("")}
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-0.5" role="listbox">
          {chatGroups.length === 0 && (
            <p className="text-xs text-muted-foreground px-2.5 py-4 text-center">
              {t.chat.noConversations}
            </p>
          )}
          {chatGroups.map((group) => (
            <div key={group.label}>
              <div className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider px-2.5 pt-3 pb-1">
                {group.label}
              </div>
              {group.items.map((chat) => (
                <ChatListItem
                  key={chat.chat_id}
                  chat={chat}
                  isActive={chatId === chat.chat_id}
                  onSelect={() => loadChat(chat.chat_id)}
                  onDelete={(id) => setDeleteTarget(id)}
                  onUpdateAvatar={(id, avatar) => updateChat(id, { avatar })}
                  onUpdateName={(id, name) => updateChat(id, { name })}
                />
              ))}
            </div>
          ))}
        </div>
      </SidePanel>

      {/* Right: Chat content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {isNewChat ? <ChatWelcome /> : (
          <ChatMessages
            timelineItems={timelineItems}
            streamingText={streamingText}
            isProcessing={isProcessing}
            pendingToolUse={pendingToolUse}
          />
        )}

        {/* ChatInput - always at bottom */}
        <div className="relative px-4 pb-4">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              onSubmit={handleSend}
              onStop={stop}
              status={status}
              disabled={false}
              placeholder={t.chat.placeholder}
              agents={agents}
              selectedAgentId={agentId}
              onAgentChange={setAgentId}
            />
          </div>
        </div>
      </div>

      {/* Delete confirmation dialog */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open: boolean) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t.chat.deleteChat}</AlertDialogTitle>
            <AlertDialogDescription>
              {t.chat.confirmDelete}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t.common.cancel}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {t.common.delete}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

// SSE handler component - handles SSE connection and updates store
function SSEHandler({ sidecarStatus }: { sidecarStatus: SidecarStatus }) {
  const activeChatId = useChatStore((s) => s.activeChatId);
  const initChat = useChatStore((s) => s.initChat);
  const setActiveChatId = useChatStore((s) => s.setActiveChatId);
  const appendStreamText = useChatStore((s) => s.appendStreamText);
  const completeMessage = useChatStore((s) => s.completeMessage);
  const addToolUse = useChatStore((s) => s.addToolUse);
  const setProcessing = useChatStore((s) => s.setProcessing);

  const isSidecarRunning = sidecarStatus.status === 'Running';
  const streamUrl = isSidecarRunning
    ? `http://127.0.0.1:${sidecarStatus.port}/api/stream`
    : '';

  // Handle SSE events - use chat_id from event, fallback to activeChatId
  const handleSSEMessage = useCallback((event: { type: string; data: any }) => {
    // Extract chat_id from event data, with multiple fallback paths
    const eventChatId = event.data?.chat_id || event.data?.payload?.chat_id;
    const targetChatId = eventChatId || activeChatId;

    if (!targetChatId) {
      console.log('[SSEHandler] No chat_id available, skipping event:', event.type);
      return;
    }

    // Initialize chat if needed and sync activeChatId
    if (eventChatId && eventChatId !== activeChatId) {
      initChat(eventChatId);
      setActiveChatId(eventChatId);
    }

    console.log('[SSEHandler] Processing event:', event.type, 'for chat:', targetChatId);

    switch (event.type) {
      case 'content_delta':
        if (event.data.delta) {
          appendStreamText(targetChatId, event.data.delta);
        } else if (event.data.content) {
          appendStreamText(targetChatId, event.data.content);
        }
        break;

      case 'message:outbound':
        const content = event.data.payload?.content || event.data.content || '';
        console.log('[SSEHandler] message:outbound content:', content.substring(0, 50));
        completeMessage(targetChatId, content, []);
        setProcessing(targetChatId, false);  // Reset processing state
        break;

      case 'message_end':
        // Already handled by message:outbound
        break;

      case 'tool:start':
        addToolUse(targetChatId, {
          id: event.data.tool_id || `tool_${Date.now()}`,
          name: event.data.name || 'unknown',
          input: event.data.input ? JSON.stringify(event.data.input) : undefined,
          status: 'running',
        });
        break;

      case 'tool:complete':
        addToolUse(targetChatId, {
          id: event.data.tool_id || `tool_${Date.now()}`,
          name: event.data.name || 'unknown',
          input: event.data.input ? JSON.stringify(event.data.input) : undefined,
          status: 'done',
        });
        break;

      case 'error':
        setProcessing(targetChatId, false);
        break;
    }
  }, [activeChatId, initChat, setActiveChatId, appendStreamText, completeMessage, addToolUse, setProcessing]);

  // SSE connection
  useSSE({
    url: streamUrl,
    enabled: isSidecarRunning,
    onMessage: handleSSEMessage,
    onError: (error) => console.error('SSE error:', error),
  });

  return null;
}

// Outer component that provides context
interface ChatProps {
  sidecarStatus?: SidecarStatus;
}

export function Chat({ sidecarStatus }: ChatProps) {
  const api = sidecarStatus ? getApiClient(sidecarStatus.port) : getApiClient();

  // Fetch chat list from API
  const handleFetchChatList = useCallback(async (): Promise<ChatItem[]> => {
    try {
      const chats = await api.getChats();
      return chats;
    } catch (error) {
      console.error('Failed to fetch chat list:', error);
      return [];
    }
  }, [api]);

  // Load chat messages from API
  const handleLoadChat = useCallback(async (chatId: string): Promise<Message[]> => {
    try {
      const data = await api.getChat(chatId);
      return data.messages.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: msg.timestamp,
      }));
    } catch (error) {
      console.error('Failed to load chat:', error);
      return [];
    }
  }, [api]);

  // Delete chat via API
  const handleDeleteChat = useCallback(async (chatId: string) => {
    try {
      await api.deleteChat(chatId);
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  }, [api]);

  // Update chat via API
  const handleUpdateChat = useCallback(async (chatId: string, data: { name?: string; avatar?: string }) => {
    try {
      await api.updateChat(chatId, data);
    } catch (error) {
      console.error('Failed to update chat:', error);
    }
  }, [api]);

  // Send message via API (SSE streaming handled separately)
  const handleSendMessage = useCallback(async (chatId: string, prompt: string, agentId: string, _attachments?: Attachment[]) => {
    try {
      // Pass conversation_id to backend so SSE events have matching chat_id
      await api.sendMessage(agentId, prompt, chatId);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [api]);

  return (
    <>
      {sidecarStatus && <SSEHandler sidecarStatus={sidecarStatus} />}
      <ChatProvider
        agents={[
          { id: 'default', name: 'Default Agent' },
        ]}
        onFetchChatList={handleFetchChatList}
        onLoadChat={handleLoadChat}
        onDeleteChat={handleDeleteChat}
        onUpdateChat={handleUpdateChat}
        onSendMessage={handleSendMessage}
      >
        <ChatContent />
      </ChatProvider>
    </>
  )
}

export default Chat
