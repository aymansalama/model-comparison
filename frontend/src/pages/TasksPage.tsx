import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { tasksApi } from '../api'

export default function TasksPage() {
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list().then((res) => res.data),
  })

  if (isLoading) {
    return <div className="spinner" />
  }

  const builtinTasks = tasks?.filter((t) => t.is_builtin) || []
  const customTasks = tasks?.filter((t) => !t.is_builtin) || []

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="card-header" style={{ marginBottom: 0 }}>
          Tasks
        </h1>
        <Link to="/upload-task" className="btn btn-success">
          Upload Custom Task
        </Link>
      </div>

      {/* Built-in Tasks */}
      <div className="card mb-4">
        <h3 className="card-header">Built-in Tasks ({builtinTasks.length})</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Description</th>
              <th>Metrics</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {builtinTasks.map((task) => (
              <tr key={task.task_id}>
                <td>
                  <strong>{task.name}</strong>
                  <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                    {task.task_id}
                  </div>
                </td>
                <td>
                  <span className="badge badge-builtin">{task.task_type}</span>
                </td>
                <td>{task.description}</td>
                <td>
                  <div style={{ fontSize: '0.875rem' }}>
                    {task.metrics.join(', ')}
                  </div>
                </td>
                <td>{new Date(task.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Custom Tasks */}
      {customTasks.length > 0 && (
        <div className="card">
          <h3 className="card-header">Custom Tasks ({customTasks.length})</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Metrics</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {customTasks.map((task) => (
                <tr key={task.task_id}>
                  <td>
                    <strong>{task.name}</strong>
                    <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                      {task.task_id}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-custom">{task.task_type}</span>
                  </td>
                  <td>{task.description}</td>
                  <td>
                    <div style={{ fontSize: '0.875rem' }}>
                      {task.metrics.join(', ')}
                    </div>
                  </td>
                  <td>{new Date(task.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {customTasks.length === 0 && (
        <div className="alert alert-info">
          No custom tasks yet. <Link to="/upload-task">Upload your first custom task</Link>
        </div>
      )}
    </div>
  )
}
