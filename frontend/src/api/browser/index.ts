import { request } from "@/utils/service"
import type * as Browser from "./types/browser"

/** 新增瀏覽器任務 */
export function browserAddTaskApi(params: any) {
  return request({
    url: "browser/add_task",
    method: "post",
    data: params
  })
}

/** 取得裝置是否運行 **/
export function getBrowserStatusApi(profile_index: number) {
  return request<Browser.BrowserStatusResponseData>({
    url: "browser/status",
    method: "get",
    params: {
      profile_index: profile_index
    }
  })
}
