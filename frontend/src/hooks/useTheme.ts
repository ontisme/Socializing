import { ref, watchEffect } from "vue"
import { getActiveThemeName, setActiveThemeName } from "@/utils/cache/localStorage"

const DEFAULT_THEME_NAME = "normal"
type DefaultThemeName = typeof DEFAULT_THEME_NAME

/** 註冊的主題名稱, 其中 DefaultThemeName 是必填的 */
export type ThemeName = DefaultThemeName | "dark" | "dark-blue"

interface ThemeList {
  title: string
  name: ThemeName
}

/** 主題列表 */
const themeList: ThemeList[] = [
  {
    title: "默認",
    name: DEFAULT_THEME_NAME
  },
  {
    title: "黑暗",
    name: "dark"
  },
  {
    title: "深藍",
    name: "dark-blue"
  }
]

/** 正在應用的主題名稱 */
const activeThemeName = ref<ThemeName>(getActiveThemeName() || DEFAULT_THEME_NAME)

/** 設置主題 */
const setTheme = (value: ThemeName) => {
  activeThemeName.value = value
}

/** 在 html 根元素上掛載 class */
const setHtmlRootClassName = (value: ThemeName) => {
  document.documentElement.className = value
}

/** 初始化 */
const initTheme = () => {
  // watchEffect 來收集副作用
  watchEffect(() => {
    const value = activeThemeName.value
    setHtmlRootClassName(value)
    setActiveThemeName(value)
  })
}

/** 主題 hook */
export function useTheme() {
  return { themeList, activeThemeName, initTheme, setTheme }
}
