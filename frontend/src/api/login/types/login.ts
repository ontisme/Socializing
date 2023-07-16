export interface LoginRequestData {
  /** admin 或 editor */
  account: "admin" | "editor"
  /** 密碼 */
  password: string
}

export type LoginCodeResponseData = ApiResponseData<string>

export type LoginResponseData = ApiResponseData<{ token: string }>

export type UserInfoResponseData = ApiResponseData<{ account: string; roles: string[] }>
