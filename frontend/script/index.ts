import PKG from "../package.json"
import NodePath from "path"
import EleLog from "electron-log"
import {
  app,
  screen,
  dialog,
  ipcMain,
  Tray,
  Menu,
  BrowserWindow,
  type MessageBoxSyncOptions,
  type BrowserWindowConstructorOptions
} from "electron"
import * as remote from "@electron/remote/main"
const cmd = require("node-cmd");

//#region 全局配置 - 日志器
// 日志路徑
// on Linux: ~/.config/{app name}/logs/{process type}.log
// on macOS: ~/Library/Logs/{app name}/{process type}.log
// on Windows: %USERPROFILE%\AppData\Roaming\{app name}\logs\{process type}.log
// 日志設置
EleLog.transports.file.format = "[{y}-{m}-{d} {h}:{i}:{s}.{ms}] [{level}]{scope} \n{text} \n"
EleLog.transports.file.maxSize = 10 * 1024 * 1024
//#endregion

//#region 全局配置 - 進程
/** 關閉安全警告 */
process.env["ELECTRON_DISABLE_SECURITY_WARNINGS"] = "false"
/** 必要的全局錯誤捕獲 */
process.on("uncaughtException", (error) => {
  EleLog.error("[uncaughtException]", error)
  exitApp("異常捕獲", error.message || error.stack)
})
//#endregion

//#region 全局聲明 - 變量、常量
/** 當前系統平台 */
const platformType = { win32: false, darwin: false, linux: false }
platformType[process.platform] = true
/** 是否為開發環境 */
const isDevEnv = !app.isPackaged
/** app 目錄路徑
 * - dev : {project directory}/
 * - prod :
 *    1. on macOS : /Applications/{app name}.app/Contents/Resources/app?.asar/
 *    2. on Linux : {installation directory}/resources/app?.asar/
 *    3. on Windows : {installation directory}/resources/app?.asar/
 */
const appDirPath = NodePath.resolve(__dirname, "..")
/** static 目錄路徑
 * - dev : {project directory}/static
 * - prod :
 *    1. on macOS : /Applications/{app name}.app/Contents/Resources/app?.asar/static/
 *    2. on Linux : {installation directory}/resources/app?.asar/static/
 *    3. on Windows : {installation directory}/resources/app?.asar/static/
 */
const staticDirPath = NodePath.resolve(appDirPath, "static")
/** 根路徑
 * - dev : {project directory}/
 * - prod :
 *    1. on macOS : /Applications/{app name}.app/Contents/
 *    2. on Linux : {installation directory}/
 *    3. on Windows : {installation directory}/
 */
const rootDirPath = NodePath.resolve(appDirPath, "../".repeat(isDevEnv ? 0 : 2))
/** 客戶端 logo
 * https://www.electron.build/icons
 */
const logoMap = {
  win32: "logo_256x256.ico",
  darwin: "logo_256x256.icns",
  linux: "logo_256x256.png"
}
const winLogo = NodePath.join(staticDirPath, "icons", logoMap[process.platform])
/** 加載 url 路徑 */
const winURL = isDevEnv ? `http://${PKG.env.host}:${PKG.env.port}` : NodePath.join(__dirname, "./index.html")

console.log("[app   ]", appDirPath)
console.log("[root  ]", rootDirPath)
console.log("[static]", staticDirPath)
console.log("[url   ]", winURL)
console.log("")

/** 系統托盤 */
let winTray: Tray | null = null
/** 主窗口 */
let winMain: BrowserWindow | null = null
// #endregion

// #region 全局配置 - 掛載全局變量
/** 根路徑 */
global.RootPath = rootDirPath
/** 靜態資源路徑 */
global.StaticPath = staticDirPath
/** 客戶端版本號 */
global.ClientVersion = PKG.version
// #endregion

racketLaunch() // 運行

//#region 函數聲明 - 應用程序
/** 程序入口 */
function racketLaunch() {
  /** 應用單例 */
  if (!app.requestSingleInstanceLock()) {
    return exitApp("There are already instances running.")
  }
  //@todo others
  // ...
  startApp()
}
/** 退出應用 */
function exitApp(title?: string, content?: string) {
  console.log("[exitApp]", title || "", content || "")
  if (title && content) {
    const callback = () => {
      const opt: MessageBoxSyncOptions = {
        title: title,
        message: content,
        icon: winLogo,
        type: "warning",
        noLink: true,
        buttons: ["確定"],
        cancelId: -1,
        defaultId: 0
      }
      dialog.showMessageBoxSync(opt)
      app.quit()
    }
    app.isReady() ? callback() : app.whenReady().then(callback)
  } else {
    app.quit()
  }
}

/** 啟動後端 */
function startBackendApp(){
  cmd.run(`${rootDirPath}\\resources\\bin\\main.exe`, function () {
  });
}

/** 啟動應用 */
function startApp() {
  /** 初始化remote */
  remote.initialize()

  /** 禁用 Chromium 沙箱 */
  app.commandLine.appendSwitch("no-sandbox")
  /** 忽略證書相關錯誤 */
  app.commandLine.appendSwitch("ignore-certificate-errors")
  /** 禁用GPU */
  app.commandLine.appendSwitch("disable-gpu")
  app.commandLine.appendSwitch("disable-gpu-compositing")
  app.commandLine.appendSwitch("disable-gpu-rasterization")
  app.commandLine.appendSwitch("disable-gpu-sandbox")
  app.commandLine.appendSwitch("disable-software-rasterizer")
  /** 禁用動畫, 解決透明窗口打開閃爍問題 */
  app.commandLine.appendSwitch("wm-window-animations-disabled")

  /** 初始化完成 */
  app.whenReady().then(() => {
    startBackendApp()
    monitorRenderer()
    createMainWindow()
  })

  /** 運行第二個實例時 */
  app.on("second-instance", (e, argv) => {
    showMainWindow()
    const param = "--odt="
    if (argv[1] && argv[1].indexOf(param) === 0) {
      if (argv[1].substring(param.length) === "0" && winMain) {
        winMain.maximize()
        winMain.setResizable(true)
        winMain.webContents.openDevTools()
      }
    }
  })

  /** 所有的窗口都被關閉 */
  app.on("window-all-closed", () => exitApp())

  // app.on("before-quit", (event) => {})
  // app.on("quit", (event) => {})
}
//#endregion

