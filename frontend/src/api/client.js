import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  try {
    const token = JSON.parse(localStorage.getItem('bookstore-account') || 'null')?.token
    if (token) config.headers.Authorization = `Bearer ${token}`
    const branchId = localStorage.getItem('bookstore-branch-id')
    if (branchId) config.headers['X-Branch-ID'] = branchId
  } catch {
    // Ignore malformed local session data; the API will return an auth error.
  }
  return config
})

export const authApi = {
  login: (payload) => api.post('/auth/login/', payload).then(({ data }) => data),
  cashierLogin: (payload) => api.post('/auth/cashier-login/', payload).then(({ data }) => data),
  signup: (payload) => api.post('/auth/signup/', payload).then(({ data }) => data),
  client: () => api.get('/auth/client/').then(({ data }) => data),
  saveClient: (payload) => api.patch('/auth/client/', payload).then(({ data }) => data),
  createClient: (payload) => api.post('/auth/client/', payload).then(({ data }) => data),
  branches: () => api.get('/auth/branches/').then(({ data }) => data),
  createBranch: (payload) => api.post('/auth/branches/', payload).then(({ data }) => data),
  cashiers: () => api.get('/auth/cashiers/').then(({ data }) => data),
  createCashier: (payload) => api.post('/auth/cashiers/', payload).then(({ data }) => data),
  updateCashier: (id, payload) => api.patch(`/auth/cashiers/${id}/`, payload).then(({ data }) => data),
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('bookstore-account')
      localStorage.removeItem('bookstore-branch-id')
      if (window.location.pathname !== '/login') window.location.assign('/login')
    }
    const detail = error.response?.data?.detail || error.response?.data || error.message
    return Promise.reject(new Error(typeof detail === 'string' ? detail : 'The request could not be completed.'))
  },
)

export const productsApi = {
  list: (params = {}) => api.get('/products/', { params }).then(({ data }) => data),
  create: (payload) => {
    const body = new FormData()
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) body.append(key, value)
    })
    return api.post('/products/', body, { headers: { 'Content-Type': undefined } }).then(({ data }) => data)
  },
  update: (id, payload) => {
    const body = new FormData()
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) body.append(key, value)
    })
    return api.patch(`/products/${id}/`, body, { headers: { 'Content-Type': undefined } }).then(({ data }) => data)
  },
  remove: (id) => api.delete(`/products/${id}/`).then(({ data }) => data),
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
  setLevel: (payload) => api.post('/inventory/set-level/', payload).then(({ data }) => data),
}

export const reportsApi = {
  sales: (params) => api.get('/reports/', { params: { report_type: 'sales', ...params } }).then(({ data }) => data),
  fetch: (params = {}) => api.get('/reports/', { params }).then(({ data }) => data),
}
