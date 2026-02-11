import { useState } from 'react'
import {
  Search,
  Upload,
  FileText,
  FileCode,
  Image as ImageIcon,
  MoreVertical,
  Trash2,
  Eye,
  Edit,
  FolderOpen,
  Tag,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  TooltipProvider,
} from '@/components/ui/tooltip'

interface KnowledgeFile {
  id: string
  name: string
  type: 'document' | 'code' | 'image'
  size: string
  uploadedAt: Date
  tags: string[]
  chunks: number
  status: 'indexed' | 'processing'
}

const mockFiles: KnowledgeFile[] = [
  {
    id: '1',
    name: 'React 官方文档.pdf',
    type: 'document',
    size: '2.4 MB',
    uploadedAt: new Date('2024-01-15'),
    tags: ['React', '前端', '文档'],
    chunks: 156,
    status: 'indexed',
  },
  {
    id: '2',
    name: 'Python 数据分析脚本.py',
    type: 'code',
    size: '124 KB',
    uploadedAt: new Date('2024-01-14'),
    tags: ['Python', '数据分析', '脚本'],
    chunks: 45,
    status: 'indexed',
  },
  {
    id: '3',
    name: '系统架构图.png',
    type: 'image',
    size: '1.2 MB',
    uploadedAt: new Date('2024-01-13'),
    tags: ['架构', '设计'],
    chunks: 12,
    status: 'indexed',
  },
  {
    id: '4',
    name: 'API 接口文档.md',
    type: 'document',
    size: '256 KB',
    uploadedAt: new Date('2024-01-12'),
    tags: ['API', '文档'],
    chunks: 67,
    status: 'processing',
  },
]

export function KnowledgeBase() {
  const [files, setFiles] = useState<KnowledgeFile[]>(mockFiles)
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [selectedTab, setSelectedTab] = useState('files')

  const filteredFiles = files.filter(
    (file) =>
      file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      file.tags.some((tag) =>
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      )
  )

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'document':
        return FileText
      case 'code':
        return FileCode
      case 'image':
        return ImageIcon
      default:
        return FileText
    }
  }

  const handleDeleteFile = (id: string) => {
    setFiles(files.filter((file) => file.id !== id))
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">
            知识库管理
          </h1>
          <p className="text-muted-foreground mt-1">
            上传和管理你的知识库文件
          </p>
        </div>
        <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="btn-glow">
              <Upload className="h-5 w-5 mr-2" />
              上传文件
            </Button>
          </DialogTrigger>
          <DialogContent className="glass border-primary/20">
            <DialogHeader>
              <DialogTitle>上传文件到知识库</DialogTitle>
              <DialogDescription>
                支持文档、代码、图片等多种格式,系统会自动进行向量化和索引
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="border-2 border-dashed border-border/50 rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-2">
                  拖拽文件到此处或点击上传
                </p>
                <p className="text-xs text-muted-foreground">
                  支持 PDF, MD, TXT, PY, JS, PNG, JPG 等格式
                </p>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  选择文件夹 (可选)
                </label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="默认文件夹" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">默认文件夹</SelectItem>
                    <SelectItem value="tech">技术文档</SelectItem>
                    <SelectItem value="api">API 文档</SelectItem>
                    <SelectItem value="code">代码示例</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  添加标签 (可选)
                </label>
                <Input placeholder="用逗号分隔多个标签" />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setUploadDialogOpen(false)}
              >
                取消
              </Button>
              <Button className="btn-glow">上传</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜索和统计 */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="搜索文件、标签..."
            className="pl-10 bg-muted/30 border-border/50"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="card-tech">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">总文件</p>
                <p className="text-2xl font-bold">{files.length}</p>
              </div>
            </div>
          </div>
        </Card>
        <Card className="card-tech">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <FolderOpen className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">总向量数</p>
                <p className="text-2xl font-bold">
                  {files.reduce((sum, f) => sum + f.chunks, 0)}
                </p>
              </div>
            </div>
          </div>
        </Card>
        <Card className="card-tech">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Tag className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">标签数</p>
                <p className="text-2xl font-bold">
                  {new Set(files.flatMap((f) => f.tags)).size}
                </p>
              </div>
            </div>
          </div>
        </Card>
        <Card className="card-tech">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <ImageIcon className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">总大小</p>
                <p className="text-2xl font-bold">4.0 MB</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* 内容区域 */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="glass">
          <TabsTrigger value="files">文件列表</TabsTrigger>
          <TabsTrigger value="folders">文件夹</TabsTrigger>
          <TabsTrigger value="tags">标签管理</TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="mt-4">
          <Card className="glass border-primary/20">
            <ScrollArea className="h-[calc(100vh-500px)]">
              <div className="p-4 space-y-2">
                {filteredFiles.map((file) => {
                  const FileIcon = getFileIcon(file.type)
                  return (
                    <div
                      key={file.id}
                      className="flex items-center gap-4 p-4 rounded-lg hover:bg-accent/10 transition-colors group"
                    >
                      <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
                        <FileIcon className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium truncate">{file.name}</p>
                          {file.status === 'processing' && (
                            <span className="px-2 py-0.5 text-xs bg-yellow-500/20 text-yellow-400 rounded-full">
                              处理中
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span>{file.size}</span>
                          <span>•</span>
                          <span>{file.chunks} 个向量</span>
                          <span>•</span>
                          <span>
                            {file.uploadedAt.toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex gap-1 mt-2">
                          {file.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 text-xs bg-primary/20 text-primary rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <TooltipProvider>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuItem>
                              <Eye className="h-4 w-4 mr-2" />
                              查看详情
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Edit className="h-4 w-4 mr-2" />
                              编辑标签
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => handleDeleteFile(file.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              删除
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TooltipProvider>
                    </div>
                  )
                })}
              </div>
            </ScrollArea>
          </Card>
        </TabsContent>

        <TabsContent value="folders" className="mt-4">
          <Card className="glass border-primary/20 p-8">
            <div className="text-center text-muted-foreground">
              <FolderOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>文件夹管理功能即将推出</p>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="tags" className="mt-4">
          <Card className="glass border-primary/20 p-8">
            <div className="text-center text-muted-foreground">
              <Tag className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>标签管理功能即将推出</p>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