//#region 函數聲明 - 窗口
/** 創建 主窗口 */
function createMainWindow() {
  if (winMain) return

  /** 窗口配置 */
  const options: BrowserWindowConstructorOptions = {
    icon: winLogo, // 圖標
    title: PKG.env.title, // 如果由loadURL()加載的HTML文件中含有標簽<title>，此屬性將被忽略
    width: 1200,
    height: 800,
    minWidth: 500,
    minHeight: 400,
    show: false, // 是否在創建時顯示, 默認值為 true
    frame: true, // 是否有邊框
    center: true, // 是否在屏幕居中
    opacity: 0, // 設置窗口的初始透明度
    resizable: true, // 是否允許拉伸大小
    fullscreenable: true, // 是否允許全屏，為false則插件screenfull不起作用
    autoHideMenuBar: false, // 自動隱藏菜單欄, 除非按了Alt鍵, 默認值為 false
    backgroundColor: "#fff", // 背景顏色為十六進制值
    webPreferences: {
      devTools: true, // 是否開啟 DevTools, 如果設置為 false, 則無法使用 BrowserWindow.webContents.openDevTools()。 默認值為 true
      webSecurity: false, // 當設置為 false, 將禁用同源策略
      nodeIntegration: true, // 是否啟用Node集成
      contextIsolation: false, // 是否在獨立 JavaScript 環境中運行 Electron API和指定的preload腳本，默認為 true
      backgroundThrottling: false, // 是否在頁面成為背景時限制動畫和計時器，默認值為 true
      nodeIntegrationInWorker: true // 是否在Web工作器中啟用了Node集成
    }
  }
  winMain = new BrowserWindow(options)
  winMain.removeMenu()
  isDevEnv ? winMain.loadURL(winURL) : winMain.loadFile(winURL)
  remote.enable(winMain.webContents)
  if (isDevEnv) {
    winMain.webContents.openDevTools() // 顯示調試工具
  }

  /** 初始化完成後顯示 */
  winMain.on("ready-to-show", () => {
    winMain?.setOpacity(1)
    showMainWindow() // 顯示主窗口
    createTray() // 創建系統托盤
    winMain?.setAlwaysOnTop(true)
    winMain?.once("focus", () => winMain?.setAlwaysOnTop(false))
  })

  // /** 主窗口-即將關閉 */
  // winMain.on("close", (event) => {})

  /** 主窗口-已關閉 */
  winMain.on("closed", () => {
    destroyTray()
    winMain = null
  })
}
/** 顯示 主窗口 */
function showMainWindow() {
  winMain?.center()
  winMain?.show()
  winMain?.focus()
}
/** 根據分辨率適配窗口大小 */
function adaptSizeWithScreen(params: any) {
  const devWidth = 1920 // 1920 2160
  const devHeight = 1080 // 1080 1440
  const workAreaSize = screen.getPrimaryDisplay().workAreaSize // 顯示器工作區域大小
  const zoomFactor = Math.max(workAreaSize.width / devWidth, workAreaSize.height / devHeight)
  winMain?.webContents.send("zoom_win", zoomFactor)
  // 計算實際窗口大小
  const realSize = { width: 0, height: 0 }
  realSize.width = Math.round(params.width * zoomFactor)
  realSize.height = Math.round(params.height * zoomFactor)
  // console.log(workAreaSize, realSize, zoomFactor)
  return realSize
}
/** 監聽渲染進程 */
function monitorRenderer() {
  /** 獲取應用標題 */
  ipcMain.on("query_title", () => {
    winMain && winMain.webContents.send("get_title", PKG.env.title)
  })

  /** 設置窗口大小 */
  ipcMain.on("set_win_size", (_, params: any) => {
    if (!winMain) return
    const size = adaptSizeWithScreen(params)
    winMain.setResizable(true)
    winMain.setSize(size.width, size.height)
    winMain.setMaximizable(params.maxable)
    params.center && winMain.center()
    winMain.setResizable(params.resizable)
  })
}
//#endregion

//#region 函數聲明 - 系統托盤
/** 銷毀 */
function destroyTray() {
  platformType.darwin && app.dock.hide()
  winTray?.destroy()
  winTray = null
}
/** 創建 */
function createTray() {
  if (winTray) return

  /** 右鍵/dock 菜單選項 */
  const menuList = Menu.buildFromTemplate([
    {
      label: "顯示",
      click: showMainWindow
    },
    {
      label: "控制台",
      // visible: isDevEnv,
      click: () => winMain?.webContents.openDevTools()
    },
    {
      role: "quit",
      label: "關閉應用"
    }
  ])

  if (platformType.darwin) {
    const dockIcon = NodePath.join(staticDirPath, "icons", logoMap.linux)
    app.dock.setIcon(dockIcon)
    app.dock.setMenu(menuList)
  } else {
    /** 聲明托盤對象 */
    winTray = new Tray(winLogo)
    /** 懸停提示內容 */
    winTray.setToolTip(PKG.env.title)
    /** 右鍵菜單 */
    winTray.setContextMenu(menuList)
    /** 雙擊圖標打開窗口 */
    winTray.on("double-click", showMainWindow)
  }
}
//#endregion
