import type {
  ChangeEvent,
  ComponentProps,
  KeyboardEventHandler,
  PropsWithChildren,
  RefObject,
} from "react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";
import {
  CornerDownLeftIcon,
  StopCircleIcon,
} from "lucide-react";

// Types
type ChatStatus = "submitted" | "streaming" | "ready" | "error";

export type PromptInputMessage = {
  text: string;
  files: Array<{
    id: string;
    filename: string;
    mediaType: string;
    filePath?: string;
  }>;
};

// Context
interface PromptInputContextValue {
  id: string;
  value: string;
  setValue: (value: string) => void;
  files: PromptInputMessage["files"];
  setFiles: (files: PromptInputMessage["files"]) => void;
  onSubmit: (message: PromptInputMessage) => void | Promise<void>;
  status: ChatStatus;
  disabled: boolean;
  maxFiles: number;
  maxFileSize: number;
  accept: string;
}

const PromptInputContext = createContext<PromptInputContextValue | null>(null);

function usePromptInput() {
  const context = useContext(PromptInputContext);
  if (!context) {
    throw new Error("usePromptInput must be used within PromptInput");
  }
  return context;
}

// Root component
export type PromptInputProps = PropsWithChildren<{
  onSubmit: (message: PromptInputMessage) => void | Promise<void>;
  value?: string;
  onValueChange?: (value: string) => void;
  defaultValue?: string;
  status?: ChatStatus;
  disabled?: boolean;
  maxFiles?: number;
  maxFileSize?: number;
  accept?: string;
  className?: string;
}>;

export function PromptInput({
  children,
  onSubmit,
  value: controlledValue,
  onValueChange,
  defaultValue = "",
  status = "ready",
  disabled = false,
  maxFiles = 10,
  maxFileSize = 10 * 1024 * 1024, // 10MB
  accept = "image/*,.pdf,.txt,.md,.csv",
  className,
}: PromptInputProps) {
  const id = useId();
  const [internalValue, setInternalValue] = useState(defaultValue);
  const [files, setFiles] = useState<PromptInputMessage["files"]>([]);

  const value = controlledValue ?? internalValue;
  const setValue = useCallback(
    (newValue: string) => {
      if (onValueChange) {
        onValueChange(newValue);
      } else {
        setInternalValue(newValue);
      }
    },
    [onValueChange]
  );

  const handleSubmit = useCallback(
    async (message: PromptInputMessage) => {
      await onSubmit(message);
    },
    [onSubmit]
  );

  const contextValue = useMemo(
    () => ({
      id,
      value,
      setValue,
      files,
      setFiles,
      onSubmit: handleSubmit,
      status,
      disabled,
      maxFiles,
      maxFileSize,
      accept,
    }),
    [
      id,
      value,
      setValue,
      files,
      setFiles,
      handleSubmit,
      status,
      disabled,
      maxFiles,
      maxFileSize,
      accept,
    ]
  );

  return (
    <PromptInputContext.Provider value={contextValue}>
      <div className={cn("relative", className)}>{children}</div>
    </PromptInputContext.Provider>
  );
}

// Textarea
export type PromptInputTextareaProps = Omit<
  ComponentProps<"textarea">,
  "value" | "onChange"
> & {
  ref?: RefObject<HTMLTextAreaElement>;
};

export const PromptInputTextarea = ({
  className,
  onKeyDown,
  ref,
  ...props
}: PromptInputTextareaProps) => {
  const { value, setValue, onSubmit, status, disabled, files } =
    usePromptInput();
  const textareaRef = ref || useRef<HTMLTextAreaElement>(null);

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
    },
    [setValue]
  );

  const handleKeyDown: KeyboardEventHandler<HTMLTextAreaElement> = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
        e.preventDefault();
        if (status === "ready" && !disabled && (value.trim() || files.length > 0)) {
          onSubmit({ text: value, files });
          setValue("");
        }
      }
      onKeyDown?.(e);
    },
    [onKeyDown, status, disabled, value, files, onSubmit, setValue]
  );

  // Auto-resize
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const isDisabled = disabled || status === "submitted";

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      disabled={isDisabled}
      className={cn(
        "w-full resize-none bg-transparent text-sm outline-none",
        "min-h-[24px] max-h-[200px]",
        "placeholder:text-muted-foreground",
        isDisabled && "cursor-not-allowed opacity-50",
        className
      )}
      rows={1}
      {...props}
    />
  );
};

