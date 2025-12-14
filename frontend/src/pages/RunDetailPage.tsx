import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { runsApi } from '../api'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()

  const { data: run, isLoading: runLoading } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => runsApi.get(runId!).then((res) => res.data),
    refetchInterval: (data) => {
      // Refetch every 3 seconds if running, otherwise don't refetch
      return data?.status === 'running' ? 3000 : false
    },
  })

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['run-results', runId],
    queryFn: () => runsApi.getResults(runId!).then((res) => res.data),
    enabled: run?.status === 'completed',
  })

  const { data: leaderboard } = useQuery({
    queryKey: ['run-leaderboard', runId],
    queryFn: () => runsApi.getLeaderboard(runId!).then((res) => res.data),
    enabled: run?.status === 'completed',
  })

  if (runLoading) {
    return <div className="spinner" />
  }

  if (!run) {
    return (
      <div className="alert alert-error">
        Run not found
      </div>
    )
  }

  const handleExport = () => {
    runsApi.exportCSV(runId!)
  }

  // Prepare chart data
  const getMetricsChartData = () => {
    if (!results) return []

    const taskGroups = results.reduce((acc, result) => {
      if (!acc[result.task_id]) {
        acc[result.task_id] = []
      }
      acc[result.task_id].push(result)
      return acc
    }, {} as Record<string, typeof results>)

    return Object.entries(taskGroups).map(([taskId, taskResults]) => {
      const chartData: any = { task: taskId }
      taskResults.forEach((result) => {
        // Get first metric value for simplicity
        const firstMetric = Object.entries(result.metrics)[0]
        if (firstMetric) {
          chartData[result.model_id] = firstMetric[1]
        }
      })
      return chartData
    })
  }

  const getLatencyChartData = () => {
    if (!results) return []

    return results.map((result) => ({
      model: result.model_id.split('/').pop() || result.model_id,
      avg: result.avg_latency_ms,
      p50: result.p50_latency_ms,
      p95: result.p95_latency_ms,
    }))
  }

  const getCostChartData = () => {
    if (!results) return []

    return results.map((result) => ({
      model: result.model_id.split('/').pop() || result.model_id,
      cost: result.estimated_cost_usd || 0,
    }))
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="card-header" style={{ marginBottom: 0 }}>
          {run.name}
        </h1>
        <Link to="/runs" className="btn btn-secondary">
          Back to Runs
        </Link>
      </div>

      {/* Run Status */}
      <div className="card mb-4">
        <div className="grid grid-2">
          <div>
            <div className="mb-2">
              <strong>Status:</strong>{' '}
              <span className={`badge badge-${run.status}`}>{run.status}</span>
            </div>
            <div className="mb-2">
              <strong>Created:</strong> {new Date(run.created_at).toLocaleString()}
            </div>
            {run.completed_at && (
              <div className="mb-2">
                <strong>Completed:</strong> {new Date(run.completed_at).toLocaleString()}
              </div>
            )}
            {run.description && (
              <div className="mb-2">
                <strong>Description:</strong> {run.description}
              </div>
            )}
          </div>
          <div>
            <div className="mb-2">
              <strong>Models:</strong> {run.selected_models.length}
            </div>
            <div className="mb-2">
              <strong>Tasks:</strong> {run.selected_tasks.length}
            </div>
            <div className="mb-2">
              <strong>Evaluations:</strong> {run.completed_evaluations} / {run.total_evaluations}
            </div>
            {run.failed_evaluations > 0 && (
              <div className="mb-2" style={{ color: '#e74c3c' }}>
                <strong>Failed:</strong> {run.failed_evaluations}
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {run.status !== 'completed' && (
          <div className="mt-3">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${run.progress_percent}%` }} />
            </div>
            <div style={{ fontSize: '0.875rem', marginTop: '0.25rem', textAlign: 'center' }}>
              {run.progress_percent.toFixed(0)}%
            </div>
          </div>
        )}

        {run.error_message && (
          <div className="alert alert-error mt-3">
            <strong>Error:</strong> {run.error_message}
          </div>
        )}
      </div>

      {/* Configuration */}
      <div className="card mb-4">
        <h3 className="card-header">Configuration</h3>
        <div className="grid grid-3">
          <div>
            <strong>Temperature:</strong> {run.config.temperature}
          </div>
          <div>
            <strong>Max Tokens:</strong> {run.config.max_tokens}
          </div>
          <div>
            <strong>Top P:</strong> {run.config.top_p}
          </div>
          <div>
            <strong>Trials:</strong> {run.config.trials}
          </div>
          <div>
            <strong>Split:</strong> {run.config.split}
          </div>
          <div>
            <strong>Sample Cap:</strong> {run.config.sample_cap || 'None'}
          </div>
        </div>
      </div>

      {/* Results */}
      {run.status === 'completed' && results && (
        <>
          {/* Export Button */}
          <div className="mb-4">
            <button onClick={handleExport} className="btn btn-primary">
              Export Results (CSV)
            </button>
          </div>

          {/* Metrics Chart */}
          <div className="card mb-4">
            <h3 className="card-header">Performance by Task</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getMetricsChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="task" />
                <YAxis />
                <Tooltip />
                <Legend />
                {run.selected_models.map((modelId, idx) => (
                  <Bar
                    key={modelId}
                    dataKey={modelId}
                    fill={`hsl(${(idx * 360) / run.selected_models.length}, 70%, 50%)`}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Latency Chart */}
          <div className="card mb-4">
            <h3 className="card-header">Latency (ms)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getLatencyChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="model" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg" fill="#3498db" name="Average" />
                <Bar dataKey="p95" fill="#e74c3c" name="P95" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Cost Chart */}
          {getCostChartData().some((d) => d.cost > 0) && (
            <div className="card mb-4">
              <h3 className="card-header">Estimated Cost (USD)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={getCostChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="model" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="cost" fill="#27ae60" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Detailed Results Table */}
          <div className="card">
            <h3 className="card-header">Detailed Results</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Task</th>
                  <th>Metrics</th>
                  <th>Latency (ms)</th>
                  <th>Tokens</th>
                  <th>Cost (USD)</th>
                  <th>Samples</th>
                  <th>Errors</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, idx) => (
                  <tr key={idx}>
                    <td>{result.model_id}</td>
                    <td>{result.task_id}</td>
                    <td>
                      {Object.entries(result.metrics).map(([key, value]) => (
                        <div key={key} style={{ fontSize: '0.875rem' }}>
                          <strong>{key}:</strong> {(value as number).toFixed(3)}
                        </div>
                      ))}
                    </td>
                    <td>
                      {result.avg_latency_ms ? (
                        <>
                          <div>Avg: {result.avg_latency_ms.toFixed(0)}</div>
                          <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                            P95: {result.p95_latency_ms?.toFixed(0)}
                          </div>
                        </>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      {result.total_input_tokens ? (
                        <>
                          <div>In: {result.total_input_tokens}</div>
                          <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                            Out: {result.total_output_tokens}
                          </div>
                        </>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      {result.estimated_cost_usd
                        ? `$${result.estimated_cost_usd.toFixed(4)}`
                        : '-'}
                    </td>
                    <td>{result.num_samples}</td>
                    <td>
                      {result.num_errors > 0 ? (
                        <span style={{ color: '#e74c3c' }}>{result.num_errors}</span>
                      ) : (
                        0
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {run.status === 'running' && (
        <div className="alert alert-info">
          Benchmark is currently running. Results will appear here when complete.
        </div>
      )}
    </div>
  )
}
