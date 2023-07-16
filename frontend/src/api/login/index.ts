import { request } from "@/utils/service"
import type * as Login from "./types/login"

/** 登入并返回 Token */
export function loginApi(data: Login.LoginRequestData) {
  return request<Login.LoginResponseData>({
    url: "/client/users/login",
    method: "post",
    data
  })
}

/** 获取用户详情 */
export function getUserInfoApi() {
  return request<Login.UserInfoResponseData>({
    url: "/client/users/info",
    method: "get"
  })
}
