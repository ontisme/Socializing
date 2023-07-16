<script lang="ts" setup>
import { ref, watch } from "vue"
import { usePagination } from "@/hooks/usePagination"
import { ElMessage, ElMessageBox, ElNotification } from "element-plus"
import { useUserStore } from "@/store/modules/user"
import { deleteProfileApi, getProfileListApi } from "@/api/profile"
import { ProfileListResponseData } from "@/api/profile/types/profile"
import { browserAddTaskApi, getBrowserStatusApi } from "@/api/browser"
import { ProfileItem } from "@/views/dashboard/types/dashboard"

type CurrentRole = "admin" | "editor"
const userStore = useUserStore()
const currentRole = ref<CurrentRole>("admin")
if (!userStore.roles.includes("admin")) {
  currentRole.value = "editor"
}
const cardCollapse = ref<boolean>(false)
const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()
const batchComment = ref("")
const randomBatchComment = ref("")
const editDrawer = ref(false)
const editPlatform = ref("")
const editForm = ref<any>({
  account: "",
  password: ""
})
const multipleTableRef = ref()
const multipleSelection = ref([])
const toggleCardCollapse = () => {
  cardCollapse.value = !cardCollapse.value
}
//#region 查
const tableData = ref<ProfileListResponseData[]>([])
const getTableData = () => {
  loading.value = true
  getProfileListApi()
    .then((res: any) => {
      paginationData.total = res.data.total
      tableData.value = res.data.list
    })
    .catch(() => {
      tableData.value = []
    })
    .finally(() => {
      loading.value = false
    })
}

const handleEdit = (data: any) => {
  editPlatform.value = data.platform_name
  editForm.value = {
    account: data.account,
    password: data.password
  }
  editDrawer.value = true
}

const handleAddTask = async (data: any, action: string) => {
  if (data.comment === undefined && action === "comment") {
    ElMessage.error("請填寫留言內容")
    return
  }

  await browserAddTaskApi({
    profile_index: data.index,
    script: "C:\\Users\\User\\PycharmProjects\\Socializing\\script\\facebook.py",
    params: {
      page_id: "100078408274064",
      action: action,
      comment: data.comment,
      idle_time: 30
    }
  })
}

const handleDeleteProfile = async (data: any) => {
  // 先跳出確認是否刪除視窗，並且告知僅會刪除配置檔，不會刪除實際的瀏覽器資料

  ElMessageBox.confirm("確定要刪除該配置檔嗎？", "提醒", {
    confirmButtonText: "是",
    cancelButtonText: "否",
    type: "error",
    draggable: true
  }).then(async () => {
    await deleteProfileApi(data.index)
    ElNotification.success({
      title: "成功",
      message: `刪除成功 [${data.facebook.name}]`,
      duration: 3000
    })
    getTableData()
  })
}

const handleBatch = async (action: string) => {
  if (batchComment.value.trim() === "" && action === "comment") {
    ElMessage.error("請填寫批量留言內容")
    return
  }

  console.log("handleBatchPush")
  console.log(multipleSelection)
  let selectionRange: number[] = [] // 用于存储任务范围的数组

  if (Array.isArray(multipleSelection.value) && multipleSelection.value.length > 0) {
    // 如果有选中项，则使用选中项作为任务范围
    selectionRange = multipleSelection.value.map((item: ProfileItem) => item.index)
  } else {
    ElMessage.error("沒有勾選要操作的使用者")
    return
  }
  for (const index of selectionRange) {
    const data = {
      index: index,
      comment: randomBatchComment.value
    }
    await handleAddTask(data, action)
  }
}
const randomBatchAmount = ref(0) // 隨機批量數量
const randomBatchMaxAmount = ref(1) // 隨機批量最大數量
const handleRandomBatch = async (action: string) => {
  if (randomBatchComment.value.trim() === "" && action === "comment") {
    ElMessage.error("請填寫隨機留言內容")
    return
  }
  let selectionRange: number[] = [] // 用于存储任务范围的数组

  if (Array.isArray(multipleSelection.value) && multipleSelection.value.length > 0) {
    // 如果有选中项，则使用选中项作为任务范围
    selectionRange = multipleSelection.value.map((item: ProfileItem) => item.index)
  } else {
    // 如果没有选中项，则将任务范围设置为全部数据
    selectionRange = tableData.value.map((item: any) => item.index)
  }

  for (const index of selectionRange) {
    const data = {
      index: index,
      comment: randomBatchComment.value
    }
    await handleAddTask(data, action)
  }
}

