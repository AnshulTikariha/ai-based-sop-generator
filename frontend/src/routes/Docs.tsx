import { useMemo, useState } from 'react'
import { api } from '../services/api'
import { marked } from 'marked'

export default function Docs() {
  // Base URL not needed; inferred from cURL
  const [format] = useState<'sheet'|'default'|'vendor'>('vendor')
  const [aiEnabled] = useState<boolean>(true)
  const [curlsText, setCurlsText] = useState<string>('')
  const [busy, setBusy] = useState<boolean>(false)
  const [msg, setMsg] = useState<string>('')
  const [markdown, setMarkdown] = useState<string>('')
  const html = useMemo(() => {
    const out = (marked as any).parse ? (marked as any).parse(markdown || '') : ''
    return typeof out === 'string' ? out : ''
  }, [markdown])

  const generate = async () => {
    if (!curlsText.trim()) { setMsg('Provide at least one cURL'); return }
    setBusy(true); setMsg('')
    try {
      const res = await api.docsGenerateInline({ curls_text: curlsText, format, ai_enabled: aiEnabled })
      setMarkdown(res.markdown || '')
      setMsg('Generated')
    } catch (e: any) {
      setMsg(String(e))
    } finally { setBusy(false) }
  }

  const download = async (kind: 'pdf'|'docx') => {
    if (!curlsText.trim()) { setMsg('Provide at least one cURL'); return }
    setBusy(true); setMsg('')
    try {
      const blob = await api.docsExport({ curls_text: curlsText, format, ai_enabled: aiEnabled, output: kind })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = kind === 'pdf' ? 'api-docs.pdf' : 'api-docs.docx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e: any) {
      setMsg(String(e))
    } finally { setBusy(false) }
  }

  return (
    <div className="grid lg:grid-cols-12 gap-6 items-start">
      <div className="lg:col-span-5 space-y-4">
        <h2 className="text-xl font-semibold">API Docs Builder</h2>
        <div className="grid sm:grid-cols-1 gap-3" />
        <div className="space-y-2">
          <label className="text-sm opacity-80">Paste cURL commands</label>
          <textarea
            value={curlsText}
            onChange={(e) => setCurlsText(e.target.value)}
            className="w-full h-72 border rounded p-3 bg-transparent font-mono text-sm resize-y"
            placeholder={`curl -X POST 'https://api.example.com/v1/resource' \\\n-H 'Content-Type: application/json' \\\n-d '{"key":"value"}'`}
          />
          <div className="flex gap-2">
            <button disabled={busy} onClick={generate} className="px-3 py-1 border rounded hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 flex items-center gap-2">{busy && <span className="inline-block h-3 w-3 rounded-full border-2 border-current border-t-transparent animate-spin" />} Generate Docs</button>
          </div>
          {msg && <div className="text-sm opacity-80">{msg}</div>}
        </div>
      </div>
      <div className="lg:col-span-7 space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Preview</h3>
          <div className="flex gap-2">
            <button disabled={busy} onClick={() => download('pdf')} className="px-3 py-1 border rounded hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 flex items-center gap-2">{busy && <span className="inline-block h-3 w-3 rounded-full border-2 border-current border-t-transparent animate-spin" />} Download PDF</button>
            <button disabled={busy} onClick={() => download('docx')} className="px-3 py-1 border rounded hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 flex items-center gap-2">{busy && <span className="inline-block h-3 w-3 rounded-full border-2 border-current border-t-transparent animate-spin" />} Download DOCX</button>
          </div>
        </div>
        <div className="relative">
          <div className="prose prose-slate dark:prose-invert max-w-none border rounded-lg p-4 h-[70vh] overflow-auto bg-white/40 dark:bg-slate-900/30" dangerouslySetInnerHTML={{ __html: typeof html === 'string' ? html : '' }} />
          {busy && (
            <div className="absolute inset-0 bg-black/10 dark:bg-black/20 flex items-center justify-center rounded">
              <div className="flex items-center gap-3 px-3 py-2 bg-white dark:bg-slate-900 border rounded shadow">
                <span className="inline-block h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
                <span className="text-sm">Processing...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


