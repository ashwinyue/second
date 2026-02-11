/**
 * 视频生成对话界面
 * 支持 SSE 流式进度、图片/视频展示
 * 支持历史会话加载
 */
import { useState, useRef, useEffect, useCallback } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { Send, RefreshCw, X, CheckCircle2, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Bot, User } from "lucide-react"
import { generateVideoStream, getSession, createSession, addMessage } from "@/lib/api"
import type {
  SSEProgressEvent,
  SSEWritingDoneEvent,
  SSESceneEvent,
  SSEDoneEvent,
  SSEErrorEvent,
  SSEInitEvent,
  StepType,
  SceneInfo,
  SessionMessage,
} from "@/lib/types"
import { STEP_CONFIG } from "@/lib/types"
import { cn } from "@/lib/utils"

// ============================================================================
// 类型定义
// ============================================================================

interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  taskId?: string
  isStreaming?: boolean
  progress?: number
  step?: StepType
  scripts?: ScriptScene[]  // 生成的文案
  scenes?: SceneInfo[]
  finalVideoUrl?: string
  error?: string
  abortController?: AbortController
}

interface ScriptScene {
  id: number
  text: string
  type: string
  emotion: string
}

// ============================================================================
// 组件
// ============================================================================

const STYLE_PRESETS = [
  { id: "minimal", name: "极简金句", description: "小而精悍、直击人心" },
  { id: "camus", name: "加缪荒诞", description: "深度拷问、诗意克制" },
  { id: "healing", name: "温暖治愈", description: "亲切陪伴、温柔鼓励" },
  { id: "knowledge", name: "硬核科普", description: "权威数据、逻辑清晰" },
  { id: "humor", name: "幽默搞笑", description: "反转套路、轻松调侃" },
  { id: "growth", name: "成长觉醒", description: "认知升级、自我突破" },
]

