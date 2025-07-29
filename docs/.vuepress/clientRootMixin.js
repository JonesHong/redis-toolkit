// 客戶端混入
export default {
  mounted() {
    // 修復程式碼標籤相關問題
    if (typeof window !== 'undefined') {
      // 延遲執行以避免 DOM 未準備好的問題
      this.$nextTick(() => {
        // 檢查是否有程式碼標籤元素
        const codeTabs = document.querySelectorAll('.code-tabs');
        if (codeTabs.length > 0) {
          console.log('Found code tabs, applying fixes...');
        }
      });
    }
  }
}