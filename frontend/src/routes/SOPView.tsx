import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { useMemo, useState, useRef } from 'react'
import { marked } from 'marked'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import fileDownload from 'js-file-download'

export default function SOPView() {
  const { id } = useParams()
  const { data, isLoading } = useQuery({ queryKey: ['sop', id], queryFn: () => api.getSop(id!) })
  const { data: md } = useQuery({ queryKey: ['sop-md', id], queryFn: () => api.getSopMarkdown(id!), enabled: !!id })

  const [search, setSearch] = useState('')
  const [edited, setEdited] = useState<string>('')
  const [showPdfPreview, setShowPdfPreview] = useState<boolean>(false)
  const exportRef = useRef<HTMLDivElement>(null)

  const html = useMemo(() => {
    const source = edited || md || ''
    return marked.parse(source)
  }, [edited, md])

  const exportMarkdown = () => {
    const content = edited || md || ''
    fileDownload(content, `sop-${id}.md`)
  }

  const exportPDF = async () => {
    if (!exportRef.current) return
    const el = exportRef.current
    const canvas = await html2canvas(el, { scale: 2, backgroundColor: '#ffffff' })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()

    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let position = 0
    let heightLeft = imgHeight

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save(`sop-${id}.pdf`)
  }

  const filteredHtml = useMemo(() => {
    if (!search.trim()) return html
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const regex = new RegExp(search, 'ig')
      doc.querySelectorAll('p, li, h1, h2, h3, h4').forEach((el) => {
        el.innerHTML = el.innerHTML.replace(regex, (m) => `<mark>${m}</mark>`)
      })
      return doc.body.innerHTML
    } catch {
      return html
    }
  }, [html, search])

  if (isLoading) return <div>Loading...</div>
  if (!data) return <div>Not found</div>

  return (
    <div className="grid md:grid-cols-2 gap-6 items-start">
      <div className="space-y-3 h-full">
        <div className="flex items-center gap-2 flex-nowrap overflow-x-auto whitespace-nowrap">
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search in SOP" className="flex-1 min-w-0 px-2 py-1 border rounded bg-transparent" />
          <button onClick={exportMarkdown} className="px-3 py-1 border rounded whitespace-nowrap">Export MD</button>
          <button onClick={exportPDF} className="px-3 py-1 border rounded whitespace-nowrap">Export PDF</button>
          <button onClick={() => setShowPdfPreview((v) => !v)} className="px-3 py-1 border rounded whitespace-nowrap">
            {showPdfPreview ? 'Hide PDF view' : 'Show PDF view'}
          </button>
        </div>
        <textarea className="w-full h-[70vh] border rounded p-2 bg-transparent mt-2" value={edited || (md ?? '')} onChange={(e) => setEdited(e.target.value)} />
      </div>
      <div className="h-full">
        {!showPdfPreview ? (
          <div className="prose prose-slate dark:prose-invert max-w-none border rounded p-4 h-[70vh] overflow-auto mt-2">
            <div dangerouslySetInnerHTML={{ __html: filteredHtml }} />
          </div>
        ) : (
          <div className="border rounded p-2 h-[70vh] overflow-auto mt-2">
            <div ref={exportRef} className="pdf-doc mx-auto">
              <div dangerouslySetInnerHTML={{ __html: html }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
