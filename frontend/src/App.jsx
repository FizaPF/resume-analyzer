import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {

  const [jd, setJd] = useState('')
  const [resume, setResume] = useState('')

  const [result, setResult] = useState(null)

  const [loading, setLoading] = useState(false)

  const analyze = async () => {

    if (!jd || !resume) {
      alert('Please enter both JD and Resume')
      return
    }
    

    try {

      setLoading(true)

      const response = await axios.post(
        'http://localhost:5000/analyze',
        {
          jd: jd,
          resume: resume
        }
      )

      setResult(response.data)

    } catch (error) {

      console.log(error)

      alert('Error connecting to backend')

    } finally {

      setLoading(false)

    }
  }
const downloadReport = async () => {

  try {

    const response = await axios.post(
      'http://localhost:5000/report',
      result,
      {
        responseType: 'blob'
      }
    )

    const url = window.URL.createObjectURL(
      new Blob([response.data])
    )

    const link = document.createElement('a')

    link.href = url

    link.setAttribute(
      'download',
      'report.pdf'
    )

    document.body.appendChild(link)

    link.click()

  } catch (error) {

    console.log(error)

    alert('Failed to download report')

  }
}
  return (

    <div className="container">

      <h1>ATS Resume Analyzer</h1>

      <div className="input-section">

        <textarea
          placeholder="Paste Job Description Here..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />

        <textarea
          placeholder="Paste Resume Here..."
          value={resume}
          onChange={(e) => setResume(e.target.value)}
        />

      </div>

      <button onClick={analyze}>
        {loading ? 'Analyzing...' : 'Analyze Resume'}
      </button>

      {result && (

        <div className="result-box">

          <h2>Match Score: {result.score}%</h2>
          <button onClick={downloadReport}> Download PDF Report </button>

          <div className="keywords">

            <div>

              <h3>✅ Matched Keywords</h3>

              <ul>
                {result.matched.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

            </div>

            <div>

              <h3>❌ Missing Keywords</h3>

              <ul>
                {result.missing.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

            </div>

          </div>

        </div>

      )}

    </div>
  )
}

export default App