import { User } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Message as AIMessage,
} from "@/components/ai-elements/message";
import type { Message } from "@/stores/chat";

function UserAvatar() {
  const sizeClass = "w-8 h-8 text-xs";

  return (
    <div
      className={cn(
        "rounded-full bg-muted flex items-center justify-center text-muted-foreground",
        sizeClass,
      )}
    >
      <User className="h-4 w-4" />
    </div>
  );
}

interface UserMessageProps {
  message: Message & { role: 'user' };
}

export function UserMessage({ message }: UserMessageProps) {
  return (
    <AIMessage from="user" data-testid="message-user">
      <div className="group flex gap-3 py-3 flex-row-reverse">
        <div className="mt-0.5">
          <UserAvatar />
        </div>
        <div className="flex-1 min-w-0 flex flex-col items-end">
          <div className="text-xs font-medium text-muted-foreground mb-1.5">
            <span className="ml-2 text-[10px] opacity-60">
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
          <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-md px-4 py-2.5 max-w-[85%]">
            <p className="text-sm whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          </div>
        </div>
      </div>
    </AIMessage>
  );
}
