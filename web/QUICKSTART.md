# 快速开始指南

## 🎯 项目已就绪!

企业级 Agent 脚手架前端系统已成功创建并运行在 **http://localhost:3000**

## ✅ 已完成的功能

### 1. 🎨 设计系统
- ✅ 深色科技感主题
- ✅ 紫色渐变 + 霓虹发光效果
- ✅ 玻璃态设计语言
- ✅ 响应式布局

### 2. 🧩 UI 组件库
- ✅ Button (6种变体)
- ✅ Card (卡片家族)
- ✅ Dialog (模态框)
- ✅ Input/Textarea
- ✅ Select (下拉选择)
- ✅ Tabs (标签页)
- ✅ ScrollArea (滚动区)
- ✅ Avatar (头像)
- ✅ Tooltip (提示)
- ✅ DropdownMenu (下拉菜单)

### 3. 📄 核心页面
- ✅ **Agent 工作台** - 创建和管理 AI Agents
- ✅ **对话界面** - 实时聊天 + Markdown 支持
- ✅ **知识库管理** - 文件上传和管理
- ✅ **系统设置** - 偏好配置

### 4. 🏗️ 布局系统
- ✅ 侧边栏导航 (可折叠)
- ✅ 顶部导航栏 (搜索 + 用户)
- ✅ 主布局容器

## 🚀 如何使用

### 查看应用

打开浏览器访问:
```
http://localhost:3000
```

### 导航功能

- **Agent 工作台** (`/`)
  - 创建新 Agent
  - 查看 Agent 列表
  - 启动/停止 Agent
  - 编辑/删除 Agent

- **对话界面** (`/chat`)
  - 选择 Agent
  - 发送消息
  - 查看 Markdown 渲染
  - 对话历史

- **知识库** (`/knowledge`)
  - 上传文件
  - 查看文件列表
  - 标签管理
  - 搜索过滤

- **系统设置** (`/settings`)
  - 外观设置
  - 个人资料
  - 通知设置

### 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

## 🎨 自定义样式

### 修改主题颜色

编辑 `src/index.css`:

```css
:root {
  --primary: 263 70% 50%;  /* 修改这里的色相值 */
  --background: 220 30% 8%;  /* 修改背景色 */
}
```

### 添加自定义特效

```css
/* 在 index.css 中添加 */
.my-custom-effect {
  @apply glass;
  box-shadow: 0 0 20px theme('colors.primary');
}
```

## 🔌 连接后端 API

### 配置 API 地址

创建 `.env` 文件:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 使用示例

```typescript
const response = await fetch(`${import.meta.env.VITE_API_URL}/api/agents`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
})
```

## 📦 添加新组件

### 使用 shadcn/ui CLI

```bash
# 添加新组件
npx shadcn@latest add [component-name]

# 示例
npx shadcn@latest add badge
npx shadcn@latest add switch
npx shadcn@latest add table
```

### 手动创建组件

在 `src/components/ui/` 创建新文件:

```typescript
// src/components/ui/my-component.tsx
import { cn } from '@/lib/utils'

interface MyComponentProps {
  className?: string
  children: React.ReactNode
}

export function MyComponent({ className, children }: MyComponentProps) {
  return (
    <div className={cn('glass rounded-lg p-4', className)}>
      {children}
    </div>
  )
}
```

## 🛠️ 故障排除

### 端口被占用

修改 `vite.config.ts`:

```typescript
server: {
  port: 3001,  // 改为其他端口
}
```

### 组件未找到

确保路径别名 `@` 正确配置:

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 样式未生效

1. 确保 `tailwind.config.js` 内容路径正确
2. 检查 `index.css` 是否导入
3. 清除缓存重启

```bash
rm -rf node_modules/.vite
npm run dev
```

## 📚 下一步

### 推荐的学习路径

1. **熟悉现有组件** - 浏览 `src/components/ui/` 目录
2. **理解路由** - 查看 `src/App.tsx` 的路由配置
3. **自定义页面** - 修改现有页面或创建新页面
4. **添加状态管理** - 集成 Zustand 或 React Query
5. **连接后端** - 实现真实的 API 调用
6. **添加测试** - 使用 Vitest 和 Testing Library

### 扩展功能建议

- [ ] 添加 WebSocket 实时通信
- [ ] 实现拖拽式工作流编辑器
- [ ] 添加数据可视化图表
- [ ] 集成 Monaco 代码编辑器
- [ ] 添加文件预览功能
- [ ] 实现多语言支持

## 🎓 参考资源

- [Vite 文档](https://vitejs.dev/)
- [React 文档](https://react.dev/)
- [shadcn/ui 文档](https://ui.shadcn.com/)
- [Tailwind CSS 文档](https://tailwindcss.com/)
- [Radix UI 文档](https://www.radix-ui.com/)

## 💬 获取帮助

遇到问题?
1. 查看项目 `ARCHITECTURE.md` 架构文档
2. 阅读 `README.md` 完整说明
3. 检查组件源码和注释
4. 查阅技术文档

---

**享受开发! 🚀**
