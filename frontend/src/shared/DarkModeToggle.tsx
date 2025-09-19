import { useEffect, useState } from 'react'

export default function DarkModeToggle() {
  const [enabled, setEnabled] = useState<boolean>(false)

  useEffect(() => {
    const root = document.documentElement
    if (enabled) root.classList.add('dark')
    else root.classList.remove('dark')
  }, [enabled])

  return (
    <button
      className="text-sm px-3 py-1 rounded border border-slate-300 dark:border-slate-700"
      onClick={() => setEnabled((v) => !v)}
      aria-label="Toggle dark mode"
    >
      {enabled ? 'Dark' : 'Light'}
    </button>
  )
}
