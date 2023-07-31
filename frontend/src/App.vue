<script lang="ts" setup>
import { useTheme } from "@/hooks/useTheme"
import zhTw from "element-plus/lib/locale/lang/zh-tw"

const { initTheme } = useTheme()

/** 初始化主题 */
initTheme()
/** 将 Element Plus 的语言设置为中文 */
const locale = zhTw

// end
</script>

<template>
  <ElConfigProvider :locale="locale">
    <router-view />
  </ElConfigProvider>
</template>
