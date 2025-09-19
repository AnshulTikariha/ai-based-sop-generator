const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) throw new Error(await res.text())
  return res.headers.get('content-type')?.includes('application/json') ? res.json() : (await res.text() as any)
}

export const api = {
  async uploadZip(file: File) {
    const fd = new FormData()
    fd.append('file', file)
    return request<{ project_id: string; project_name: string; message: string }>(`/sop/upload`, { method: 'POST', body: fd })
  },
  async parseProject(projectId: string) {
    return request<any>(`/sop/parse/${projectId}`, { method: 'POST' })
  },
  async generateSop(data: { project_id: string; project_description?: string; template?: any }) {
    return request<{ id: string; project_name: string; sections: any[]; metadata: any }>(`/sop/generate`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
  },
  async listSops() {
    return request<Array<{ id: string; project_name: string; modified_ts: number }>>(`/sop/list`)
  },
  async getSop(id: string) {
    return request(`/sop/${id}`)
  },
  async getSopMarkdown(id: string) {
    return request<string>(`/sop/${id}/markdown`)
  },
  async deleteSop(id: string) {
    return request<{ ok: boolean }>(`/sop/${id}`, { method: 'DELETE' })
  },
  // AI controls
  async backendsAvailable() {
    return request<{ hf: boolean; gpt4all: boolean }>(`/sop/ai/backends`)
  },
  async setBackend(payload: { backend: 'hf'|'gpt4all'|'none'; hf_model_name?: string; gpt4all_model_path?: string }) {
    return request<{ ok: boolean; backend: string; hf_model_name?: string; gpt4all_model_path?: string }>(`/sop/ai/backend`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) })
  },
  async getBackend() {
    // Reuse backends endpoint to infer availability; we don't have a dedicated getter, so return last set via setBackend isn't persisted.
    // We'll just call setBackend('none') when user selects none.
    return this.backendsAvailable()
  }
}
