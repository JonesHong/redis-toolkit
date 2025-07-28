import { defaultTheme } from 'vuepress'
import { searchPlugin } from '@vuepress/plugin-search'
import { backToTopPlugin } from '@vuepress/plugin-back-to-top'

export default {
  lang: 'zh-TW',
  title: 'Redis Toolkit',
  description: '簡化 Redis 操作的 Python 工具包',
  
  base: '/redis-toolkit/',
  
  head: [
    ['link', { rel: 'icon', href: '/images/logo.png' }],
    ['meta', { name: 'theme-color', content: '#dc382d' }],
  ],

  theme: defaultTheme({
    logo: '/images/logo.png',
    repo: 'https://github.com/yourusername/redis-toolkit',
    docsDir: 'docs',
    editLink: true,
    editLinkText: '編輯此頁',
    lastUpdated: true,
    lastUpdatedText: '最後更新',
    contributors: true,
    contributorsText: '貢獻者',
    
    navbar: [
      { text: '首頁', link: '/' },
      {
        text: '教程',
        children: [
          { text: '快速開始', link: '/tutorials/getting-started' },
          { text: '第一個應用', link: '/tutorials/first-redis-app' },
        ],
      },
      {
        text: '指南',
        children: [
          { text: '批次操作', link: '/how-to/batch-operations' },
          { text: '媒體處理', link: '/how-to/media-processing' },
          { text: '性能調優', link: '/how-to/performance-tuning' },
        ],
      },
      {
        text: 'API 參考',
        children: [
          { text: '核心 API', link: '/reference/api/core' },
          { text: '轉換器', link: '/reference/api/converters' },
          { text: '配置', link: '/reference/api/configuration' },
        ],
      },
    ],
    
    sidebar: {
      '/tutorials/': [
        {
          text: '教程',
          collapsible: true,
          children: [
            '/tutorials/getting-started',
            '/tutorials/first-redis-app',
          ],
        },
      ],
      '/how-to/': [
        {
          text: '操作指南',
          collapsible: true,
          children: [
            '/how-to/batch-operations',
            '/how-to/media-processing',
            '/how-to/performance-tuning',
          ],
        },
      ],
      '/reference/': [
        {
          text: 'API 參考',
          collapsible: true,
          children: [
            '/reference/api/core',
            '/reference/api/converters',
            '/reference/api/configuration',
          ],
        },
        {
          text: 'CLI 參考',
          collapsible: true,
          children: [
            '/reference/cli',
          ],
        },
      ],
      '/explanation/': [
        {
          text: '深入理解',
          collapsible: true,
          children: [
            '/explanation/architecture',
            '/explanation/design-decisions',
            '/explanation/serialization',
          ],
        },
      ],
    },
  }),

  plugins: [
    searchPlugin({
      locales: {
        '/': {
          placeholder: '搜尋',
        },
      },
    }),
    backToTopPlugin(),
  ],
}