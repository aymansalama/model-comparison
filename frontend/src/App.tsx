import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import HomePage from './pages/HomePage'
import NewRunPage from './pages/NewRunPage'
import RunsPage from './pages/RunsPage'
import RunDetailPage from './pages/RunDetailPage'
import TasksPage from './pages/TasksPage'
import UploadTaskPage from './pages/UploadTaskPage'

function Navigation() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : ''
  }

  return (
    <nav className="nav">
      <div className="nav-content">
        <div className="nav-title">NLP Benchmark Platform</div>
        <ul className="nav-links">
          <li>
            <Link to="/" className={isActive('/')}>
              Home
            </Link>
          </li>
          <li>
            <Link to="/runs" className={isActive('/runs')}>
              Runs
            </Link>
          </li>
          <li>
            <Link to="/new-run" className={isActive('/new-run')}>
              New Run
            </Link>
          </li>
          <li>
            <Link to="/tasks" className={isActive('/tasks')}>
              Tasks
            </Link>
          </li>
          <li>
            <Link to="/upload-task" className={isActive('/upload-task')}>
              Upload Task
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <Navigation />
      <div className="container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/runs" element={<RunsPage />} />
          <Route path="/runs/:runId" element={<RunDetailPage />} />
          <Route path="/new-run" element={<NewRunPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/upload-task" element={<UploadTaskPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
