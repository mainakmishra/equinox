import { useState } from 'react'
import './App.css'


function App() {
  const [backendMsg, setBackendMsg] = useState<string | null>(null);

  const testBackend = async () => {
    try {
      const res = await fetch('http://localhost:8001/ping');
      const data = await res.json();
      setBackendMsg(data.message);
    } catch (err) {
      setBackendMsg('Error connecting to backend');
    }
  };

  return (
    <>
      <h1>Vite + React</h1>
      <div className="card">
        <button style={{marginLeft: 8}} onClick={testBackend}>
          Test Backend Connection
        </button>
        {backendMsg && (
          <p style={{marginTop: 10}}>Backend says: {backendMsg}</p>
        )}
      </div>
    </>
  )
}

export default App
