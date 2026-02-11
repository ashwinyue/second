import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/layout/main-layout'
import { AgentWorkspace } from './pages/agent-workspace'
import { ChatInterface } from './pages/chat-interface'
import { KnowledgeBase } from './pages/knowledge-base'
import { Settings } from './pages/settings'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<AgentWorkspace />} />
          <Route path="chat" element={<ChatInterface />} />
          <Route path="knowledge" element={<KnowledgeBase />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
