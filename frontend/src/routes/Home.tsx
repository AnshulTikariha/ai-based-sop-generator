import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

export default function Home() {
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [projectId, setProjectId] = useState<string | null>(null)
  const [description, setDescription] = useState<string>('')
  const [templateText, setTemplateText] = useState<string>('')
  const [projectName, setProjectName] = useState<string>('')
  const [modelName, setModelName] = useState<string>(() => localStorage.getItem('ai_model') || 'google/flan-t5-xl')
  const [startedAt, setStartedAt] = useState<number | null>(null)
  const [elapsedMs, setElapsedMs] = useState<number>(0)
  const [showPopup, setShowPopup] = useState<{ message: string; visible: boolean; tone?: 'success'|'error'|'info' } | null>(null)
  const [confirmState, setConfirmState] = useState<{ visible: boolean; message: string; onConfirm: () => Promise<void> | void } | null>(null)
  const timerRef = useRef<number | null>(null)
  const startedAtRef = useRef<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [isDragging, setIsDragging] = useState<boolean>(false)

  const listQuery = useQuery({
    queryKey: ['sops'],
    queryFn: api.listSops,
  })



  const generateMutation = useMutation({
    mutationFn: api.generateSop,
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: ['sops'] })
      if (timerRef.current) {
        window.clearInterval(timerRef.current)
        timerRef.current = null
      }
      setShowPopup({ message: 'SOP generated successfully', visible: true, tone: 'success' })
      setTimeout(() => setShowPopup((s) => (s ? { ...s, visible: false } : s)), 2500)
      setStartedAt(null)
    },
    onError(err: any) {
      setShowPopup({ message: String(err), visible: true, tone: 'error' })
      setTimeout(() => setShowPopup((s) => (s ? { ...s, visible: false } : s)), 3000)
    }
  })

  const isLoading = generateMutation.isPending

  const onFileChange = (f: File | null) => {
    setFile(f)
    setProjectId(null)
    if (f) {
      const nm = f.name.endsWith('.zip') ? f.name.slice(0, -4) : f.name
      setProjectName(nm)
    } else {
      setProjectName('')
    }
  }


  const ensureUploaded = async (): Promise<{ id: string; name: string } | null> => {
    if (projectId) return { id: projectId, name: projectName }
    if (!file) return null
    const res = await api.uploadZip(file)
    setProjectId(res.project_id)
    setProjectName(res.project_name)
    return { id: res.project_id, name: res.project_name }
  }


  const onGenerate = async () => {
    let pid = projectId
    if (!pid) {
      const uploaded = await ensureUploaded()
      if (!uploaded) return
      pid = uploaded.id
    }
    let template: any = undefined
    if (templateText.trim()) {
      try { template = JSON.parse(templateText) } catch {}
    }
    const now = Date.now()
    setStartedAt(now)
    startedAtRef.current = now
    startTimer()
    // Always parse to ensure metadata is fresh before generation
    try {
      await api.parseProject(pid!)
    } catch {}
    await generateMutation.mutateAsync({ project_id: pid!, project_description: description, template })
  }

  const startTimer = () => {
    if (timerRef.current) return
    timerRef.current = window.setInterval(() => {
      const base = startedAtRef.current || Date.now()
      setElapsedMs(Date.now() - base)
    }, 100)
  }

  const stopTimerIfIdle = () => {
    const anyPending = generateMutation.isPending
    if (!anyPending && timerRef.current) {
      window.clearInterval(timerRef.current)
      timerRef.current = null
      startedAtRef.current = null
    }
  }

  useEffect(() => {
    stopTimerIfIdle()
  }, [generateMutation.isPending])

  useEffect(() => () => { if (timerRef.current) window.clearInterval(timerRef.current) }, [])

  // Persist chosen model and apply to backend
  useEffect(() => {
    localStorage.setItem('ai_model', modelName)
    if (modelName === 'none') return
    api.setBackend({ backend: 'hf', hf_model_name: modelName }).catch(() => {})
  }, [modelName])

  const latestId = useMemo(() => {
    if (!listQuery.data || listQuery.data.length === 0) return null
    const maxTs = Math.max(...listQuery.data.map((x) => x.modified_ts))
    const latest = listQuery.data.find((x) => x.modified_ts === maxTs)
    return latest ? latest.id : null
  }, [listQuery.data?.length, listQuery.data && Math.max(...listQuery.data.map((x) => x.modified_ts))])

  const fmt = (ms: number) => {
    const s = Math.floor(ms / 1000)
    const mm = Math.floor(s / 60)
    const ss = s % 60
    const ms2 = Math.floor((ms % 1000) / 100)
    return `${mm.toString().padStart(2,'0')}:${ss.toString().padStart(2,'0')}.${ms2}`
  }

  const exampleTemplate = `{
  "sections": [
    {"title": "Overview", "content": "{description}"},
    {"title": "Tech Stack", "content": "Languages: {metadata[languages]} | Frameworks: {metadata[frameworks]}"},
    {"title": "Setup", "content": "1) Install deps 2) Configure env 3) Run dev server"},
    {"title": "API Routes", "content": "{metadata[routes]}"},
    {"title": "Deployment", "content": "Local: docker-compose up\\nProd: Describe your steps"}
  ]
}`

  return (
    <div className="space-y-6">
      {isLoading && <div className="progress-bar w-full rounded" />}
      {startedAt && isLoading && (
        <div className="text-sm opacity-80">Processing time: {fmt(elapsedMs)}</div>
      )}

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">1) Upload Project (ZIP)</h2>
        <input ref={fileInputRef} type="file" accept=".zip" className="hidden" onChange={(e) => onFileChange(e.target.files?.[0] || null)} />
        <div
          className={`border-2 border-dashed rounded p-6 text-sm cursor-pointer select-none ${isDragging ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20' : 'border-slate-300 dark:border-slate-700'}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false)
            const f = e.dataTransfer.files?.[0]
            if (f && f.name.endsWith('.zip')) onFileChange(f)
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          {file ? (
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-medium">{file.name}</div>
                <div className="opacity-70">Drag & drop a different .zip or click to change</div>
              </div>
              <button
                className="px-2 py-1 border rounded text-xs"
                onClick={(e) => { e.stopPropagation(); onFileChange(null) }}
              >
                Clear
              </button>
            </div>
          ) : (
            <div className="opacity-80">Drag & drop a .zip here, or click to browse</div>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <label className="opacity-80">AI Model:</label>
          <select value={modelName} onChange={(e) => setModelName(e.target.value)} className="px-2 py-1 border rounded bg-transparent">
            <option value="google/flan-t5-xl">google/flan-t5-xl</option>
            <option value="google/flan-t5-large">google/flan-t5-large</option>
            <option value="google/flan-t5-base">google/flan-t5-base</option>
            <option value="google/flan-t5-small">google/flan-t5-small</option>
            <option value="none">Disable AI (rule-based only)</option>
          </select>
        </div>
        <div className="flex gap-2 items-center">
          <button className="px-3 py-1 border rounded hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50" onClick={onGenerate} disabled={generateMutation.isPending || (!projectId && !file)}>Generate SOP</button>
          {isLoading && <svg className="spin h-5 w-5 opacity-80" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.2"/><path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="4"/></svg>}
        </div>
        {(projectId || projectName) && <div className="text-sm opacity-80">Project: {projectName || 'pending upload'} {projectId && `(id ${projectId})`}</div>}
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">2) Describe Project (optional)</h2>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="w-full h-24 border rounded p-2 bg-transparent" placeholder="Short project description" />
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">3) Custom Template (optional, JSON)</h2>
        <textarea value={templateText} onChange={(e) => setTemplateText(e.target.value)} className="w-full h-32 border rounded p-2 bg-transparent" placeholder='{"sections":[{"title":"Overview","content":"{description}"}]}' />
        <div className="text-xs opacity-80 flex items-center gap-2">
          <button
            className="px-2 py-1 border rounded hover:bg-slate-100 dark:hover:bg-slate-800"
            onClick={() => setTemplateText(exampleTemplate)}
          >
            Use example template
          </button>
          <span>Tip: leave empty to generate the full default SOP.</span>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Existing SOPs</h2>
        {listQuery.isLoading && <div>Loading...</div>}
        {!listQuery.isLoading && listQuery.data && listQuery.data.length === 0 && (
          <div className="text-sm opacity-70 border rounded p-4 bg-slate-50 dark:bg-slate-900/40">No data found.</div>
        )}
        {listQuery.data && listQuery.data.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {listQuery.data.map((it) => (
              <div key={it.id} className="border rounded-lg p-4 bg-white/40 dark:bg-slate-900/40 backdrop-blur shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="font-semibold text-slate-900 dark:text-slate-100 break-words pr-2">
                    {it.project_name}
                  </div>
                  {latestId === it.id && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-600 text-white whitespace-nowrap">latest</span>
                  )}
                </div>
                <div className="mt-4 flex gap-2">
                  <Link to={`/sop/${it.id}`} className="px-3 py-1 border rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">View</Link>
                  <button
                    className="px-3 py-1 border rounded text-red-700 border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    onClick={() => {
                      setConfirmState({
                        visible: true,
                        message: `Delete \"${it.project_name}\" SOP?`,
                        onConfirm: async () => {
                        const prev = queryClient.getQueryData<Array<{ id: string; project_name: string; modified_ts: number }>>(['sops'])
                        // Optimistic remove from cache
                        if (prev) {
                          queryClient.setQueryData(['sops'], prev.filter((x) => x.id !== it.id))
                        }
                        try {
                          await api.deleteSop(it.id)
                          setShowPopup({ message: 'SOP deleted', visible: true, tone: 'success' })
                          setTimeout(() => setShowPopup((s) => (s ? { ...s, visible: false } : s)), 2000)
                          // Ensure server truth after optimistic update
                          queryClient.invalidateQueries({ queryKey: ['sops'] })
                        } catch (e) {
                          // Rollback cache on error
                          if (prev) queryClient.setQueryData(['sops'], prev)
                            setShowPopup({ message: 'Failed to delete SOP', visible: true, tone: 'error' })
                            setTimeout(() => setShowPopup((s) => (s ? { ...s, visible: false } : s)), 2500)
                        }
                        },
                      })
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {showPopup?.visible && (
        <div className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg ${showPopup.tone === 'error' ? 'bg-red-600 text-white' : showPopup.tone === 'info' ? 'bg-slate-700 text-white' : 'bg-emerald-600 text-white'}`}>
          {showPopup.message}
        </div>
      )}

      {confirmState?.visible && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-900 border rounded p-4 w-[90%] max-w-sm shadow-xl">
            <div className="mb-4 text-sm">{confirmState.message}</div>
            <div className="flex justify-end gap-2">
              <button className="px-3 py-1 border rounded" onClick={() => setConfirmState(null)}>Cancel</button>
              <button
                className="px-3 py-1 border rounded bg-red-600 text-white"
                onClick={async () => {
                  const cb = confirmState.onConfirm
                  setConfirmState(null)
                  await cb()
                }}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
