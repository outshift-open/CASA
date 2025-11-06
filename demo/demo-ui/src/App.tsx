import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import './App.css'
import { fetchTraces } from './api'
import { TraceTable } from './components/TraceTable'
import type { Trace } from './types'

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50]

function App() {
  const [traces, setTraces] = useState<Trace[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState(0)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    const loadTraces = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchTraces({ page, pageSize, signal: controller.signal })
        setTraces(data.items)
        setTotal(data.total)
        setLastUpdated(new Date().toISOString())

        if (data.page !== page) {
          setPage(data.page)
        }

        if (data.page_size !== pageSize) {
          setPageSize(data.page_size)
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          const message = error instanceof Error ? error.message : 'Failed to load traces'
          setError(message)
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    loadTraces()

    return () => controller.abort()
  }, [page, pageSize, reloadToken])

  const totalPages = useMemo(() => (total === 0 ? 1 : Math.max(1, Math.ceil(total / pageSize))), [total, pageSize])
  const displayPage = total === 0 ? 0 : Math.min(page, totalPages)
  const displayTotalPages = total === 0 ? 0 : totalPages

  const canGoPrev = displayPage > 1
  const canGoNext = displayPage < totalPages && total > 0

  const handleNext = () => {
    if (canGoNext) {
      setPage((current) => current + 1)
    }
  }

  const handlePrev = () => {
    if (canGoPrev) {
      setPage((current) => Math.max(1, current - 1))
    }
  }

  const handlePageSizeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const newSize = Number(event.target.value)
    setPageSize(newSize)
    setPage(1)
  }

  const handleRefresh = () => setReloadToken((token) => token + 1)

  const rangeStart = total === 0 ? 0 : (displayPage - 1) * pageSize + 1
  const rangeEnd = total === 0 ? 0 : Math.min(total, displayPage * pageSize)

  return (
    <div className="app-shell">
      <header className="page-header">
        <div>
          <h1>ZTA Trace Explorer</h1>
          <p className="page-subtitle">
            Browse traces aggregated by the Identity Service ZTA Auth Server and drill into each stage of execution.
          </p>
        </div>
        <div className="header-meta">
          <span className="muted">API base</span>
          <span className="mono">http://127.0.0.1:8000</span>
          {lastUpdated && (
            <span className="muted small-text">Last updated {new Date(lastUpdated).toLocaleTimeString()}</span>
          )}
        </div>
      </header>

      <section className="toolbar" aria-label="Pagination controls">
        <div className="pagination-group">
          <button type="button" onClick={handlePrev} disabled={!canGoPrev || loading}>
            Previous
          </button>
          <button type="button" onClick={handleNext} disabled={!canGoNext || loading}>
            Next
          </button>
          <span className="muted">
            Page {displayPage} of {displayTotalPages}
          </span>
          <span className="muted">
            Showing {rangeStart.toLocaleString()} – {rangeEnd.toLocaleString()} of {total.toLocaleString()} records
          </span>
        </div>

        <div className="toolbar-right">
          <label className="muted" htmlFor="page-size">
            Page size
          </label>
          <select
            id="page-size"
            value={pageSize}
            onChange={handlePageSizeChange}
            disabled={loading}
            aria-label="Select page size"
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>

          <button type="button" onClick={handleRefresh} disabled={loading} className="secondary-button">
            Refresh
          </button>
        </div>
      </section>

      {error && (
        <div role="alert" className="error-banner">
          <div>
            <strong>Failed to load traces.</strong> {error}
          </div>
          <button type="button" onClick={handleRefresh} disabled={loading}>
            Try again
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-indicator" role="status">
          Loading traces…
        </div>
      ) : (
        <TraceTable traces={traces} />
      )}
    </div>
  )
}

export default App
