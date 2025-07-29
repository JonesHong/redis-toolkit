// VuePress 插件配置
module.exports = [
  // 返回頂部按鈕
  '@vuepress/back-to-top',
  
  // 圖片縮放
  '@vuepress/medium-zoom',
  
  // 程式碼複製按鈕
  ['vuepress-plugin-code-copy', {
    align: 'top',
    color: '#dc382d',
    backgroundTransition: true,
    backgroundColor: '#0075b8',
    successText: '已複製！',
    successTextColor: '#fff',
    // 添加錯誤處理
    onError: (err) => {
      console.warn('Code copy error:', err);
    }
  }],
  
  // 搜尋功能
  ['@vuepress/search', {
    searchMaxSuggestions: 10,
    searchHotkeys: ['s', '/'],
    getExtraFields: (page) => page.frontmatter.tags || [],
    locales: {
      '/': {
        placeholder: '搜尋文檔'
      },
      '/en/': {
        placeholder: 'Search docs'
      }
    },
    // 根據當前語言過濾搜尋結果
    test: (page, searchValue, locale) => {
      const currentLocale = locale || '/'
      if (currentLocale === '/') {
        return !page.path.startsWith('/en/')
      } else {
        return page.path.startsWith(currentLocale)
      }
    }
  }],
  
  // 禁用可能導致問題的功能
  ['@vuepress/plugin-nprogress', false]
]