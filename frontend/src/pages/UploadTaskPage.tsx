import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { tasksApi } from '../api'

export default function UploadTaskPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const uploadMutation = useMutation({
    mutationFn: (file: File) => tasksApi.upload(file),
    onSuccess: (response) => {
      // Invalidate tasks query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      navigate('/tasks')
    },
  })

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  return (
    <div>
      <h1 className="card-header mb-4">Upload Custom Task</h1>

      <div className="card mb-4">
        <h3 className="card-header">Instructions</h3>
        <p>Upload a ZIP file containing:</p>
        <ul style={{ marginLeft: '2rem', marginTop: '1rem' }}>
          <li>
            <strong>task.yaml</strong> - Task definition file
          </li>
          <li>
            <strong>Dataset files</strong> - JSONL or CSV files for each split
          </li>
          <li>
            <strong>README.md</strong> - Optional documentation
          </li>
        </ul>

        <div className="mt-3">
          <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Task Definition Format (task.yaml):
          </h4>
          <pre
            style={{
              backgroundColor: '#f5f5f5',
              padding: '1rem',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '0.875rem',
            }}
          >
            {`task_id: my_custom_task
name: My Custom Task
description: Description of the task
task_type: classification  # or multilabel, ner, summarization, qa, similarity, nli, translation, freeform
input_fields:
  - text
label_field: label
metrics:
  - accuracy
  - f1_macro
prompt_template: |
  Classify the following text.

  Text: {{ text }}

  Label:
splits:
  test: test.jsonl
  validation: validation.jsonl
golden_format:  # optional
  0: negative
  1: positive`}
          </pre>
        </div>

        <div className="mt-3">
          <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Dataset Format (JSONL):
          </h4>
          <pre
            style={{
              backgroundColor: '#f5f5f5',
              padding: '1rem',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '0.875rem',
            }}
          >
            {`{"text": "This is a positive example", "label": 1}
{"text": "This is a negative example", "label": 0}`}
          </pre>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card mb-4">
          <h3 className="card-header">Upload File</h3>

          {/* Drag and Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? '#3498db' : '#ddd'}`,
              borderRadius: '8px',
              padding: '3rem',
              textAlign: 'center',
              backgroundColor: dragActive ? '#e3f2fd' : '#fafafa',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            {file ? (
              <div>
                <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📦</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 500 }}>
                  {file.name}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#7f8c8d', marginTop: '0.5rem' }}>
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </div>
                <button
                  type="button"
                  className="btn btn-secondary mt-2"
                  onClick={(e) => {
                    e.stopPropagation()
                    setFile(null)
                  }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <div>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '0.5rem' }}>
                  Drop your ZIP file here or click to browse
                </div>
                <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
                  Maximum file size: 100 MB
                </div>
              </div>
            )}
          </div>

          {uploadMutation.isError && (
            <div className="alert alert-error mt-3">
              Upload failed:{' '}
              {(uploadMutation.error as any).response?.data?.detail ||
                (uploadMutation.error as Error).message}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="btn btn-success"
            disabled={!file || uploadMutation.isPending}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload Task'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/tasks')}
          >
            Cancel
          </button>
        </div>
      </form>

      {/* Example Download */}
      <div className="card mt-4">
        <h3 className="card-header">Need Help?</h3>
        <p>
          Check the example custom task in the{' '}
          <code>examples/custom_task_example/</code> directory for a complete reference.
        </p>
      </div>
    </div>
  )
}