export function ChatInterface() {
  // URL 参数和导航
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const sessionId = searchParams.get("session")

  // 消息状态
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "# 欢迎使用 AI 视频生成器\n\n请输入一个主题，我将为你生成一段精彩的视频。\n\n**可选风格：**\n- 极简金句：短小精悍、直击人心\n- 加缪荒诞：深度拷问、诗意克制\n- 温暖治愈：亲切陪伴、温柔鼓励\n- 硬核科普：权威数据、逻辑清晰\n- 幽默搞笑：反转套路、轻松调侃\n- 成长觉醒：认知升级、行动导向\n\n**示例主题：**\n- 生命的意义是什么\n- 如何应对焦虑\n- 什么是量子纠缠",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")

  // UI 状态
  const [selectedStyle, setSelectedStyle] = useState("minimal")
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId)
  const [isLoadingSession, setIsLoadingSession] = useState(false)

  // 用于跟踪当前进度消息的状态
  const progressMessageRef = useRef<ChatMessage | null>(null)

  // ============================================================================
  // 历史会话加载
  // ============================================================================

  /**
   * 将数据库消息转换为 ChatMessage
   */
  const convertDbMessageToChatMessage = useCallback((dbMessage: SessionMessage): ChatMessage => {
    const extraData = dbMessage.extra_data as Record<string, unknown> | undefined

    return {
      id: dbMessage.id,
      role: dbMessage.role,
      content: dbMessage.content,
      timestamp: new Date(dbMessage.created_at),
      // 从 extra_data 中恢复视频生成相关数据
      taskId: extraData?.task_id as string | undefined,
      isStreaming: false,
      progress: extraData?.progress as number | undefined,
      step: extraData?.step as StepType | undefined,
      scripts: extraData?.scripts as ScriptScene[] | undefined,
      scenes: extraData?.scenes as SceneInfo[] | undefined,
      finalVideoUrl: extraData?.final_video_url as string | undefined,
      error: extraData?.error as string | undefined,
    }
  }, [])

  /**
   * 加载历史会话
   */
  useEffect(() => {
    const loadHistorySession = async () => {
      if (!sessionId) return

      setIsLoadingSession(true)
      try {
        const session = await getSession(sessionId)

        // 转换消息
        const chatMessages = session.messages.map(convertDbMessageToChatMessage)

        // 如果没有消息，添加欢迎消息
        if (chatMessages.length === 0) {
          chatMessages.push({
            id: "welcome",
            role: "assistant",
            content: "# 历史会话\n\n这是一个空的历史会话。",
            timestamp: new Date(session.created_at),
          })
        }

        setMessages(chatMessages)
        setCurrentSessionId(sessionId)
      } catch (error) {
        console.error("加载历史会话失败:", error)
        setMessages([
          {
            id: "error",
            role: "assistant",
            content: `# 加载失败\n\n无法加载历史会话：${error instanceof Error ? error.message : "未知错误"}`,
            timestamp: new Date(),
          },
        ])
      } finally {
        setIsLoadingSession(false)
      }
    }

    loadHistorySession()
  }, [sessionId, convertDbMessageToChatMessage])

  /**
   * 创建新会话
   */
  const createNewSessionIfNeeded = useCallback(async (): Promise<string | null> => {
    // 如果已经有会话 ID，直接返回
    if (currentSessionId) {
      return currentSessionId
    }

    try {
      const session = await createSession()
      setCurrentSessionId(session.id)
      return session.id
    } catch (error) {
      console.error("创建会话失败:", error)
      return null
    }
  }, [currentSessionId])

  // ============================================================================
  // 消息处理
  // ============================================================================

  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, ...updates } : msg))
    )
  }, [])

  const handleMessageProgress = useCallback((event: SSEProgressEvent, messageId: string) => {
    updateMessage(messageId, {
      progress: event.progress,
      step: event.step,
    })
  }, [updateMessage])

  const handleMessageScene = useCallback((event: SSESceneEvent, messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.id === messageId) {
          const scenes = msg.scenes || []
          const sceneId = event.scene_id

          // 查找是否已存在该场景
          const existingIndex = scenes.findIndex((s) => s.id === sceneId)

          let updatedScenes: SceneInfo[]
          if (existingIndex >= 0) {
            // 更新现有场景
            updatedScenes = [...scenes]
            if (event.scene_type === "image") {
              updatedScenes[existingIndex] = {
                ...updatedScenes[existingIndex],
                imageUrl: event.url,
              }
            } else if (event.scene_type === "video") {
              updatedScenes[existingIndex] = {
                ...updatedScenes[existingIndex],
                videoUrl: event.url,
              }
            }
            const updated = { ...msg, scenes: updatedScenes }
            // 更新 ref
            if (progressMessageRef.current?.id === messageId) {
              progressMessageRef.current = updated
            }
            return updated
          } else {
            // 添加新场景
            const newScene: SceneInfo = {
              id: event.scene_id,
              text: event.text || "",
              type: "",
              duration: 0,
              emotion: event.emotion || "",
              imageUrl: event.scene_type === "image" ? event.url : undefined,
              videoUrl: event.scene_type === "video" ? event.url : undefined,
            }
            const updated = { ...msg, scenes: [...scenes, newScene] }
            // 更新 ref
            if (progressMessageRef.current?.id === messageId) {
              progressMessageRef.current = updated
            }
            return updated
          }
        }
        return msg
      })
    )
  }, [])

  const handleMessageWritingDone = useCallback((event: SSEWritingDoneEvent, messageId: string) => {
    const scripts = event.scenes.map((s) => ({
      id: s.id,
      text: s.text,
      type: s.type,
      emotion: s.emotion,
    }))
    updateMessage(messageId, { scripts })
    // 更新 ref
    if (progressMessageRef.current?.id === messageId) {
      progressMessageRef.current = {
        ...progressMessageRef.current,
        scripts,
      }
    }
  }, [updateMessage])

  const handleMessageDone = useCallback((event: SSEDoneEvent, messageId: string) => {
    updateMessage(messageId, {
      isStreaming: false,
      progress: 1,
      step: "done",
      finalVideoUrl: event.final_video_url,
    })
    // 更新 ref
    if (progressMessageRef.current?.id === messageId) {
      progressMessageRef.current = {
        ...progressMessageRef.current,
        isStreaming: false,
        progress: 1,
        step: "done",
        finalVideoUrl: event.final_video_url,
      }
    }
  }, [updateMessage])

  const handleMessageError = useCallback((event: SSEErrorEvent, messageId: string) => {
    updateMessage(messageId, {
      isStreaming: false,
      error: event.message,
    })
  }, [updateMessage])

  // ============================================================================
  // 核心功能
  // ============================================================================

  const handleSend = useCallback(async () => {
    if (!input.trim()) return

    const topic = input.trim()
    setInput("")

    // 确保有会话 ID
    const activeSessionId = await createNewSessionIfNeeded()

    // 添加用户消息
    const userMessageId = Date.now().toString()
    const userMessage: ChatMessage = {
      id: userMessageId,
      role: "user",
      content: topic,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    // 保存用户消息到数据库
    if (activeSessionId) {
      addMessage(activeSessionId, "user", topic).catch((error) => {
        console.error("保存用户消息失败:", error)
      })
    }

    // 创建系统消息显示进度
    const progressMessageId = (Date.now() + 1).toString()
    const progressMessage: ChatMessage = {
      id: progressMessageId,
      role: "system",
      content: `正在生成关于"${topic}"的视频...`,
      timestamp: new Date(),
      taskId: "",
      isStreaming: true,
      progress: 0,
      step: "init",
      scripts: [],
      scenes: [],
    }
    // 保存到 ref
    progressMessageRef.current = progressMessage

    setMessages((prev) => [...prev, progressMessage])

    // 开始 SSE 流式请求
    const abortController = generateVideoStream(
      {
        topic,
        style: selectedStyle as any,
      },
      {
        onInit: (event: SSEInitEvent) => {
          updateMessage(progressMessageId, { taskId: event.task_id })
        },
        onProgress: (event: SSEProgressEvent) => {
          handleMessageProgress(event, progressMessageId)
        },
        onWritingDone: (event: SSEWritingDoneEvent) => {
          handleMessageWritingDone(event, progressMessageId)
        },
        onScene: (event: SSESceneEvent) => {
          handleMessageScene(event, progressMessageId)
        },
        onDone: (event: SSEDoneEvent) => {
          handleMessageDone(event, progressMessageId)

          // 保存完成后的系统消息到数据库（包含完整状态）
          if (activeSessionId && progressMessageRef.current) {
            const currentMsg = progressMessageRef.current
            addMessage(
              activeSessionId,
              "system",
              `视频生成完成：${topic}`,
              {
                task_id: event.task_id,
                final_video_url: event.final_video_url,
                progress: 1,
                step: "done",
                scripts: currentMsg.scripts,
                scenes: currentMsg.scenes,
              }
            ).catch((error) => {
              console.error("保存系统消息失败:", error)
            })
            // 清除 ref
            progressMessageRef.current = null
          }
        },
        onError: (event: SSEErrorEvent) => {
          handleMessageError(event, progressMessageId)

          // 保存错误消息到数据库
          if (activeSessionId) {
            addMessage(
              activeSessionId,
              "system",
              `生成失败：${event.message}`,
              {
                error: event.message,
              }
            ).catch((error) => {
              console.error("保存错误消息失败:", error)
            })
          }
        },
      }
    )

    // 保存 abortController 用于取消
    updateMessage(progressMessageId, { abortController })
  }, [
    input,
    selectedStyle,
    updateMessage,
    handleMessageProgress,
    handleMessageWritingDone,
    handleMessageScene,
    handleMessageDone,
    handleMessageError,
    createNewSessionIfNeeded,
  ])

  const handleCancelTask = useCallback((messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.id === messageId && msg.abortController) {
          msg.abortController.abort()
          return {
            ...msg,
            isStreaming: false,
            error: "用户取消",
          }
        }
        return msg
      })
    )
  }, [])

  // ============================================================================
  // 工具函数
  // ============================================================================

  function formatProgress(progress: number): string {
    return `${Math.round(progress * 100)}%`
  }

  function getStepIcon(step: StepType): string {
    return STEP_CONFIG[step]?.icon || "⏳"
  }

  function getStepLabel(step: StepType): string {
    return STEP_CONFIG[step]?.label || "处理中"
  }

  // ============================================================================
  // 自动滚动
  // ============================================================================

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // 监听滚动事件，检测用户是否手动滚动
  useEffect(() => {
    const scrollArea = scrollAreaRef.current?.querySelector('[data-radix-scroll-area-viewport]')
    if (!scrollArea) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollArea
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
      // 如果用户滚动到接近底部，重新启用自动滚动
      if (isAtBottom) {
        setIsAutoScrollEnabled(true)
      } else {
        // 用户向上滚动查看历史消息，禁用自动滚动
        setIsAutoScrollEnabled(false)
      }
    }

    scrollArea.addEventListener('scroll', handleScroll)
    return () => scrollArea.removeEventListener('scroll', handleScroll)
  }, [])

  // 自动滚动到最新消息
  useEffect(() => {
    if (messagesEndRef.current && isAutoScrollEnabled) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end" })
    }
  }, [messages, isAutoScrollEnabled])

  // ============================================================================
  // 键盘事件
  // ============================================================================

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // ============================================================================
  // 渲染
  // ============================================================================

  // 获取当前正在进行的任务
  const activeTask = messages.find(m => m.isStreaming)

  // 加载历史会话时的显示
  if (isLoadingSession) {
    return (
      <div className="h-[calc(100vh-120px)] flex items-center justify-center">
        <Card className="p-8 flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">正在加载历史会话...</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-120px)] flex gap-4">
      {/* 主对话区域 */}
      <Card className="flex-1 glass border-primary/20 flex flex-col relative z-10">
        {/* 全局进度条 - 固定在顶部 */}
        {activeTask && (
          <div className="sticky top-0 z-30 bg-card/95 backdrop-blur border-b border-border/50 px-4 py-2">
            <div className="flex items-center justify-between text-sm mb-2">
              <div className="flex items-center gap-2">
                <span>{getStepIcon(activeTask.step || "init")}</span>
                <span className="font-medium">{getStepLabel(activeTask.step || "init")}</span>
              </div>
              <span className="text-muted-foreground">{formatProgress(activeTask.progress || 0)}</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full transition-all duration-300 bg-primary"
                style={{ width: `${(activeTask.progress || 0) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* 顶部工具栏 */}
        <div className="p-4 border-b border-border/50 flex items-center justify-between relative z-20">
          <div className="flex items-center gap-4">
            <h2 className="font-semibold">视频生成器</h2>
            <Select value={selectedStyle} onValueChange={setSelectedStyle}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STYLE_PRESETS.map((preset) => (
                  <SelectItem key={preset.id} value={preset.id}>
                    <div>
                      <div className="font-medium">{preset.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {preset.description}
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // 清除当前会话 ID，跳转到新对话页面
              setCurrentSessionId(null)
              navigate("/chat")
              setMessages([
                {
                  id: "welcome",
                  role: "assistant",
                  content: "# 新对话\n\n请输入一个主题，我将为你生成一段精彩的视频。",
                  timestamp: new Date(),
                },
              ])
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            新对话
          </Button>
        </div>

        {/* 消息列表 */}
        <div ref={scrollAreaRef} className="flex-1 overflow-hidden">
          <ScrollArea className="h-full p-4">
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onCancelTask={handleCancelTask}
                  formatProgress={formatProgress}
                  getStepIcon={getStepIcon}
                  getStepLabel={getStepLabel}
                />
              ))}
              {/* 自动滚动目标 */}
              <div ref={messagesEndRef} className="h-1" />
            </div>
          </ScrollArea>
        </div>

        {/* 输入区域 */}
        <div className="p-4 border-t border-border/50">
          <div className="flex gap-2 items-end max-w-4xl mx-auto">
            <div className="flex-1">
              <Textarea
                placeholder="输入主题... (例如: 生命的意义是什么)"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="min-h-[60px] max-h-[200px] resize-none bg-muted/50"
              />
            </div>
            <Button
              onClick={handleSend}
              disabled={!input.trim()}
              className="flex-shrink-0 btn-glow h-[60px] px-6"
            >
              <Send className="h-5 w-5 mr-2" />
              生成
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

// ============================================================================
// 子组件：消息气泡
// ============================================================================

interface MessageBubbleProps {
  message: ChatMessage
  onCancelTask: (messageId: string) => void
  formatProgress: (progress: number) => string
  getStepIcon: (step: StepType) => string
  getStepLabel: (step: StepType) => string
}

function MessageBubble({
  message,
  onCancelTask,
  formatProgress: _formatProgress,
  getStepIcon: _getStepIcon,
  getStepLabel: _getStepLabel,
}: MessageBubbleProps) {
  const isUser = message.role === "user"
  const isSystem = message.role === "system"

  if (isSystem && message.isStreaming) {
    // 流式进度消息 - 简化版，不显示进度条（已有全局进度条）
    return (
      <div className="flex justify-start">
        <div className="max-w-2xl w-full bg-muted/50 rounded-lg p-4">
          {/* 进度头部 */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6 border border-primary/30">
                <AvatarFallback className="bg-primary/20 text-primary text-xs">
                  <Bot className="h-3 w-3" />
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{message.content}</span>
              <Loader2 className="h-3 w-3 animate-spin text-primary" />
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCancelTask(message.id)}
              className="h-7 px-2 text-destructive hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* 文案展示 */}
          {message.scripts && message.scripts.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <span>✍️</span>
                <span>文案生成完成</span>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {message.scripts.map((script) => (
                  <div
                    key={script.id}
                    className="bg-background/50 rounded p-2 text-sm border border-border/50"
                  >
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary">
                          {script.type}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {script.emotion}
                        </span>
                      </div>
                      <p className="text-foreground/90">{script.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 场景预览 */}
            {message.scenes && message.scenes.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-muted-foreground mb-2">
                  已生成 {message.scenes.length} 个场景
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {message.scenes.slice(0, 8).map((scene) => (
                    <div
                      key={scene.id}
                      className={cn(
                        "aspect-[9/16] rounded bg-muted flex items-center justify-center text-xs",
                        scene.imageUrl ? "overflow-hidden" : "text-muted-foreground"
                      )}
                    >
                      {scene.imageUrl ? (
                        <img
                          src={scene.imageUrl}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 错误信息 */}
            {message.error && (
              <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-sm text-destructive">{message.error}</p>
              </div>
            )}
          </div>
        </div>
    )
  }

  if (isSystem && message.finalVideoUrl) {
    // 完成消息 - 保留所有内容
    return (
      <div className="flex justify-start">
        <div className="max-w-2xl w-full bg-muted/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Avatar className="h-6 w-6 border border-primary/30">
              <AvatarFallback className="bg-primary/20 text-primary text-xs">
                <Bot className="h-3 w-3" />
              </AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium">{message.content}</span>
          </div>

          {/* 文案展示 */}
          {message.scripts && message.scripts.length > 0 && (
            <div className="mb-4 space-y-2">
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <span>✍️</span>
                <span>生成的文案</span>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {message.scripts.map((script) => (
                  <div
                    key={script.id}
                    className="bg-background/50 rounded p-3 text-sm border border-border/50"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary">
                        {script.type}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {script.emotion}
                      </span>
                    </div>
                    <p className="text-foreground/90">{script.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 觺频播放器 */}
          <div className="mb-4">
            <div className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
              <span>🎞️</span>
              <span>最终视频（点击播放）</span>
            </div>
            <div
              className="aspect-[9/16] max-w-[200px] rounded-lg bg-muted overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all relative group mx-auto"
              onClick={() => {
                const modal = document.createElement('div');
                modal.className = 'fixed inset-0 bg-black/90 flex items-center justify-center z-[100]';
                modal.onclick = () => modal.remove();
                const video = document.createElement('video');
                video.src = message.finalVideoUrl!;
                video.className = 'max-h-[90vh] max-w-[90vw]';
                video.controls = true;
                video.autoplay = true;
                modal.appendChild(video);
                document.body.appendChild(modal);
              }}
            >
              <video
                src={message.finalVideoUrl}
                className="w-full h-full object-cover"
                muted
                preload="metadata"
                playsInline
              />
              <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-12 h-12 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
                  <span className="text-black text-xl">▶</span>
                </div>
              </div>
              <div className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
                最终视频
              </div>
            </div>
          </div>

          {/* 分镜视频 */}
          {message.scenes && message.scenes.some(s => s.videoUrl) && (
            <div className="mb-4">
              <div className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                <span>🎬</span>
                <span>分镜视频（点击播放）</span>
              </div>
              <div className="grid grid-cols-4 gap-2">
                {message.scenes.filter(s => s.videoUrl).map((scene) => (
                  <div
                    key={scene.id}
                    className="aspect-[9/16] rounded bg-muted overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all relative group"
                    onClick={() => {
                      const modal = document.createElement('div');
                      modal.className = 'fixed inset-0 bg-black/80 flex items-center justify-center z-50';
                      modal.onclick = () => modal.remove();
                      const video = document.createElement('video');
                      video.src = scene.videoUrl!;
                      video.className = 'max-h-[90vh] max-w-[90vw]';
                      video.controls = true;
                      video.autoplay = true;
                      modal.appendChild(video);
                      document.body.appendChild(modal);
                    }}
                  >
                    <video
                      src={scene.videoUrl}
                      className="w-full h-full object-cover"
                      muted
                      preload="metadata"
                      playsInline
                    />
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="w-10 h-10 rounded-full bg-white/90 flex items-center justify-center">
                        <span className="text-black text-lg">▶</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 场景图片 */}
          {message.scenes && message.scenes.some(s => s.imageUrl) && (
            <div className="mb-4">
              <div className="text-sm text-muted-foreground mb-2">场景预览</div>
              <div className="grid grid-cols-4 gap-2">
                {message.scenes.filter(s => s.imageUrl).slice(0, 8).map((scene) => (
                  <div
                    key={scene.id}
                    className="aspect-[9/16] rounded bg-muted overflow-hidden"
                  >
                    <img
                      src={scene.imageUrl!}
                      alt={scene.text}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 flex items-center gap-2 text-sm text-green-500">
            <CheckCircle2 className="h-4 w-4" />
            <span>视频生成完成！</span>
          </div>
        </div>
      </div>
    )
  }

  // 默认系统消息
  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="bg-muted/30 rounded-lg px-4 py-2 text-sm text-muted-foreground">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 border border-primary/30">
          <AvatarFallback className="bg-primary/20 text-primary">
            <Bot className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser ? "bg-primary text-primary-foreground ml-auto" : "bg-muted/50"
        }`}
      >
        {!isUser && <ReactMarkdown>{message.content}</ReactMarkdown>}
        {isUser && <p className="text-sm whitespace-pre-wrap">{message.content}</p>}

        <span className="text-xs opacity-60 mt-2 block">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>

      {isUser && (
        <Avatar className="h-8 w-8 border border-primary/30">
          <AvatarFallback className="bg-primary/20 text-primary">
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}

// 简单的 Markdown 渲染
function ReactMarkdown({ children }: { children: string }) {
  const lines = children.split("\n")
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      {lines.map((line, i) => {
        if (line.startsWith("# ")) {
          return <h1 key={i}>{line.slice(2)}</h1>
        }
        if (line.startsWith("## ")) {
          return <h2 key={i}>{line.slice(3)}</h2>
        }
        if (line.startsWith("- ")) {
          return <li key={i}>{line.slice(2)}</li>
        }
        if (line.startsWith("**") && line.endsWith("**")) {
          return <strong key={i}>{line.slice(2, -2)}</strong>
        }
        return <p key={i}>{line || "\u00A0"}</p>
      })}
    </div>
  )
}
