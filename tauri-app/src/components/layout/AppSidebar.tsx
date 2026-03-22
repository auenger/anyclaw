import { NavLink } from "react-router-dom";
import {
  Bot,
  CalendarClock,
  Brain,
  ScrollText,
  PanelLeftClose,
  PanelLeft,
  SquarePen,
  Settings2,
  Github,
  BookOpen,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/hooks/useSidebar";
import { usePlatform } from "@/hooks/usePlatform";
import { useDragRegion } from "@/hooks/useDragRegion";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import logoImage from "@/assets/logo.png";

/** Inline horizontal padding, keeps icon centered within 52px when collapsed (8+36+8=52) */
const ROW_PX = "px-2";

interface AppSidebarProps {
  onOpenSettings?: (tab?: string) => void;
}

export function AppSidebar({ onOpenSettings }: AppSidebarProps) {
  const { isCollapsed, toggle } = useSidebar();
  const { isMac } = usePlatform();
  const drag = useDragRegion();

  const navItems = [
    { to: "/", icon: SquarePen, label: "Chat" },
    { to: "/agents", icon: Bot, label: "Agents" },
    { to: "/tasks", icon: CalendarClock, label: "Tasks" },
    { to: "/memory", icon: Brain, label: "Memory" },
    { to: "/logs", icon: ScrollText, label: "Logs" },
  ];

  // Avatar 组件
  const AvatarView = ({ size = "md" }: { size?: "sm" | "md" }) => {
    const sizeClass = size === "sm" ? "w-6 h-6 text-[10px]" : "w-8 h-8 text-xs";

    return (
      <div className={cn("rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center text-primary-foreground font-bold", sizeClass)}>
        <User className={size === "sm" ? "h-3 w-3" : "h-4 w-4"} />
      </div>
    );
  };

  return (
    <aside
      className={cn(
        "shrink-0 flex flex-col overflow-hidden",
        "bg-muted/30 border-r",
        "border-[var(--subtle-border)]",
        "transition-[width] duration-200 ease-[var(--ease-soft)]",
        isCollapsed ? "w-[52px]" : "w-[220px]",
      )}
      aria-expanded={!isCollapsed}
    >
      {/* macOS: traffic light spacing — draggable */}
      {isMac && <div className="h-11 shrink-0" {...drag} />}

      {/* Top action bar */}
      <div className={cn("flex items-center h-[52px] shrink-0", ROW_PX)}>
        {isCollapsed ? (
          <button
            type="button"
            onClick={toggle}
            className="w-9 h-9 shrink-0 rounded-[10px] flex items-center justify-center hover:bg-[var(--surface-hover)] transition-all duration-200 ease-[var(--ease-soft)]"
            aria-label="展开侧边栏"
          >
            <PanelLeft className="h-4 w-4" />
          </button>
        ) : (
          <div className="flex items-center gap-1.5 ml-1.5 mr-1">
            <img
              src={logoImage}
              alt="AnyClaw"
              className="h-5 w-5 rounded-md object-contain"
            />
            <span className="text-md font-semibold tracking-tight whitespace-nowrap text-primary">
              AnyClaw
            </span>
          </div>
        )}
        <div className="flex-1 min-w-0" />
        <button
          type="button"
          onClick={toggle}
          className={cn(
            "w-9 h-9 shrink-0 rounded-[10px] flex items-center justify-center hover:bg-[var(--surface-hover)] transition-all duration-200 ease-[var(--ease-soft)]",
            isCollapsed ? "opacity-0 pointer-events-none" : "opacity-100",
          )}
          aria-label="折叠侧边栏"
          tabIndex={isCollapsed ? -1 : 0}
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>

      {/* Page navigation */}
      <nav className="space-y-0.5 px-1.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            data-testid={`nav-${item.to === "/" ? "chat" : item.to.slice(1)}`}
            className={({ isActive }) =>
              cn(
                "flex items-center h-9 rounded-[10px] whitespace-nowrap overflow-hidden",
                "transition-all duration-200 ease-[var(--ease-soft)]",
                isCollapsed ? "px-0.5" : "px-1",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-[var(--surface-hover)]",
              )
            }
            aria-label={item.label}
          >
            <div className="w-9 h-9 shrink-0 flex items-center justify-center">
              <item.icon className="h-4 w-4" />
            </div>
            <span
              className={cn(
                "text-sm transition-opacity duration-200",
                isCollapsed ? "opacity-0" : "opacity-100",
              )}
            >
              {item.label}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* Spacer — draggable for window movement */}
      <div className="flex-1" {...drag} />

      {/* Bottom: user avatar popup menu */}
      <div className="border-t border-[var(--subtle-border)] py-2 px-1.5">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              className={cn(
                "flex items-center w-full h-9 rounded-[10px] whitespace-nowrap overflow-hidden outline-none",
                "transition-all duration-200 ease-[var(--ease-soft)]",
                isCollapsed ? "px-0.5" : "px-1",
                "text-muted-foreground hover:text-foreground hover:bg-[var(--surface-hover)]",
              )}
            >
              <div className="w-9 h-9 shrink-0 flex items-center justify-center">
                <AvatarView size="md" />
              </div>
              <div
                className={cn(
                  "flex-1 min-w-0 text-left ml-1.5 transition-opacity duration-200",
                  isCollapsed ? "opacity-0" : "opacity-100",
                )}
              >
                <p className="text-xs font-semibold truncate">本地模式</p>
                <p className="text-[10px] text-muted-foreground truncate">AnyClaw Desktop</p>
              </div>
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            side="top"
            align="start"
            sideOffset={8}
            className="w-[240px] rounded-xl p-2"
          >
            <div className="flex flex-col items-center py-3 px-2">
              <div className="mb-2">
                <AvatarView size="md" />
              </div>
              <p className="text-sm font-semibold truncate max-w-full">本地模式</p>
              <p className="text-[11px] text-muted-foreground truncate max-w-full">AnyClaw Desktop</p>
            </div>

            <DropdownMenuSeparator />

            {onOpenSettings && (
              <DropdownMenuItem onClick={() => onOpenSettings()} className="gap-3 px-3 py-2.5 rounded-lg cursor-pointer">
                <Settings2 className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">设置</span>
              </DropdownMenuItem>
            )}

            <DropdownMenuItem onClick={() => window.open("https://github.com/CodePhiliaX/AnyClaw", "_blank")} className="gap-3 px-3 py-2.5 rounded-lg cursor-pointer">
              <Github className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">GitHub</span>
            </DropdownMenuItem>

            {onOpenSettings && (
              <DropdownMenuItem onClick={() => onOpenSettings("about")} className="gap-3 px-3 py-2.5 rounded-lg cursor-pointer">
                <BookOpen className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">关于</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
