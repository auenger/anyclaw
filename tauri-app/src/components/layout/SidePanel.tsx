import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

interface SidePanelProps {
  children: ReactNode
  className?: string
}

export function SidePanel({ children, className }: SidePanelProps) {
  return (
    <div
      className={cn(
        "w-[260px] shrink-0 border-r border-[var(--subtle-border)] flex flex-col",
        className
      )}
    >
      {children}
    </div>
  )
}