const handleUpdateProfile = async (data: any) => {
  await browserAddTaskApi({
    profile_index: data.index,
    script: "C:\\Users\\User\\PycharmProjects\\Socializing\\script\\facebook_get_profile.py",
    params: {}
  })
  // 循環檢查 await getBrowserStatusApi(data.index) 等待返回 True 超過一分鐘則跳出錯誤
  const startTime = Date.now()
  const timeout = 60000 // 1 minute timeout

  let isBrowserStatusTrue = false

  while (!isBrowserStatusTrue) {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    const browserStatus = await getBrowserStatusApi(data.index)
    if (browserStatus.data === false) {
      isBrowserStatusTrue = true
    }

    const elapsedTime = Date.now() - startTime
    if (elapsedTime >= timeout) {
      throw new Error("Timeout: Browser status did not return true within 1 minute.")
    }
  }

  ElNotification.success({
    title: "成功",
    message: `建檔成功 ID:${data.index} 名稱:${data.facebook.name}`,
    duration: 3000
  })
  getTableData()
}

const handleBatchUpdateProfile = async () => {
  const totalLength = multipleSelection.value.length
  if (Array.isArray(multipleSelection.value) && multipleSelection.value.length > 0) {
    // 如果有选中项
  } else {
    ElMessage.error("沒有勾選要操作的使用者")
    return
  }

  let count = 1
  for (const data of multipleSelection.value) {
    const c = data as ProfileItem

    ElNotification.success({
      title: "成功",
      message: `正在建檔 ID:${c.index} 名稱:${c.facebook.name} [${count}/${totalLength}]`,
      duration: 3000
    })

    await handleUpdateProfile(c)
    count++
  }
}

// const handleEditConfirm = () => {
//   clientEditApi(editPlatform.value, editForm.value)
//     .then((res) => {
//       console.log(res)
//     })
//     .catch(() => {
//       console.log("error")
//     })
//     .finally(() => {
//       console.log("finally")
//       editDrawer.value = false
//       getTableData()
//
//       ElNotification({
//         title: "更新成功",
//         comment: `修改 ${editPlatform.value} 成功`,
//         type: "success"
//       })
//     })
// }
const handleEditCancel = () => {
  editDrawer.value = false
}
const handleSelectionChange = (val) => {
  multipleSelection.value = val
}
//#endregion
/** 监听分页参数的变化 */
watch([() => paginationData.currentPage, () => paginationData.pageSize], getTableData, { immediate: true })
/** 監聽 multipleSelection */
watch(multipleSelection, (val) => {
  console.log(val)
  if (Array.isArray(val) && val.length > 0) {
    randomBatchMaxAmount.value = val.length
  } else {
    randomBatchMaxAmount.value = tableData.value.length
  }
})
defineOptions({
  name: "ElementPlus"
})
</script>

