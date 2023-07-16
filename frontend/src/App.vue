<script lang="ts" setup>
import { h, onMounted } from "vue"
import { useTheme } from "@/hooks/useTheme"
import zhTw from "element-plus/lib/locale/lang/zh-tw"
const { webFrame } = require("electron")

onMounted(() => {
  window.vIpcRenderer.once("zoom_win", (_, scale: number) => webFrame.setZoomFactor(scale))
  window.vIpcRenderer.once("get_title", (_, args: string) => {
    const style1 = "color: #fff; background: #41b883; padding: 4px; border-radius: 4px;"
    const style2 = "color: #fff; background: #409EFF; padding: 4px 8px; border-radius: 4px;"
    console.log(`%c Hi! %c${args}@v${window.CLIENT_VERSION}`, style1, style2)
  })
  /** 设置窗口 */
  const params = {
    width: 1200,
    height: 800,
    center: true,
    maxable: true,
    resizable: true
  }
  window.vIpcRenderer.send("set_win_size", params)
  /** 打印 应用标题与版本号 */
  window.vIpcRenderer.send("query_title")
})

/** 初始化主题 */
const { initTheme } = useTheme()
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
