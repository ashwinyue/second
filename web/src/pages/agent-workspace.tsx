import { useState } from 'react'
import {
  Plus,
  Search,
  Edit,
  Trash2,
  Power,
  PowerOff,
  Sparkles,
  Brain,
  Code,
  Globe,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

// 模拟数据
const mockAgents = [
  {
    id: '1',
    name: '代码助手',
    description: '专业的代码生成和审查 Agent',
    type: 'coding',
    status: 'active',
    model: 'GPT-4',
    conversations: 1234,
  },
  {
    id: '2',
    name: '数据分析专家',
    description: '数据可视化和分析 Agent',
    type: 'analysis',
    status: 'active',
    model: 'Claude-3',
    conversations: 856,
  },
  {
    id: '3',
    name: '客服机器人',
    description: '智能客服对话 Agent',
    type: 'service',
    status: 'inactive',
    model: 'GPT-3.5',
    conversations: 2341,
  },
  {
    id: '4',
    name: '文档生成器',
    description: '自动生成技术文档',
    type: 'writing',
    status: 'active',
    model: 'Claude-3',
    conversations: 567,
  },
]

const agentTypes = [
  { value: 'coding', label: '编程助手', icon: Code },
  { value: 'analysis', label: '数据分析', icon: Brain },
  { value: 'service', label: '客户服务', icon: Globe },
  { value: 'writing', label: '文档写作', icon: Sparkles },
]

export function AgentWorkspace() {
  const [agents, setAgents] = useState(mockAgents)
  const [searchQuery, setSearchQuery] = useState('')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    type: '',
    model: 'GPT-4',
  })

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCreateAgent = () => {
    const agent = {
      id: String(agents.length + 1),
      ...newAgent,
      status: 'active',
      conversations: 0,
    }
    setAgents([...agents, agent])
    setCreateDialogOpen(false)
    setNewAgent({ name: '', description: '', type: '', model: 'GPT-4' })
  }

  const handleToggleStatus = (id: string) => {
    setAgents(
      agents.map((agent) =>
        agent.id === id
          ? { ...agent, status: agent.status === 'active' ? 'inactive' : 'active' }
          : agent
      )
    )
  }

  const handleDeleteAgent = (id: string) => {
    setAgents(agents.filter((agent) => agent.id !== id))
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">
            Agent 工作台
          </h1>
          <p className="text-muted-foreground mt-1">
            创建和管理你的 AI Agents
          </p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="btn-glow">
              <Plus className="h-5 w-5" />
              创建 Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="glass border-primary/20">
            <DialogHeader>
              <DialogTitle>创建新的 Agent</DialogTitle>
              <DialogDescription>
                配置你的 AI Agent 的基本信息和能力
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Agent 名称
                </label>
                <Input
                  placeholder="例如: 代码助手"
                  value={newAgent.name}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, name: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Agent 类型
                </label>
                <Select
                  value={newAgent.type}
                  onValueChange={(value) =>
                    setNewAgent({ ...newAgent, type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择 Agent 类型" />
                  </SelectTrigger>
                  <SelectContent>
                    {agentTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center gap-2">
                          <type.icon className="h-4 w-4" />
                          {type.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  模型
                </label>
                <Select
                  value={newAgent.model}
                  onValueChange={(value) =>
                    setNewAgent({ ...newAgent, model: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="GPT-4">GPT-4</SelectItem>
                    <SelectItem value="GPT-3.5">GPT-3.5</SelectItem>
                    <SelectItem value="Claude-3">Claude-3</SelectItem>
                    <SelectItem value="Claude-2">Claude-2</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  描述
                </label>
                <Textarea
                  placeholder="描述这个 Agent 的功能..."
                  value={newAgent.description}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, description: e.target.value })
                  }
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={handleCreateAgent} className="btn-glow">
                创建
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜索栏 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="搜索 Agents..."
          className="pl-10 bg-muted/30 border-border/50"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="card-tech">
          <CardHeader className="pb-3">
            <CardDescription>总 Agents</CardDescription>
            <CardTitle className="text-2xl">{agents.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="card-tech">
          <CardHeader className="pb-3">
            <CardDescription>运行中</CardDescription>
            <CardTitle className="text-2xl text-green-400">
              {agents.filter((a) => a.status === 'active').length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card className="card-tech">
          <CardHeader className="pb-3">
            <CardDescription>总对话数</CardDescription>
            <CardTitle className="text-2xl">
              {agents.reduce((sum, a) => sum + a.conversations, 0)}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card className="card-tech">
          <CardHeader className="pb-3">
            <CardDescription>今日新增</CardDescription>
            <CardTitle className="text-2xl text-primary">12</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Agent 列表 */}
      <ScrollArea className="h-[calc(100vh-400px)]">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAgents.map((agent) => {
            const AgentIcon = agentTypes.find(
              (t) => t.value === agent.type
            )?.icon || Sparkles

            return (
              <Card key={agent.id} className="card-tech group">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                        <AgentIcon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <CardDescription className="text-xs mt-0.5">
                          {agent.model}
                        </CardDescription>
                      </div>
                    </div>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleToggleStatus(agent.id)}
                          >
                            {agent.status === 'active' ? (
                              <Power className="h-4 w-4 text-green-400" />
                            ) : (
                              <PowerOff className="h-4 w-4 text-muted-foreground" />
                            )}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>
                            {agent.status === 'active' ? '停止' : '启动'}
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    {agent.description}
                  </p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>对话数: {agent.conversations}</span>
                    <div className="flex gap-1">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <Edit className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>编辑</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => handleDeleteAgent(agent.id)}
                            >
                              <Trash2 className="h-3 w-3 text-destructive" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>删除</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </ScrollArea>
    </div>
  )
}
