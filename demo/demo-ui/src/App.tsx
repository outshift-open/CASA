import { useState } from 'react'
import './App.css'
import { TracesView } from './views/TracesView'
import { AppsView } from './views/AppsView'

type TabId = 'traces' | 'apps'

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('traces')

  return (
    <div className="app-shell">
      <header className="page-header">
        <div>
          <h1>ZTA Authorizations Explorer</h1>
          <p className="page-subtitle">
            Browse authorizations aggregated by the ZTA Auth Server and drill into each stage of execution.
          </p>
        </div>
      </header>

      <nav className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={activeTab === 'traces'}
          className={`tab ${activeTab === 'traces' ? 'active' : ''}`}
          onClick={() => setActiveTab('traces')}
        >
          Traces
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'apps'}
          className={`tab ${activeTab === 'apps' ? 'active' : ''}`}
          onClick={() => setActiveTab('apps')}
        >
          Applications
        </button>
      </nav>

      <div className="tab-content">
        {activeTab === 'traces' && <TracesView />}
        {activeTab === 'apps' && <AppsView />}
      </div>
    </div>
  )
}

export default App
