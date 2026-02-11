import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings as SettingsIcon, User, Bell, Shield, Palette } from 'lucide-react'

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">
          系统设置
        </h1>
        <p className="text-muted-foreground mt-1">配置你的系统偏好</p>
      </div>

      <Tabs defaultValue="general">
        <TabsList className="glass">
          <TabsTrigger value="general">通用设置</TabsTrigger>
          <TabsTrigger value="profile">个人资料</TabsTrigger>
          <TabsTrigger value="notifications">通知</TabsTrigger>
          <TabsTrigger value="security">安全</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-4 space-y-4">
          <Card className="glass border-primary/20 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Palette className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">外观设置</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  主题
                </label>
                <div className="flex gap-3">
                  <Button variant="outline" className="flex-1">
                    深色
                  </Button>
                  <Button variant="outline" className="flex-1">
                    浅色
                  </Button>
                  <Button variant="outline" className="flex-1">
                    跟随系统
                  </Button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  主色调
                </label>
                <div className="flex gap-3">
                  {['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'].map(
                    (color) => (
                      <button
                        key={color}
                        className="h-10 w-10 rounded-lg border-2 border-border hover:scale-110 transition-transform"
                        style={{ backgroundColor: color }}
                      />
                    )
                  )}
                </div>
              </div>
            </div>
          </Card>

          <Card className="glass border-primary/20 p-6">
            <div className="flex items-center gap-3 mb-4">
              <SettingsIcon className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">系统偏好</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  默认模型
                </label>
                <select className="w-full h-10 rounded-lg border border-border bg-muted/50 px-3">
                  <option>GPT-4</option>
                  <option>Claude-3</option>
                  <option>GPT-3.5</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  语言
                </label>
                <select className="w-full h-10 rounded-lg border border-border bg-muted/50 px-3">
                  <option>简体中文</option>
                  <option>English</option>
                </select>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="profile" className="mt-4">
          <Card className="glass border-primary/20 p-6">
            <div className="flex items-center gap-3 mb-4">
              <User className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">个人资料</h2>
            </div>
            <div className="space-y-4 max-w-md">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  用户名
                </label>
                <Input placeholder="输入用户名" />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  邮箱
                </label>
                <Input type="email" placeholder="输入邮箱" />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  个人简介
                </label>
                <textarea
                  className="w-full min-h-[80px] rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm resize-none"
                  placeholder="介绍一下自己..."
                />
              </div>
              <Button className="btn-glow">保存更改</Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="mt-4">
          <Card className="glass border-primary/20 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Bell className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">通知设置</h2>
            </div>
            <p className="text-muted-foreground">通知管理功能即将推出</p>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-4">
          <Card className="glass border-primary/20 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">安全设置</h2>
            </div>
            <p className="text-muted-foreground">安全设置功能即将推出</p>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
