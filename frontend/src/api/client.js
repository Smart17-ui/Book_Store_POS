import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const authApi = {
  login: (payload) => api.post('/auth/login/', payload).then(({ data }) => data),
  signup: (payload) => api.post('/auth/signup/', payload).then(({ data }) => data),
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail || error.response?.data || error.message
    return Promise.reject(new Error(typeof detail === 'string' ? detail : 'The request could not be completed.'))
  },
)

export const productsApi = {
  list: (params = {}) => api.get('/products/', { params }).then(({ data }) => data),
  create: (payload) => api.post('/products/', payload).then(({ data }) => data),
}

export const categoriesApi = {
  list: () => api.get('/categories/').then(({ data }) => data),
}

export const customersApi = {
  list: () => api.get('/customers/').then(({ data }) => data),
  create: (payload) => api.post('/customers/', payload).then(({ data }) => data),
}

export const salesApi = {
  list: () => api.get('/sales/').then(({ data }) => data),
  process: (payload) => api.post('/sales/process/', payload).then(({ data }) => data),
}

export const receiptsApi = {
  list: () => api.get('/receipts/').then(({ data }) => data),
}

export const paymentsApi = {
  methods: () => api.get('/payment-methods/').then(({ data }) => data),
}

export const returnsApi = {
  process: (payload) => api.post('/returns/process/', payload).then(({ data }) => data),
}

export const inventoryApi = {
  list: () => api.get('/inventory/').then(({ data }) => data),
  adjust: (payload) => api.post('/inventory/adjust/', payload).then(({ data }) => data),
}

export const reportsApi = {
  sales: (params) => api.get('/reports/sales/', { params }).then(({ data }) => data),
}
