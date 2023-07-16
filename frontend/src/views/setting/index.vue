<script setup lang="ts">
import { syncProfileFromChromeApi } from "@/api/profile"
import { ElNotification } from "element-plus"

const syncChromeProfile = async () => {
  await syncProfileFromChromeApi().then((res) => {
    console.log(res)
    ElNotification.success({
      title: "成功",
      message: `同步成功`,
      duration: 3000
    })
  })
}
</script>

<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <h2>瀏覽器設置</h2>
      </template>
      <el-button type="primary" @click="syncChromeProfile">同步 Chrome 配置</el-button>
    </el-card>
  </div>
</template>

<style scoped lang="scss"></style>
