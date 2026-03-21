import { useEffect, useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Check, Copy, FileCode } from "lucide-react";
import { codeToHtml } from "shiki";

interface CodeBlockProps {
  language: string;
  code: string;
  className?: string;
  showLineNumbers?: boolean;
}

export function CodeBlock({
  language,
  code,
  className,
  showLineNumbers = false,
}: CodeBlockProps) {
  const [html, setHtml] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const preRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    async function highlight() {
      try {
        const highlighted = await codeToHtml(code, {
          lang: language.toLowerCase() || "text",
          theme: "github-dark",
        });
        setHtml(highlighted);
      } catch {
        // Fallback to plain text if shiki fails
        setHtml(`<pre class="shiki"><code>${escapeHtml(code)}</code></pre>`);
      }
    }
    highlight();
  }, [code, language]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split("\n");
  const lineCount = lines.length;

  return (
    <div className={cn("relative group rounded-lg overflow-hidden", className)}>
      {/* Header */}
      <div className="flex items-center justify-between bg-zinc-800/50 px-4 py-2 text-xs">
        <div className="flex items-center gap-2 text-zinc-400">
          <FileCode className="h-3.5 w-3.5" />
          <span>{language || "code"}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-zinc-400 hover:text-zinc-200"
          onClick={handleCopy}
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 mr-1" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3 mr-1" />
              <span>Copy</span>
            </>
          )}
        </Button>
      </div>

      {/* Code content */}
      <div className="relative overflow-x-auto">
        {showLineNumbers && (
          <div className="absolute left-0 top-0 bottom-0 w-10 bg-zinc-900/50 flex flex-col items-end pr-3 pt-4 text-zinc-500 text-xs font-mono select-none">
            {Array.from({ length: lineCount }, (_, i) => (
              <div key={i} className="leading-6">
                {i + 1}
              </div>
            ))}
          </div>
        )}
        <pre
          ref={preRef}
          className={cn(
            "!bg-zinc-900 p-4 text-sm overflow-x-auto",
            showLineNumbers && "pl-14"
          )}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      </div>
    </div>
  );
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
