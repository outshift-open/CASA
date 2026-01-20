import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { fetchApps, createApp, updateApp, deleteApp } from '../api'
import type { App, AppType } from '../types'

const APP_TYPES: { value: AppType; label: string }[] = [
  { value: 'agent', label: 'Agent' },
  { value: 'client', label: 'Client' },
  { value: 'mcp_server', label: 'MCP Server' },
]

export function AppsView() {
  const [apps, setApps] = useState<App[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingApp, setEditingApp] = useState<App | null>(null)
  const [formData, setFormData] = useState<Omit<App, 'id'>>({
    type: 'agent',
    name: '',
    base_url: '',
    tools: [],
  })
  const [toolsInput, setToolsInput] = useState('')

  const loadApps = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchApps()
      setApps(data.items)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load apps'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadApps()
  }, [])

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      // Convert comma-separated tools string to array
      const tools = toolsInput
        .split(',')
        .map((tool) => tool.trim())
        .filter((tool) => tool.length > 0)

      const appData = { ...formData, tools }

      if (editingApp && editingApp.id) {
        await updateApp(editingApp.id, appData)
      } else {
        await createApp(appData)
      }
      await loadApps()
      resetForm()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save app'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleEdit = (app: App) => {
    console.log('handleEdit called with app:', app)
    setEditingApp(app)
    setFormData({
      type: app.type,
      name: app.name,
      base_url: app.base_url,
      tools: app.tools || [],
    })
    setToolsInput(Array.isArray(app.tools) ? app.tools.join(', ') : '')
    setShowForm(true)
    console.log('showForm should be true now')
  }

  const handleDelete = async (id: string | undefined) => {
    if (!id) return
    if (!confirm('Are you sure you want to delete this app?')) return

    setError(null)
    setDeletingId(id)
    try {
      await deleteApp(id)
      await loadApps()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete app'
      setError(message)
    } finally {
      setDeletingId(null)
    }
  }

  const resetForm = () => {
    setFormData({
      type: 'agent',
      name: '',
      base_url: '',
      tools: [],
    })
    setToolsInput('')
    setEditingApp(null)
    setShowForm(false)
  }

  const openNewAppForm = () => {
    setFormData({
      type: 'agent',
      name: '',
      base_url: '',
      tools: [],
    })
    setToolsInput('')
    setEditingApp(null)
    setShowForm(true)
  }

  return (
    <div className="apps-view">
      <div className="apps-header">
        <h2>Applications</h2>
        <button
          type="button"
          onClick={openNewAppForm}
          className="primary-button"
        >
          + Add Application
        </button>
      </div>

      {error && (
        <div role="alert" className="error-banner">
          <div>
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingApp ? 'Edit Application' : 'New Application'}</h3>
              <button type="button" onClick={resetForm} className="modal-close" aria-label="Close">
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="app-form">
              <div className="form-group">
                <label htmlFor="type">Type</label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                >
                  {APP_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., untrusted_agent"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="base_url">Base URL</label>
                <input
                  type="url"
                  id="base_url"
                  name="base_url"
                  value={formData.base_url}
                  onChange={handleInputChange}
                  placeholder="e.g., http://localhost:8082"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="tools">
                  Tools <span className="optional-label">(optional)</span>
                </label>
                <input
                  type="text"
                  id="tools"
                  name="tools"
                  value={toolsInput}
                  onChange={(e) => setToolsInput(e.target.value)}
                  placeholder="e.g., tool1, tool2, tool3"
                />
                <span className="form-hint">Separate multiple tools with commas</span>
              </div>

              <div className="form-actions">
                <button type="submit" className="primary-button" disabled={submitting}>
                  {submitting ? (editingApp ? 'Updating...' : 'Creating...') : (editingApp ? 'Update' : 'Create')}
                </button>
                <button type="button" onClick={resetForm} className="secondary-button" disabled={submitting}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-indicator">Loading applications...</div>
      ) : apps.length === 0 ? (
        <div className="empty-state">
          <p className="muted">No applications configured yet.</p>
          <p className="muted small-text">Click "Add Application" to create your first app.</p>
        </div>
      ) : (
        <div className="apps-list">
          {apps.map((app) => (
            <div key={app.id} className="app-card">
              <div className="app-card-header">
                <div>
                  <h4>{app.name}</h4>
                  <span className={`app-type-badge app-type-${app.type}`}>
                    {APP_TYPES.find((t) => t.value === app.type)?.label || app.type}
                  </span>
                </div>
                <div className="app-card-actions">
                  <button
                    type="button"
                    onClick={() => handleEdit(app)}
                    className="icon-button"
                    title="Edit"
                    disabled={deletingId === app.id}
                  >
                    ✏️
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(app.id)}
                    className="icon-button delete"
                    title="Delete"
                    disabled={deletingId === app.id}
                  >
                    {deletingId === app.id ? '⏳' : '🗑️'}
                  </button>
                </div>
              </div>
              <div className="app-card-body">
                <div className="app-detail">
                  <span className="muted">URL:</span>
                  <span className="mono">{app.base_url}</span>
                </div>
                {app.id && (
                  <div className="app-detail">
                    <span className="muted">ID:</span>
                    <span className="mono small-text">{app.id}</span>
                  </div>
                )}
                {app.tools && app.tools.length > 0 && (
                  <div className="app-detail">
                    <span className="muted">Tools:</span>
                    <div className="tools-list">
                      {app.tools.map((tool, index) => (
                        <span key={index} className="tool-tag">
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
