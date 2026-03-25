const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api'

function getToken() {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken()
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export const api = {
  register: (email: string, username: string, password: string) =>
    request('/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, username, password }) }),
  login: (email: string, password: string) =>
    request('/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) }),
  me: () => request('/auth/me'),
  createProject: (title: string, style: string, file: File) => {
    const form = new FormData()
    form.append('title', title)
    form.append('style', style)
    form.append('file', file)
    return request('/projects/create', { method: 'POST', body: form })
  },
  listProjects: () => request('/projects'),
  getProject: (id: number) => request(`/projects/${id}`),
}
