<script lang="ts" setup>
import { useSettingsStore } from "@/store/modules/settings"

const settingsStore = useSettingsStore()
</script>

<template>
  <div class="drawer-container">
    <div>
      <h3 class="drawer-title">系統布局配置</h3>
      <div class="drawer-item">
        <span>顯示標簽欄</span>
        <el-switch v-model="settingsStore.showTagsView" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示側邊欄 Logo</span>
        <el-switch v-model="settingsStore.showSidebarLogo" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>固定 Header</span>
        <el-switch v-model="settingsStore.fixedHeader" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示消息通知</span>
        <el-switch v-model="settingsStore.showNotify" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示切換主題按鈕</span>
        <el-switch v-model="settingsStore.showThemeSwitch" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示全屏按鈕</span>
        <el-switch v-model="settingsStore.showScreenfull" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示灰色模式</span>
        <el-switch v-model="settingsStore.showGreyMode" class="drawer-switch" />
      </div>
      <div class="drawer-item">
        <span>顯示色弱模式</span>
        <el-switch v-model="settingsStore.showColorWeakness" class="drawer-switch" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.drawer-container {
  padding: 24px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  .drawer-title {
    margin-bottom: 12px;
    font-size: 14px;
    line-height: 22px;
  }
  .drawer-item {
    font-size: 14px;
    padding: 12px 0;
  }
  .drawer-switch {
    float: right;
  }
}
</style>
