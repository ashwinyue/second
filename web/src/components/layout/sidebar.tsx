import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Bot,
  MessageSquare,
  Database,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  History,
  Trash2,
  Plus,
  Edit2,
  Check,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Input } from '@/components/ui/input'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogTitle,
} from '@/components/ui/dialog'

const navigation = [
  { name: 'Agent 工作台', href: '/', icon: Bot },
  { name: '对话界面', href: '/chat', icon: MessageSquare },
  { name: '知识库管理', href: '/knowledge', icon: Database },
  { name: '系统设置', href: '/settings', icon: Settings },
]

interface Session {
  id: string
  title?: string
  created_at: string
  updated_at: string
  messages: Array<{ id: string; role: string; content: string }>
  tasks: Array<{ id: string; topic: string; status: string }>
}

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [sessions, setSessions] = useState<Session[]>([])
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; sessionId: string }>({
    open: false,
    sessionId: '',
  })
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const location = useLocation()
  const navigate = useNavigate()

  // 加载会话列表
  useEffect(() => {
    if (!collapsed) {
      loadSessions()
    }
  }, [collapsed])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/v1/sessions?limit=20')
      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions || [])
      }
    } catch (error) {
      console.error('加载会话列表失败:', error)
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/v1/sessions/${sessionId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        setSessions(sessions.filter(s => s.id !== sessionId))
        setDeleteDialog({ open: false, sessionId: '' })
      }
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }

  const handleStartEdit = (session: Session) => {
    setEditingId(session.id)
    setEditTitle(getSessionTitle(session))
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleSaveEdit = async (sessionId: string) => {
    if (!editTitle.trim()) return

    try {
      const response = await fetch(`/api/v1/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle.trim() }),
      })

      if (response.ok) {
        // 更新本地状态
        setSessions(sessions.map(s =>
          s.id === sessionId ? { ...s, title: editTitle.trim() } : s
        ))
        setEditingId(null)
        setEditTitle('')
      }
    } catch (error) {
      console.error('更新会话标题失败:', error)
    }
  }

  const getSessionTitle = (session: Session) => {
    // 如果有自定义标题，优先使用
    if (session.title) {
      return session.title
    }
    // 从第一条用户消息中提取标题
    const firstUserMessage = session.messages.find(m => m.role === 'user')
    if (firstUserMessage) {
      const content = firstUserMessage.content
      return content.length > 20 ? content.substring(0, 20) + '...' : content
    }
    // 如果有任务，使用任务主题
    if (session.tasks.length > 0) {
      const topic = session.tasks[0].topic
      return topic.length > 20 ? topic.substring(0, 20) + '...' : topic
    }
    // 默认标题
    const date = new Date(session.created_at)
    return `会话 ${date.toLocaleDateString()}`
  }

  return (
    <>
      {/* 移动端遮罩 */}
      {!collapsed && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setCollapsed(true)}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-screen glass border-r border-primary/20 transition-all duration-300 flex flex-col',
          collapsed ? 'w-20' : 'w-64'
        )}
      >
        {/* Logo 区域 */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-border/50 shrink-0">
          {!collapsed && (
            <Link to="/" className="flex items-center gap-2 group">
              <div className="relative">
                <Sparkles className="h-6 w-6 text-primary animate-pulse-glow" />
                <div className="absolute inset-0 blur-xl bg-primary/30 group-hover:bg-primary/50 transition-all duration-300" />
              </div>
              <span className="text-lg font-semibold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">
                Next Show
              </span>
            </Link>
          )}
          {collapsed && (
            <div className="mx-auto">
              <Sparkles className="h-6 w-6 text-primary animate-pulse-glow" />
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* 导航菜单 */}
        <nav className="px-3 py-4 space-y-1 shrink-0">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/30'
                    : 'text-muted-foreground hover:bg-accent/10 hover:text-primary'
                )}
              >
                <item.icon className={cn('h-5 w-5 flex-shrink-0', !collapsed && 'group-hover:scale-110 transition-transform')} />
                {!collapsed && (
                  <span className="font-medium">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* 会话历史列表 */}
        {!collapsed && (
          <div className="flex-1 flex flex-col min-h-0 border-t border-border/50">
            <div className="px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <History className="h-4 w-4" />
                <span>历史会话</span>
              </div>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => navigate('/chat')}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>新建会话</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <ScrollArea className="flex-1 px-2">
              <div className="space-y-1">
                {sessions.length === 0 ? (
                  <div className="px-3 py-4 text-center text-sm text-muted-foreground">
                    暂无历史会话
                  </div>
                ) : (
                  sessions.map((session) => (
                    <div
                      key={session.id}
                      className="group flex items-center gap-1 px-2 py-1.5 rounded-md hover:bg-muted/50 transition-colors"
                    >
                      {editingId === session.id ? (
                        // 编辑模式
                        <div className="flex-1 flex items-center gap-1">
                          <Input
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleSaveEdit(session.id)
                              if (e.key === 'Escape') handleCancelEdit()
                            }}
                            className="h-7 text-sm"
                            autoFocus
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => handleSaveEdit(session.id)}
                          >
                            <Check className="h-3 w-3 text-green-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={handleCancelEdit}
                          >
                            <X className="h-3 w-3 text-destructive" />
                          </Button>
                        </div>
                      ) : (
                        // 显示模式
                        <>
                          <button
                            onClick={() => navigate(`/chat?session=${session.id}`)}
                            className="flex-1 text-left text-sm truncate text-muted-foreground hover:text-foreground"
                          >
                            {getSessionTitle(session)}
                          </button>
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => handleStartEdit(session)}
                                >
                                  <Edit2 className="h-3 w-3 text-muted-foreground" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>重命名</TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => setDeleteDialog({ open: true, sessionId: session.id })}
                                >
                                  <Trash2 className="h-3 w-3 text-destructive" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>删除会话</TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* 底部信息 - 仅在折叠时显示 */}
        {collapsed && (
          <div className="p-3 border-t border-border/50">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="w-full" onClick={() => navigate('/chat')}>
                    <Plus className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>新建会话</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        )}
      </aside>

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, sessionId: '' })}>
        <DialogContent>
          <DialogTitle>确认删除</DialogTitle>
          <DialogDescription>
            确定要删除这个会话吗？删除后将无法恢复。
          </DialogDescription>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog({ open: false, sessionId: '' })}>
              取消
            </Button>
            <Button variant="destructive" onClick={() => handleDeleteSession(deleteDialog.sessionId)}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
