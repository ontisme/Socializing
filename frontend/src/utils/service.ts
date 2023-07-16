import axios, { type AxiosInstance, type AxiosRequestConfig } from "axios"
import { useUserStoreHook } from "@/store/modules/user"
import { ElMessage } from "element-plus"
import { get } from "lodash-es"
import { getToken } from "./cache/sessionStorage"

/** 創建請求實例 */
function createService() {
  // 創建一個 Axios 實例
  const service = axios.create()
  // 請求攔截
  service.interceptors.request.use(
    (config) => config,
    // 發送失敗
    (error) => Promise.reject(error)
  )
  // 響應攔截（可根據具體業務作出相應的調整）
  service.interceptors.response.use(
    (response) => {
      // apiData 是 API 返回的數據
      const apiData = response.data as any
      // 這個 Code 是和後端約定的業務 Code
      const code = apiData.code
      // 如果沒有 Code, 代表這不是項目後端開發的 API
      if (code === undefined) {
        ElMessage.error("非本系統的接口")
        return Promise.reject(new Error("非本系統的接口"))
      } else {
        switch (code) {
          case 0:
            // code === 0 代表沒有錯誤
            return apiData
          default:
            // 不是正確的 Code
            ElMessage.error(apiData.message || "Error")
            return Promise.reject(new Error("Error"))
        }
      }
    },
    (error) => {
      // Status 是 HTTP 狀態碼
      const status = get(error, "response.status")
      switch (status) {
        case 400:
          error.message = "請求錯誤"
          break
        case 401:
          // Token 過期時，直接退出登入並強制刷新頁面（會重定向到登入頁）
          useUserStoreHook().logout()
          location.reload()
          break
        case 403:
          error.message = "拒絕訪問"
          break
        case 404:
          error.message = "請求地址出錯"
          break
        case 408:
          error.message = "請求超時"
          break
        case 500:
          error.message = "服務器內部錯誤"
          break
        case 501:
          error.message = "服務未實現"
          break
        case 502:
          error.message = "網關錯誤"
          break
        case 503:
          error.message = "服務不可用"
          break
        case 504:
          error.message = "網關超時"
          break
        case 505:
          error.message = "HTTP 版本不受支持"
          break
        default:
          break
      }
      ElMessage.error(error.message)
      return Promise.reject(error)
    }
  )
  return service
}

/** 創建請求方法 */
function createRequestFunction(service: AxiosInstance) {
  return function <T>(config: AxiosRequestConfig): Promise<T> {
    const configDefault = {
      headers: {
        // 攜帶 Token
        Authorization: "Bearer " + getToken(),
        "Content-Type": get(config, "headers.Content-Type", "application/json")
      },
      timeout: 60000,
      baseURL: "http://localhost:34567/api/",
      data: {}
    }
    return service(Object.assign(configDefault, config))
  }
}

/** 用於網絡請求的實例 */
export const service = createService()
/** 用於網絡請求的方法 */
export const request = createRequestFunction(service)
