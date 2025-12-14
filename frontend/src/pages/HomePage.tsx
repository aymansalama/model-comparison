import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { modelsApi, tasksApi, runsApi } from '../api'

export default function HomePage() {
  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelsApi.list().then((res) => res.data),
  })

  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list().then((res) => res.data),
  })

  const { data: runs } = useQuery({
    queryKey: ['runs'],
    queryFn: () => runsApi.list().then((res) => res.data),
  })

  const { data: credentials } = useQuery({
    queryKey: ['credentials'],
    queryFn: () => modelsApi.checkCredentials().then((res) => res.data),
  })

  const recentRuns = runs?.slice(0, 5) || []
  const completedRuns = runs?.filter((r) => r.status === 'completed').length || 0
  const runningRuns = runs?.filter((r) => r.status === 'running').length || 0

  return (
    <div>
      <h1 className="card-header mb-4">NLP Benchmark Platform</h1>

      {/* Status Cards */}
      <div className="grid grid-3 mb-4">
        <div className="card">
          <h3 className="card-header">Available Models</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3498db' }}>
            {models?.length || 0}
          </div>
          <div style={{ marginTop: '0.5rem', color: '#7f8c8d' }}>
            {models?.filter((m) => m.provider === 'openai').length || 0} OpenAI,{' '}
            {models?.filter((m) => m.provider === 'bedrock').length || 0} Bedrock
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">Available Tasks</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#27ae60' }}>
            {tasks?.length || 0}
          </div>
          <div style={{ marginTop: '0.5rem', color: '#7f8c8d' }}>
            {tasks?.filter((t) => t.is_builtin).length || 0} built-in,{' '}
            {tasks?.filter((t) => !t.is_builtin).length || 0} custom
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">Benchmark Runs</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#e74c3c' }}>
            {runs?.length || 0}
          </div>
          <div style={{ marginTop: '0.5rem', color: '#7f8c8d' }}>
            {completedRuns} completed, {runningRuns} running
          </div>
        </div>
      </div>

      {/* Credentials Status */}
      {credentials && (
        <div className="card mb-4">
          <h3 className="card-header">Provider Credentials</h3>
          <div className="grid grid-2">
            <div>
              <strong>OpenAI:</strong>{' '}
              {credentials.openai_configured ? (
                <span className="badge badge-completed">Configured</span>
              ) : (
                <span className="badge badge-failed">Not Configured</span>
              )}
              {credentials.openai_valid !== null && (
                <>
                  {' - '}
                  {credentials.openai_valid ? (
                    <span style={{ color: '#27ae60' }}>Valid</span>
                  ) : (
                    <span style={{ color: '#e74c3c' }}>Invalid</span>
                  )}
                </>
              )}
            </div>
            <div>
              <strong>AWS Bedrock:</strong>{' '}
              {credentials.aws_configured ? (
                <span className="badge badge-completed">Configured</span>
              ) : (
                <span className="badge badge-failed">Not Configured</span>
              )}
              {credentials.aws_valid !== null && (
                <>
                  {' - '}
                  {credentials.aws_valid ? (
                    <span style={{ color: '#27ae60' }}>Valid</span>
                  ) : (
                    <span style={{ color: '#e74c3c' }}>Invalid</span>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Runs */}
      <div className="card">
        <div className="flex justify-between items-center mb-3">
          <h3 className="card-header" style={{ marginBottom: 0 }}>
            Recent Runs
          </h3>
          <Link to="/runs" className="btn btn-secondary">
            View All
          </Link>
        </div>

        {recentRuns.length === 0 ? (
          <div className="alert alert-info">
            No runs yet. <Link to="/new-run">Create your first run</Link>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentRuns.map((run) => (
                <tr key={run.run_id}>
                  <td>{run.name}</td>
                  <td>
                    <span className={`badge badge-${run.status}`}>{run.status}</span>
                  </td>
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

      {/* Quick Actions */}
      <div className="grid grid-2 mt-4">
        <Link to="/new-run" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h3 className="card-header">Create New Run</h3>
          <p>Start a new benchmark comparison across models and tasks</p>
        </Link>
        <Link
          to="/upload-task"
          className="card"
          style={{ textDecoration: 'none', color: 'inherit' }}
        >
          <h3 className="card-header">Upload Custom Task</h3>
          <p>Add your own dataset and task definition</p>
        </Link>
      </div>
    </div>
  )
}
