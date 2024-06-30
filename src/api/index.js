import axios from 'axios'

const api = axios.create({
  baseURL: 'http://api.example.com', // Replace with your API base URL
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

export default {
  getReports() {
    return api.get('/reports')
  },
  createReport(data) {
    return api.post('/reports', data)
  }
  // Add more API methods as needed
}