<template>
  <div class="app-container">
    <el-scrollbar height="500px">
      <el-card v-loading="loading" shadow="never">
        <div class="table-wrapper">
          <el-button type="primary" @click="getTableData">手動更新列表</el-button>
          <el-button type="primary" @click="handleBatchUpdateProfile">批次建檔</el-button>
          <el-table
            ref="multipleTableRef"
            :data="tableData"
            border
            class="mt-4"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column prop="index" label="序列" width="60" align="center" />
            <!--          <el-table-column prop="profile.name" label="配置名稱" width="100" align="center" />-->
            <el-table-column prop="facebook.name" label="臉書名稱" width="100" align="center" />
            <el-table-column prop="facebook.img" label="照片" width="100" align="center">
              <template #default="scope">
                <el-image
                  fit="cover"
                  :preview-src-list="[`data:image/png;base64,${scope.row.facebook.img}`]"
                  :src="`data:image/png;base64,${scope.row.facebook.img}`"
                  alt=""
                />
              </template>
            </el-table-column>
            <el-table-column prop="comment" label="留言內容" align="center">
              <template #default="scope">
                <el-input v-model="scope.row.comment" />
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" width="250" align="center">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleAddTask(scope.row, 'comment')">留言</el-button>
                <el-button type="primary" size="small" @click="handleAddTask(scope.row, 'like')">讚</el-button>
                <el-button type="primary" size="small" @click="handleAddTask(scope.row, 'share')">分享</el-button>

                <el-dropdown trigger="click">
                  <el-button type="primary" text size="small" icon="Expand" />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="handleUpdateProfile(scope.row)">建檔</el-dropdown-item>
                      <el-dropdown-item divided @click="handleDeleteProfile(scope.row)">刪除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="batch-controls-container">
          <el-collapse>
            <el-collapse-item title="批次操作區" name="1">
              <el-card class="mt-4">
                <el-row :gutter="80">
                  <el-col :span="12">
                    <div class="batch-controls">
                      <h3>批次操控區</h3>
                      <el-input class="mb-4" type="textarea" v-model="batchComment" placeholder="Enter a comment..." />
                      <el-button type="primary" @click="handleBatch('comment')">留言</el-button>
                      <el-button type="primary" @click="handleBatch('like')">按讚</el-button>
                      <el-button type="primary" @click="handleBatch('share')">分享</el-button>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="random-batch-controls mt-4">
                      <h3>隨機批次操控區（有勾選即只隨機勾選範圍）</h3>
                      <div>
                        <el-input
                          class="mb-4"
                          type="textarea"
                          v-model="randomBatchComment"
                          placeholder="Enter a comment..."
                        />
                        <el-button type="primary" @click="handleRandomBatch('comment')">留言</el-button>
                        <el-button type="primary" @click="handleRandomBatch('like')">按讚</el-button>
                        <el-button type="primary" @click="handleRandomBatch('share')">分享</el-button>
                        <el-slider
                          v-if="tableData && tableData.length > 0"
                          v-model="randomBatchAmount"
                          :min="1"
                          :max="randomBatchMaxAmount"
                          :step="1"
                          show-input
                        />
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </el-card>
            </el-collapse-item>
          </el-collapse>
        </div>
        <!--      <div class="pager-wrapper">-->
        <!--        <el-pagination-->
        <!--          background-->
        <!--          :layout="paginationData.layout"-->
        <!--          :page-sizes="paginationData.pageSizes"-->
        <!--          :total="paginationData.total"-->
        <!--          :page-size="paginationData.pageSize"-->
        <!--          :currentPage="paginationData.currentPage"-->
        <!--          @size-change="handleSizeChange"-->
        <!--          @current-change="handleCurrentChange"-->
        <!--        />-->
        <!--      </div>-->
      </el-card>
    </el-scrollbar>
    <!--  EDIT PLACE-->
    <el-drawer v-model="editDrawer" direction="rtl">
      <template #header>
        <h4>{{ editPlatform }} 設定</h4>
      </template>
      <template #default>
        <div>
          <el-form label-width="100px" label-position="top">
            <el-form-item label="帳號">
              <el-input v-model="editForm.account" />
            </el-form-item>
            <el-form-item label="密碼">
              <el-input v-model="editForm.password" />
            </el-form-item>
          </el-form>
        </div>
      </template>
      <template #footer>
        <div style="flex: auto">
          <el-button @click="handleEditCancel">取消</el-button>
          <!--        <el-button type="primary" @click="handleEditConfirm">確認</el-button>-->
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<style lang="scss" scoped>
.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
.batch-controls-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 16px;
  z-index: 9999;
}
</style>
