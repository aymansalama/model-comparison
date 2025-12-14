import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { runsApi } from '../api'

export default function RunsPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: runs, isLoading, refetch } = useQuery({
    queryKey: ['runs', statusFilter],
    queryFn: () => runsApi.list(statusFilter || undefined).then((res) => res.data),
    refetchInterval: 5000, // Refetch every 5 seconds for live updates
  })

  if (isLoading) {
    return <div className="spinner" />
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="card-header" style={{ marginBottom: 0 }}>
          Benchmark Runs
        </h1>
        <Link to="/new-run" className="btn btn-success">
          Create New Run
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Filter by Status</label>
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ maxWidth: '300px' }}
          >
            <option value="">All</option>
            <option value="queued">Queued</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Runs Table */}
      <div className="card">
        {!runs || runs.length === 0 ? (
          <div className="alert alert-info">
            No runs found. <Link to="/new-run">Create your first run</Link>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Models</th>
                <th>Tasks</th>
                <th>Progress</th>
                <th>Created</th>
                <th>Completed</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.run_id}>
                  <td>
                    <Link to={`/runs/${run.run_id}`} style={{ fontWeight: 500 }}>
                      {run.name}
                    </Link>
                    {run.description && (
                      <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                        {run.description}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`badge badge-${run.status}`}>{run.status}</span>
                    {run.error_message && (
                      <div
                        style={{
                          fontSize: '0.75rem',
                          color: '#e74c3c',
                          marginTop: '0.25rem',
                        }}
                      >
                        Error
                      </div>
                    )}
                  </td>
                  <td>{run.selected_models.length}</td>
                  <td>{run.selected_tasks.length}</td>
                  <td>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${run.progress_percent}%` }}
                      />
                    </div>
                    <div style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                      {run.progress_percent.toFixed(0)}%
                    </div>
                  </td>
                  <td>{new Date(run.created_at).toLocaleString()}</td>
                  <td>
                    {run.completed_at ? new Date(run.completed_at).toLocaleString() : '-'}
                  </td>
                  <td>
                    <Link to={`/runs/${run.run_id}`} className="btn btn-primary">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
