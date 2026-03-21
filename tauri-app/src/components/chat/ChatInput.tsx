import { useEffect, useRef } from "react";
import {
  PromptInput,
  PromptInputButton,
  PromptInputFooter,
  PromptInputHeader,
  PromptInputSelect,
  PromptInputSelectContent,
  PromptInputSelectItem,
  PromptInputSelectTrigger,
  PromptInputSelectValue,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
  usePromptInputAttachments,
  type PromptInputMessage,
} from "@/components/ai-elements/prompt-input";
import {
  Attachments,
  Attachment,
  AttachmentPreview,
  AttachmentInfo,
} from "@/components/ai-elements/attachments";
import { Bot, PlusIcon } from "lucide-react";
import { cn } from "@/lib/utils";

const MAX_FILES = 10;

// Add attachment button
function AddAttachmentButton() {
  const attachments = usePromptInputAttachments();
  const isFull = attachments.files.length >= MAX_FILES;
  return (
    <PromptInputButton
      size="sm"
      disabled={isFull}
      onClick={() => attachments.openFileDialog()}
    >
      <PlusIcon className="size-4" />
      {attachments.input}
    </PromptInputButton>
  );
}

// Attachment previews in the input box (above textarea)
function AttachmentPreviews() {
  const attachments = usePromptInputAttachments();
  if (attachments.files.length === 0) return null;

  return (
    <PromptInputHeader>
      <Attachments variant="grid" className="p-2 ml-0 w-full">
        {attachments.files.map((file) => (
          <Attachment
            key={file.id}
            data={{ ...file, id: file.id, type: "file" }}
            onRemove={() => attachments.remove(file.id)}
          >
            <AttachmentPreview />
            <AttachmentInfo />
          </Attachment>
        ))}
      </Attachments>
    </PromptInputHeader>
  );
}

export interface ChatInputProps {
  onSubmit: (message: PromptInputMessage) => void | Promise<void>;
  onStop?: () => void;
  status?: "submitted" | "streaming" | "ready" | "error";
  disabled?: boolean;
  placeholder?: string;
  agents?: Array<{ id: string; name: string }>;
  selectedAgentId?: string;
  onAgentChange?: (agentId: string) => void;
  className?: string;
}

export function ChatInput({
  onSubmit,
  onStop,
  status = "ready",
  disabled = false,
  placeholder = "Send a message...",
  agents = [],
  selectedAgentId,
  onAgentChange,
  className,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus when chat becomes ready
  useEffect(() => {
    if (status === "submitted" || status === "streaming") return;

    const frameId = requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });

    return () => cancelAnimationFrame(frameId);
  }, [status]);

  const handleSubmit = async (msg: PromptInputMessage) => {
    const text = msg.text.trim();
    if (!text && msg.files.length === 0) return;
    await onSubmit(msg);
  };

  return (
    <div className={cn("bg-background px-5 py-3 border-t border-subtle-border", className)}>
      <PromptInput
        onSubmit={handleSubmit}
        accept="image/jpeg,image/png,image/gif,image/webp,application/pdf,text/plain,text/markdown,text/csv"
        maxFiles={MAX_FILES}
        maxFileSize={10 * 1024 * 1024}
        status={status}
        disabled={disabled}
      >
        <AttachmentPreviews />
        <div className="relative flex items-end gap-2 rounded-2xl border border-subtle-border bg-muted/30 px-3 py-2 focus-within:ring-2 focus-within:ring-primary/20 transition-shadow">
          <PromptInputTextarea
            ref={textareaRef}
            placeholder={placeholder}
            data-testid="chat-input"
            className="flex-1 border-0 bg-transparent focus:ring-0 resize-none min-h-[24px] max-h-[200px]"
          />
          <PromptInputFooter className="border-0 p-0 gap-1">
            <PromptInputTools className="gap-0.5">
              <AddAttachmentButton />
              {agents.length > 1 && onAgentChange && (
                <PromptInputSelect
                  value={selectedAgentId || agents[0]?.id || ""}
                  onValueChange={onAgentChange}
                >
                  <PromptInputSelectTrigger
                    className="h-7 text-xs gap-1 bg-transparent border-0 hover:bg-muted"
                    data-testid="agent-selector"
                  >
                    <Bot className="h-3.5 w-3.5" />
                    <PromptInputSelectValue />
                  </PromptInputSelectTrigger>
                  <PromptInputSelectContent>
                    {agents.map((a) => (
                      <PromptInputSelectItem
                        key={a.id}
                        value={a.id}
                        data-testid={`agent-option-${a.id}`}
                      >
                        {a.name}
                      </PromptInputSelectItem>
                    ))}
                  </PromptInputSelectContent>
                </PromptInputSelect>
              )}
            </PromptInputTools>
            <PromptInputSubmit
              status={status}
              onStop={onStop}
              data-testid="chat-send"
              size="sm"
              className="rounded-lg"
            />
          </PromptInputFooter>
        </div>
      </PromptInput>
    </div>
  );
}
