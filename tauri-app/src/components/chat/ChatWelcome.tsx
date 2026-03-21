import { cn } from "@/lib/utils";

interface ChatWelcomeProps {
  className?: string;
}

export function ChatWelcome({ className }: ChatWelcomeProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center h-full text-center px-4",
        className
      )}
    >
      {/* Logo with animation */}
      <div className="relative mb-6">
        <div
          className={cn(
            "w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500/20 to-purple-500/20",
            "flex items-center justify-center",
            "transition-transform duration-300 ease-out",
            "hover:scale-110 hover:rotate-3"
          )}
        >
          <img
            src="/icon.svg"
            alt="AnyClaw"
            className="w-12 h-12"
          />
        </div>
      </div>

      {/* Welcome text */}
      <h1 className="text-2xl font-semibold mb-2">
        Welcome to AnyClaw
      </h1>
      <p className="text-muted-foreground text-sm max-w-md mb-8">
        Your AI-powered assistant. Start a conversation to begin.
      </p>

      {/* Quick tips */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg text-left">
        <QuickTip
          title="Ask questions"
          description="Get help with coding, analysis, or any task"
        />
        <QuickTip
          title="Write code"
          description="Generate, debug, or explain code"
        />
        <QuickTip
          title="Search files"
          description="Find and analyze files in your project"
        />
        <QuickTip
          title="Run commands"
          description="Execute shell commands safely"
        />
      </div>
    </div>
  );
}

function QuickTip({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
      <h3 className="font-medium text-sm mb-0.5">{title}</h3>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
