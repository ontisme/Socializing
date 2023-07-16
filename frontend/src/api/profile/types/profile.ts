export type ProfileListResponseData = ApiResponseData<{
  index: number
  profile: ProfileInfo
  message: string
}>

interface ProfileInfo {
  name: string
}
