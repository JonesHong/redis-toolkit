module.exports = {
  // 多語言配置
  locales: {
    '/': {
      lang: 'zh-TW',
      title: 'Redis Toolkit',
      description: '強大的 Redis 工具包，支援自動序列化與媒體處理'
    },
    '/en/': {
      lang: 'en-US',
      title: 'Redis Toolkit',
      description: 'Powerful Redis toolkit with automatic serialization and media processing'
    }
  },
  
  base: '/redis-toolkit/', // 確保與您的 GitHub 倉庫名稱一致
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#dc382d' }],
    ['meta', { name: 'mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }],
    ['link', { rel: 'stylesheet', href: '/override.css' }],
    ['style', {}, `
      /* 緊急修復導航欄紅色背景 */
      .nav-item, 
      .navbar .nav-item,
      .navbar .links .nav-item,
      div.nav-item {
        background: transparent !important;
        background-color: transparent !important;
      }
      .nav-item > a {
        background: transparent !important;
        color: #2c3e50 !important;
      }
    `]
  ],
  
  themeConfig: {
    logo: '/logo.png',
    repo: 'JonesHong/redis-toolkit',
    editLinks: true,
    smoothScroll: true,
    
    // 多語言主題配置
    locales: {
      '/': {
        // 語言選擇器
        selectText: '選擇語言',
        label: '繁體中文',
        ariaLabel: '選擇語言',
        editLinkText: '在 GitHub 上編輯此頁',
        lastUpdated: '最後更新',
        
        // 導航欄
        nav: [
          { text: '指南', link: '/guide/' },
          { text: '進階', link: '/advanced/' },
          { text: 'API', link: '/api/' },
          { text: '範例', link: '/examples/' },
          {
            text: '了解更多',
            items: [
              { text: '更新日誌', link: 'https://github.com/JonesHong/redis-toolkit/blob/main/CHANGELOG.md' },
              { text: 'PyPI', link: 'https://pypi.org/project/redis-toolkit/' },
              { text: '問題回報', link: 'https://github.com/JonesHong/redis-toolkit/issues' }
            ]
          }
        ],
        
        // 側邊欄
        sidebar: {
          '/guide/': [
            {
              title: '開始使用',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                '',
                'getting-started',
                'installation',
                'basic-usage'
              ]
            },
            {
              title: '核心功能',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                'serialization',
                'pubsub',
                'configuration'
              ]
            }
          ],
          
          '/advanced/': [
            {
              title: '進階功能',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                '',
                'media-processing',
                'batch-operations'
              ]
            }
          ],
          
          '/api/': [
            {
              title: 'API 參考',
              collapsable: false,
              sidebarDepth: 3,
              children: [
                '',
                'core',
                'converters',
                'options',
                'utilities'
              ]
            }
          ],
          
          '/examples/': [
            {
              title: '範例程式',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                ''
              ]
            }
          ]
        }
      },
      
      '/en/': {
        // Language selector
        selectText: 'Languages',
        label: 'English',
        ariaLabel: 'Select language',
        editLinkText: 'Edit this page on GitHub',
        lastUpdated: 'Last Updated',
        
        // Navigation
        nav: [
          { text: 'Guide', link: '/en/guide/' },
          { text: 'Advanced', link: '/en/advanced/' },
          { text: 'API', link: '/en/api/' },
          { text: 'Examples', link: '/en/examples/' },
          {
            text: 'Learn More',
            items: [
              { text: 'Changelog', link: 'https://github.com/JonesHong/redis-toolkit/blob/main/CHANGELOG.md' },
              { text: 'PyPI', link: 'https://pypi.org/project/redis-toolkit/' },
              { text: 'Issues', link: 'https://github.com/JonesHong/redis-toolkit/issues' }
            ]
          }
        ],
        
        // Sidebar
        sidebar: {
          '/en/guide/': [
            {
              title: 'Getting Started',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                '',
                'getting-started',
                'installation',
                'basic-usage'
              ]
            },
            {
              title: 'Core Features',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                'serialization',
                'pubsub',
                'configuration'
              ]
            }
          ],
          
          '/en/advanced/': [
            {
              title: 'Advanced Features',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                '',
                'media-processing',
                'batch-operations'
              ]
            }
          ],
          
          '/en/api/': [
            {
              title: 'API Reference',
              collapsable: false,
              sidebarDepth: 3,
              children: [
                '',
                'core',
                'converters',
                'options',
                'utilities'
              ]
            }
          ],
          
          '/en/examples/': [
            {
              title: 'Examples',
              collapsable: false,
              sidebarDepth: 2,
              children: [
                ''
              ]
            }
          ]
        }
      }
    }
  },
  
  plugins: require('./config/plugins.js'),
  
  markdown: {
    lineNumbers: true
  }
}