# Agent 脚手架前端架构说明

## 技术栈

### 核心框架
- **Vite 6** - 极速的构建工具
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **React Router v7** - 路由管理

### UI 组件库
- **Radix UI** - 无样式的可访问组件原语
- **shadcn/ui** - 高质量的 React 组件集合
- **Tailwind CSS** - 原子化 CSS 框架
- **Lucide React** - 图标库

### 状态管理
- **Zustand** - 轻量级状态管理
- **React Query** - 服务端状态管理
- **React Hook Form** - 表单状态管理

### 其他
- **react-markdown** - Markdown 渲染
- **class-variance-authority** - 组件变体管理
- **tailwind-merge** - Tailwind 类名合并
- **clsx** - 条件类名工具

## 项目结构详解

```
src/
├── components/
│   ├── layout/              # 布局组件
│   │   ├── sidebar.tsx      # 侧边栏 - 导航菜单
│   │   ├── header.tsx       # 顶部栏 - 搜索和用户操作
│   │   └── main-layout.tsx  # 主布局 - 组合侧边栏和主内容区
│   └── ui/                  # UI 组件库 (shadcn/ui)
│       ├── button.tsx       # 按钮组件
│       ├── card.tsx         # 卡片组件
│       ├── dialog.tsx       # 对话框组件
│       ├── input.tsx        # 输入框组件
│       ├── textarea.tsx     # 文本域组件
│       ├── select.tsx       # 下拉选择组件
│       ├── tabs.tsx         # 标签页组件
│       ├── scroll-area.tsx  # 滚动区域组件
│       ├── avatar.tsx       # 头像组件
│       ├── tooltip.tsx      # 提示框组件
│       └── dropdown-menu.tsx # 下拉菜单组件
├── pages/                   # 页面组件
│   ├── agent-workspace.tsx  # Agent 工作台页面
│   ├── chat-interface.tsx   # 对话界面页面
│   ├── knowledge-base.tsx   # 知识库管理页面
│   └── settings.tsx         # 系统设置页面
├── lib/
│   └── utils.ts             # 工具函数 (cn 类名合并)
├── App.tsx                  # 应用根组件 - 路由配置
├── main.tsx                 # React 入口 - 挂载应用
└── index.css                # 全局样式和主题变量
```

## 设计系统

### 颜色系统

使用 HSL 格式的 CSS 变量定义颜色系统:

```css
:root {
  /* 主色调 - 紫蓝色 */
  --primary: 263 70% 50%;
  --primary-foreground: 210 40% 98%;

  /* 背景色 - 深色 */
  --background: 220 30% 8%;
  --foreground: 210 40% 98%;

  /* 卡片 */
  --card: 220 30% 10%;
  --card-foreground: 210 40% 98%;

  /* 边框和输入 */
  --border: 217 30% 18%;
  --input: 217 30% 18%;

  /* 次要颜色 */
  --secondary: 217 30% 20%;
  --secondary-foreground: 210 40% 98%;

  /* 静音色 */
  --muted: 217 30% 15%;
  --muted-foreground: 215 20% 65%;

  /* 强调色 */
  --accent: 263 70% 50%;
  --accent-foreground: 210 40% 98%;

  /* 圆角 */
  --radius: 0.75rem;
}
```

### 自定义特效类

```css
/* 玻璃态效果 */
.glass {
  @apply bg-card/80 backdrop-blur-xl border border-border/50;
}

/* 霓虹边框 */
.neon-border {
  box-shadow: 0 0 5px theme('colors.primary'),
              0 0 20px theme('colors.primary');
}

/* 霓虹文字 */
.neon-text {
  text-shadow: 0 0 10px theme('colors.primary'),
               0 0 20px theme('colors.primary'),
               0 0 40px theme('colors.primary');
}

/* 渐变背景 */
.gradient-bg {
  background: linear-gradient(135deg,
    hsl(220, 30%, 8%) 0%,
    hsl(263, 50%, 15%) 50%,
    hsl(220, 30%, 8%) 100%
  );
}

/* 网格背景 */
.grid-bg {
  background-image:
    linear-gradient(to right, hsl(217, 30%, 18%) 1px, transparent 1px),
    linear-gradient(to bottom, hsl(217, 30%, 18%) 1px, transparent 1px);
  background-size: 50px 50px;
}
```

### 组件变体

```css
/* 发光按钮 */
.btn-glow {
  @apply bg-primary text-primary-foreground;
  @apply shadow-lg shadow-primary/30;
  @apply hover:shadow-primary/50 hover:scale-105;
  @apply neon-border;
}

/* 科技感卡片 */
.card-tech {
  @apply glass rounded-xl p-6;
  @apply hover:shadow-2xl hover:shadow-primary/20;
  @apply transition-all duration-300 hover:-translate-y-1;
  @apply border border-primary/20;
}

/* 科技感输入框 */
.input-tech {
  @apply bg-muted/50 border-border rounded-lg px-4 py-3;
  @apply focus:outline-none focus:ring-2 focus:ring-primary/50;
  @apply focus:border-primary transition-all duration-200;
}
```

## 路由结构

```typescript
<BrowserRouter>
  <Routes>
    <Route path="/" element={<MainLayout />}>
      <Route index element={<AgentWorkspace />} />
      <Route path="chat" element={<ChatInterface />} />
      <Route path="knowledge" element={<KnowledgeBase />} />
      <Route path="settings" element={<Settings />} />
    </Route>
  </Routes>
</BrowserRouter>
```

## 数据流

### 侧边栏状态
- 使用 React 本地状态管理折叠状态
- 使用 `useLocation` 获取当前路由高亮

### 页面状态
- 各页面使用 `useState` 管理本地状态
- 模拟数据存储在组件内部

### 表单状态
- 使用受控组件模式
- 表单值存储在组件 state 中

## 性能优化

### 代码分割
- React Router 自动进行路由级代码分割
- 动态导入大型组件

### 懒加载
```typescript
const LazyComponent = lazy(() => import('./HeavyComponent'))
```

### 虚拟滚动
- 使用 `ScrollArea` 组件处理长列表

### 图片优化
- 使用合适的图片格式
- 延迟加载非关键图片

## 可访问性

### ARIA 属性
- 所有交互组件包含适当的 ARIA 标签
- 键盘导航支持

### 焦点管理
- 对话框自动聚焦
- 焦点陷阱在模态组件中

### 颜色对比
- 遵循 WCAG AA 标准
- 深色主题优化的对比度

## 未来扩展

### 计划中的功能
- [ ] WebSocket 实时通信
- [ ] 状态持久化 (localStorage)
- [ ] 主题切换 (浅色/深色)
- [ ] 国际化支持 (i18n)
- [ ] 单元测试
- [ ] E2E 测试

### 可优化的部分
- [ ] 添加 React Query 缓存
- [ ] 实现 Zustand 全局状态
- [ ] 添加错误边界
- [ ] 性能监控
- [ ] SEO 优化
