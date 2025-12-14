import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { modelsApi, tasksApi, runsApi } from '../api'
import type { CreateRunRequest } from '../types'

export default function NewRunPage() {
  const navigate = useNavigate()

  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [selectedTasks, setSelectedTasks] = useState<string[]>([])
  const [runName, setRunName] = useState('')
  const [runDescription, setRunDescription] = useState('')
  const [config, setConfig] = useState({
    temperature: 0.0,
    max_tokens: 512,
    top_p: 1.0,
    timeout: 60,
    max_retries: 3,
    sample_cap: null as number | null,
    trials: 1,
    split: 'test',
  })

  const { data: models, isLoading: modelsLoading } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelsApi.list().then((res) => res.data),
  })

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list().then((res) => res.data),
  })

  const createRunMutation = useMutation({
    mutationFn: (data: CreateRunRequest) => runsApi.create(data),
    onSuccess: (response) => {
      navigate(`/runs/${response.data.run_id}`)
    },
  })

  const toggleModel = (modelId: string) => {
    setSelectedModels((prev) =>
      prev.includes(modelId) ? prev.filter((id) => id !== modelId) : [...prev, modelId]
    )
  }

  const toggleTask = (taskId: string) => {
    setSelectedTasks((prev) =>
      prev.includes(taskId) ? prev.filter((id) => id !== taskId) : [...prev, taskId]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (selectedModels.length === 0) {
      alert('Please select at least one model')
      return
    }

    if (selectedTasks.length === 0) {
      alert('Please select at least one task')
      return
    }

    const requestData: CreateRunRequest = {
      name: runName || undefined,
      description: runDescription || undefined,
      model_ids: selectedModels,
      task_ids: selectedTasks,
      config: config,
    }

    createRunMutation.mutate(requestData)
  }

  if (modelsLoading || tasksLoading) {
    return <div className="spinner" />
  }

  const openaiModels = models?.filter((m) => m.provider === 'openai') || []
  const bedrockModels = models?.filter((m) => m.provider === 'bedrock') || []
  const builtinTasks = tasks?.filter((t) => t.is_builtin) || []
  const customTasks = tasks?.filter((t) => !t.is_builtin) || []

  return (
    <div>
      <h1 className="card-header mb-4">Create New Benchmark Run</h1>

      <form onSubmit={handleSubmit}>
        {/* Run Details */}
        <div className="card mb-4">
          <h3 className="card-header">Run Details</h3>
          <div className="form-group">
            <label className="form-label">Run Name (optional)</label>
            <input
              type="text"
              className="form-input"
              value={runName}
              onChange={(e) => setRunName(e.target.value)}
              placeholder="e.g., GPT-4 vs Claude comparison"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Description (optional)</label>
            <textarea
              className="form-textarea"
              value={runDescription}
              onChange={(e) => setRunDescription(e.target.value)}
              placeholder="Describe the purpose of this benchmark run"
              rows={3}
            />
          </div>
        </div>

        {/* Model Selection */}
        <div className="card mb-4">
          <h3 className="card-header">
            Select Models ({selectedModels.length} selected)
          </h3>

          <div className="mb-3">
            <h4 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              OpenAI Models
            </h4>
            <div className="grid grid-2">
              {openaiModels.map((model) => (
                <label
                  key={model.model_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: selectedModels.includes(model.model_id)
                      ? '#e3f2fd'
                      : 'white',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(model.model_id)}
                    onChange={() => toggleModel(model.model_id)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <div>
                    <div style={{ fontWeight: 500 }}>{model.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                      {model.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Bedrock Models
            </h4>
            <div className="grid grid-2">
              {bedrockModels.map((model) => (
                <label
                  key={model.model_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: selectedModels.includes(model.model_id)
                      ? '#e3f2fd'
                      : 'white',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(model.model_id)}
                    onChange={() => toggleModel(model.model_id)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <div>
                    <div style={{ fontWeight: 500 }}>{model.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                      {model.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Task Selection */}
        <div className="card mb-4">
          <h3 className="card-header">Select Tasks ({selectedTasks.length} selected)</h3>

          <div className="mb-3">
            <h4 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Built-in Tasks
            </h4>
            <div className="grid grid-2">
              {builtinTasks.map((task) => (
                <label
                  key={task.task_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: selectedTasks.includes(task.task_id)
                      ? '#e8f5e9'
                      : 'white',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedTasks.includes(task.task_id)}
                    onChange={() => toggleTask(task.task_id)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <div>
                    <div style={{ fontWeight: 500 }}>
                      {task.name}{' '}
                      <span className="badge badge-builtin" style={{ fontSize: '0.75rem' }}>
                        {task.task_type}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                      {task.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {customTasks.length > 0 && (
            <div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                Custom Tasks
              </h4>
              <div className="grid grid-2">
                {customTasks.map((task) => (
                  <label
                    key={task.task_id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      backgroundColor: selectedTasks.includes(task.task_id)
                        ? '#f3e5f5'
                        : 'white',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTasks.includes(task.task_id)}
                      onChange={() => toggleTask(task.task_id)}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <div>
                      <div style={{ fontWeight: 500 }}>
                        {task.name}{' '}
                        <span className="badge badge-custom" style={{ fontSize: '0.75rem' }}>
                          custom
                        </span>
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                        {task.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Configuration */}
        <div className="card mb-4">
          <h3 className="card-header">Configuration</h3>
          <div className="grid grid-3">
            <div className="form-group">
              <label className="form-label">Temperature</label>
              <input
                type="number"
                className="form-input"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature}
                onChange={(e) =>
                  setConfig({ ...config, temperature: parseFloat(e.target.value) })
                }
              />
            </div>
            <div className="form-group">
              <label className="form-label">Max Tokens</label>
              <input
                type="number"
                className="form-input"
                min="1"
                max="4096"
                value={config.max_tokens}
                onChange={(e) =>
                  setConfig({ ...config, max_tokens: parseInt(e.target.value) })
                }
              />
            </div>
            <div className="form-group">
              <label className="form-label">Top P</label>
              <input
                type="number"
                className="form-input"
                min="0"
                max="1"
                step="0.1"
                value={config.top_p}
                onChange={(e) => setConfig({ ...config, top_p: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Sample Cap (optional)</label>
              <input
                type="number"
                className="form-input"
                min="1"
                value={config.sample_cap || ''}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    sample_cap: e.target.value ? parseInt(e.target.value) : null,
                  })
                }
                placeholder="No limit"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Trials</label>
              <input
                type="number"
                className="form-input"
                min="1"
                max="10"
                value={config.trials}
                onChange={(e) => setConfig({ ...config, trials: parseInt(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Split</label>
              <select
                className="form-select"
                value={config.split}
                onChange={(e) => setConfig({ ...config, split: e.target.value })}
              >
                <option value="test">Test</option>
                <option value="validation">Validation</option>
                <option value="train">Train</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-2">
          <button
            type="submit"
            className="btn btn-success"
            disabled={
              selectedModels.length === 0 ||
              selectedTasks.length === 0 ||
              createRunMutation.isPending
            }
          >
            {createRunMutation.isPending ? 'Creating...' : 'Create Run'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/')}
          >
            Cancel
          </button>
        </div>

        {createRunMutation.isError && (
          <div className="alert alert-error mt-2">
            Error creating run: {(createRunMutation.error as Error).message}
          </div>
        )}
      </form>
    </div>
  )
}