// Header (for attachments)
export const PromptInputHeader = ({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) => {
  return <div className={cn("mb-2", className)}>{children}</div>;
};

// Footer
export const PromptInputFooter = ({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) => {
  return (
    <div
      className={cn(
        "flex items-center justify-between gap-2 pt-2",
        className
      )}
    >
      {children}
    </div>
  );
};

// Tools (left side of footer)
export const PromptInputTools = ({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) => {
  return (
    <div className={cn("flex items-center gap-1", className)}>{children}</div>
  );
};

// Button
export const PromptInputButton = ({
  children,
  className,
  variant = "ghost",
  size = "icon",
  ...props
}: ComponentProps<typeof Button>) => {
  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      className={cn("h-8 w-8", className)}
      {...props}
    >
      {children}
    </Button>
  );
};

// Submit button
export const PromptInputSubmit = ({
  status,
  onStop,
  className,
  children,
  ...props
}: ComponentProps<typeof Button> & {
  status?: ChatStatus;
  onStop?: () => void;
}) => {
  const { value, files, onSubmit, setValue, disabled } = usePromptInput();

  const isWorking = status === "submitted" || status === "streaming";
  const canSubmit = (value.trim() || files.length > 0) && !disabled;

  const handleClick = useCallback(() => {
    if (isWorking && onStop) {
      onStop();
    } else if (canSubmit) {
      onSubmit({ text: value, files });
      setValue("");
    }
  }, [isWorking, onStop, canSubmit, onSubmit, value, files, setValue]);

  return (
    <Button
      type="button"
      size="sm"
      disabled={!isWorking && !canSubmit}
      onClick={handleClick}
      className={cn("gap-1.5", className)}
      {...props}
    >
      {isWorking ? (
        <>
          {status === "streaming" ? (
            <>
              <StopCircleIcon className="h-4 w-4" />
              {children || "Stop"}
            </>
          ) : (
            <>
              <Spinner className="h-4 w-4" />
              {children || "Sending..."}
            </>
          )}
        </>
      ) : (
        <>
          <CornerDownLeftIcon className="h-4 w-4" />
          {children || "Send"}
        </>
      )}
    </Button>
  );
};

// Select (for agents)
export const PromptInputSelect = ({
  children,
  value,
  onValueChange,
}: PropsWithChildren<{
  value: string;
  onValueChange: (value: string) => void;
}>) => {
  return (
    <Select value={value} onValueChange={onValueChange}>
      {children}
    </Select>
  );
};

export const PromptInputSelectTrigger = ({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) => {
  return (
    <SelectTrigger className={cn("h-8", className)}>
      {children}
    </SelectTrigger>
  );
};

export const PromptInputSelectValue = ({
  placeholder,
}: {
  placeholder?: string;
}) => {
  return <SelectValue placeholder={placeholder} />;
};

export const PromptInputSelectContent = ({
  children,
}: PropsWithChildren) => {
  return <SelectContent>{children}</SelectContent>;
};

export const PromptInputSelectItem = ({
  children,
  value,
  className,
}: PropsWithChildren<{ value: string; className?: string }>) => {
  return (
    <SelectItem value={value} className={className}>
      {children}
    </SelectItem>
  );
};

// Hook for file attachments
export function usePromptInputAttachments() {
  const { files, setFiles, maxFiles, maxFileSize, accept } = usePromptInput();
  const inputRef = useRef<HTMLInputElement>(null);

  const openFileDialog = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const fileList = e.target.files;
      if (!fileList) return;

      const newFiles = Array.from(fileList)
        .filter((file) => file.size <= maxFileSize)
        .slice(0, maxFiles - files.length)
        .map((file) => ({
          id: crypto.randomUUID(),
          filename: file.name,
          mediaType: file.type,
        }));

      setFiles([...files, ...newFiles]);
      e.target.value = "";
    },
    [files, maxFiles, maxFileSize, setFiles]
  );

  const remove = useCallback(
    (id: string) => {
      setFiles(files.filter((f) => f.id !== id));
    },
    [files, setFiles]
  );

  const input = (
    <input
      ref={inputRef}
      type="file"
      accept={accept}
      multiple
      className="hidden"
      onChange={handleFileChange}
    />
  );

  return { files, openFileDialog, remove, input };
}
