import { create } from "zustand"
import { persist } from "zustand/middleware"

export type Theme = "light" | "dark" | "system"

interface AppState {
  // 主题
  theme: Theme
  setTheme: (theme: Theme) => void

  // 侧边栏
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  collapseSidebar: () => void
  expandSidebar: () => void
}

/**
 * 应用主题到 DOM
 */
export function applyThemeToDOM(theme: Theme) {
  const root = document.documentElement
  root.classList.remove("light", "dark")

  if (theme === "system") {
    const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    root.classList.add(isDark ? "dark" : "light")
  } else {
    root.classList.add(theme)
  }
}

/**
 * 初始化主题监听
 */
export function initThemeListener() {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
  const handleChange = () => {
    const theme = useAppStore.getState().theme
    if (theme === "system") {
      applyThemeToDOM("system")
    }
  }
  mediaQuery.addEventListener("change", handleChange)
  return () => mediaQuery.removeEventListener("change", handleChange)
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // 主题
      theme: "system",
      setTheme: (theme: Theme) => {
        set({ theme })
        applyThemeToDOM(theme)
      },

      // 侧边栏
      sidebarCollapsed: false,
      toggleSidebar: () => {
        set({ sidebarCollapsed: !get().sidebarCollapsed })
      },
      collapseSidebar: () => {
        set({ sidebarCollapsed: true })
      },
      expandSidebar: () => {
        set({ sidebarCollapsed: false })
      },
    }),
    {
      name: "anyclaw-app-store",
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.theme) {
          applyThemeToDOM(state.theme)
        }
      },
    }
  )
)
