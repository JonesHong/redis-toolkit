// 全域錯誤處理
export default ({
  Vue, // VuePress 正在使用的 Vue 建構函式
  options, // 附加到根實例的一些選項
  router, // 當前應用程式的路由實例
  siteData // 網站數據
}) => {
  // 處理程式碼標籤相關錯誤
  if (typeof window !== 'undefined') {
    // 覆寫可能出錯的方法
    Vue.config.errorHandler = (err, vm, info) => {
      // 忽略程式碼標籤相關錯誤
      if (err.message && err.message.includes("reading 'elm'")) {
        console.warn('忽略程式碼標籤錯誤:', err);
        return;
      }
      // 其他錯誤正常處理
      console.error(err);
    };
  }
}