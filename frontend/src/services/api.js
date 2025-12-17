import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptador para adicionar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptador para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const financialAPI = {
  getAccounts: () => api.get('/financial/accounts/'),
  createAccount: (data) => api.post('/financial/accounts/', data),
  updateAccount: (id, data) => api.put(`/financial/accounts/${id}/`, data),
  deleteAccount: (id) => api.delete(`/financial/accounts/${id}/`),
  getAccountSummary: () => api.get('/financial/accounts/summary/'),

  getTransactions: (params) => api.get('/financial/transactions/', { params }),
  createTransaction: (data) => api.post('/financial/transactions/', data),
  updateTransaction: (id, data) => api.put(`/financial/transactions/${id}/`, data),
  deleteTransaction: (id) => api.delete(`/financial/transactions/${id}/`),
  getTransactionSummary: () => api.get('/financial/transactions/summary/'),

  getCommissions: (params) => api.get('/financial/commissions/', { params }),
  createCommission: (data) => api.post('/financial/commissions/', data),
  updateCommission: (id, data) => api.put(`/financial/commissions/${id}/`, data),
  deleteCommission: (id) => api.delete(`/financial/commissions/${id}/`),
  markCommissionAsPaid: (id) => api.post(`/financial/commissions/${id}/mark_as_paid/`),
  getCommissionSummary: () => api.get('/financial/commissions/summary/'),
}

export const bookingAPI = {
  getBookings: (params) => api.get('/bookings/', { params }),
  getBooking: (id) => api.get(`/bookings/${id}/`),
  createBooking: (data) => api.post('/bookings/', data),
  updateBooking: (id, data) => api.put(`/bookings/${id}/`, data),
  deleteBooking: (id) => api.delete(`/bookings/${id}/`),
}

export const serviceAPI = {
  getServices: () => api.get('/services/'),
  getService: (id) => api.get(`/services/${id}/`),
  createService: (data) => api.post('/services/', data),
  updateService: (id, data) => api.put(`/services/${id}/`, data),
  deleteService: (id) => api.delete(`/services/${id}/`),
}

export const professionalAPI = {
  getProfessionals: () => api.get('/professionals/'),
  getProfessional: (id) => api.get(`/professionals/${id}/`),
  createProfessional: (data) => api.post('/professionals/', data),
  updateProfessional: (id, data) => api.put(`/professionals/${id}/`, data),
  deleteProfessional: (id) => api.delete(`/professionals/${id}/`),
}

export default api
