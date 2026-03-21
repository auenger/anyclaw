import { ComponentProps, createContext, useContext, useMemo, useState, useCallback } from "react";
import { cn } from "@/lib/utils";
import { FileIcon, ImageIcon, X, FileText, FileSpreadsheet } from "lucide-react";
import { Button } from "@/components/ui/button";

// Types
export interface AttachmentData {
  id: string;
  type: "file" | "image";
  filename: string;
  mediaType: string;
  url?: string;
  filePath?: string;
  size?: number;
}

// Context for attachment group
interface AttachmentContextValue {
  variant: "grid" | "list";
  onRemove?: (id: string) => void;
}

const AttachmentContext = createContext<AttachmentContextValue>({
  variant: "grid",
});

// Attachment container
export type AttachmentsProps = ComponentProps<"div"> & {
  variant?: "grid" | "list";
};

export const Attachments = ({
  variant = "grid",
  className,
  children,
  ...props
}: AttachmentsProps) => {
  const contextValue = useMemo(() => ({ variant }), [variant]);

  return (
    <AttachmentContext.Provider value={contextValue}>
      <div
        className={cn(
          "flex",
          variant === "grid"
            ? "flex-wrap gap-2"
            : "flex-col gap-1",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </AttachmentContext.Provider>
  );
};

// Single attachment wrapper
export interface AttachmentProps extends ComponentProps<"div"> {
  data: AttachmentData;
  onRemove?: (id: string) => void;
}

export const Attachment = ({
  data,
  onRemove,
  className,
  children,
  ...props
}: AttachmentProps) => {
  const context = useContext(AttachmentContext);
  const handleRemove = useCallback(() => {
    onRemove?.(data.id);
  }, [onRemove, data.id]);

  return (
    <div
      className={cn(
        "relative group",
        context.variant === "grid" && "w-20 h-20",
        context.variant === "list" && "w-full",
        className
      )}
      {...props}
    >
      {children}
      {onRemove && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-background/80 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={handleRemove}
        >
          <X className="h-3 w-3" />
        </Button>
      )}
    </div>
  );
};

// Attachment preview (thumbnail for images, icon for files)
export const AttachmentPreview = ({ className }: ComponentProps<"div">) => {
  const context = useContext(AttachmentContext);
  // This would need to receive data from parent context in a real implementation
  // For now, we'll use a simple placeholder
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-lg bg-muted overflow-hidden",
        context.variant === "grid" && "w-full h-full",
        context.variant === "list" && "w-8 h-8 shrink-0",
        className
      )}
    >
      <ImageIcon className="h-6 w-6 text-muted-foreground" />
    </div>
  );
};

// Attachment info (filename, size)
export const AttachmentInfo = ({ className }: ComponentProps<"div">) => {
  return (
    <div className={cn("text-xs truncate", className)}>
      <span className="text-foreground font-medium">file.pdf</span>
    </div>
  );
};

// Attachment remove button (handled in Attachment component)
export const AttachmentRemove = (_props: ComponentProps<"button">) => {
  return null;
};

// Helper to get icon based on media type
export function getAttachmentIcon(mediaType: string): typeof FileIcon {
  if (mediaType.startsWith("image/")) return ImageIcon;
  if (mediaType.includes("spreadsheet") || mediaType.includes("csv")) return FileSpreadsheet;
  if (mediaType.includes("text") || mediaType.includes("pdf")) return FileText;
  return FileIcon;
}

// Helper hook for managing attachments
export function useAttachments(maxFiles: number = 10) {
  const [files, setFiles] = useState<AttachmentData[]>([]);

  const addFiles = useCallback((newFiles: File[]) => {
    const attachments: AttachmentData[] = newFiles.slice(0, maxFiles - files.length).map((file) => ({
      id: crypto.randomUUID(),
      type: file.type.startsWith("image/") ? "image" : "file",
      filename: file.name,
      mediaType: file.type,
      size: file.size,
    }));
    setFiles((prev) => [...prev, ...attachments]);
  }, [files.length, maxFiles]);

  const remove = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const clear = useCallback(() => {
    setFiles([]);
  }, []);

  return { files, addFiles, remove, clear };
}
