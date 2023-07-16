import { request } from "@/utils/service"
import type * as Profile from "./types/profile"

/** 獲取配置詳情 */
export function getProfileListApi() {
  return request<Profile.ProfileListResponseData>({
    url: "profile/list",
    method: "get"
  })
}

/** 刪除配置詳情 */
export function deleteProfileApi(profile_index: number) {
  return request<Profile.ProfileListResponseData>({
    url: "profile/del",
    method: "post",
    params: {
      profile_index: profile_index
    }
  })
}

/** 同步Chrome瀏覽器配置 */
export function syncProfileFromChromeApi() {
  return request({
    url: "profile/sync/chrome",
    method: "post"
  })
}

/** 儲存驗證資料詳情 */
export function profileSaveApi(params: any, files: any) {
  return request({
    url: "profile/save",
    method: "post",
    params: params,
    data: files,
    headers: {
      Accept: "application/json",
      "Content-Type": "multipart/form-data"
    }
  })
}
