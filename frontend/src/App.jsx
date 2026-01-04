import React from 'react'
import CanvasEditor from './components/CanvasEditor'
import { uploadAssets, suggestLayouts, checkCompliance, exportImage, serverAutofix, exportBatch, listProjects, saveProject, loadProject, removeBackground } from './api'
import { applyAutofixes } from './autofix'

const FORMATS = {
  FB_STORY: { w:1080, h:1920 },
  IG_STORY: { w:1080, h:1920 },
  SQUARE: { w:1080, h:1080 },
  LANDSCAPE: { w:1200, h:628 },
  CHECKOUT: { w:1200, h:900 },
}

export default function App(){
  const [format, setFormat] = React.useState('SQUARE')
  const [headline, setHeadline] = React.useState('Fresh deals this week')
  const [subhead, setSubhead] = React.useState('Quality you can trust')
  const [valueText, setValueText] = React.useState('2 for £5')
  const [logo, setLogo] = React.useState(null)
  const [packshots, setPackshots] = React.useState([])
  const [canvas, setCanvas] = React.useState(() => ({
    format: 'SQUARE', width:1080, height:1080, background_color: {r:255,g:255,b:255,a:1}, elements: [
      { id: 'demo-logo', type: 'logo', src: 'https://placehold.co/150x150?text=Logo', bounds: { x: 50, y: 50, width: 150, height: 150 } },
      { id: 'demo-prod', type: 'packshot', src: 'https://placehold.co/600x600?text=Product', bounds: { x: 240, y: 240, width: 600, height: 600 } },
      { id: 'demo-price', type: 'value_tile', text: '2 for £5', font_size: 80, font_family: 'Arial', font_weight: 'bold', align: 'center', color: {r:255,g:0,b:0,a:1}, bounds: { x: 300, y: 850, width: 480, height: 100 } }
    ]
  }))
  const [issues, setIssues] = React.useState([
    { code: 'WARN', message: 'Logo too close to edge', suggestion: 'Move logo inward' },
    { code: 'INFO', message: 'Headline exceeds safe zone', suggestion: 'Resize text' }
  ])
  const [exportPath, setExportPath] = React.useState('')
  const [exportSizeBytes, setExportSizeBytes] = React.useState(null)
  const [exportUrls, setExportUrls] = React.useState([])
  const [busy, setBusy] = React.useState(false)
  const [projects, setProjects] = React.useState([])
  const [projectId, setProjectId] = React.useState('demo')

  const onUploadLogo = async (e) => {
    const files = [...e.target.files]
    if(!files.length) return
    const saved = await uploadAssets(files)
    setLogo(saved[0])
  }

  const onUploadPackshots = async (e) => {
    const files = [...e.target.files]
    if(!files.length) return
    const saved = await uploadAssets(files)
    setPackshots(prev => [...prev, ...saved])
  }

  const onSuggest = async ()=>{
    setBusy(true)
    try{
      const candidates = await suggestLayouts({ format, headline, subhead, value_text: valueText, logo, packshots })
      if(candidates.length) setCanvas(candidates[0])
    } finally{ setBusy(false) }
  }

  const onCheck = async ()=>{
    const res = await checkCompliance(canvas)
    setIssues(res.issues)
  }

  const onExport = async ()=>{
    const { url, fileSizeBytes } = await exportImage(canvas, 'PNG')
    setExportPath(url)
    setExportSizeBytes(fileSizeBytes ?? null)
  }

  const onApplyFixes = ()=>{
    if (!issues.length) return
    const fixed = applyAutofixes(canvas, issues)
    setCanvas(fixed)
    setIssues([])
  }

  const onExportAll = async ()=>{
    setBusy(true)
    const urls = []
    try{
      for (const f of Object.keys(FORMATS)) {
        const candidates = await suggestLayouts({ format: f, headline, subhead, value_text: valueText, logo, packshots })
        if (!candidates.length) continue
        let c = candidates[0]
        const res = await checkCompliance(c)
        if (res.issues?.length) c = applyAutofixes(c, res.issues)
        const { url, fileSizeBytes } = await exportImage(c, 'PNG')
        urls.push({ format: f, url, fileSizeBytes })
      }
      setExportUrls(urls)
    } finally{ setBusy(false) }
  }

  const onServerAutofix = async ()=>{
    setBusy(true)
    try{
      const fixed = await serverAutofix(canvas)
      setCanvas(fixed)
      setIssues([])
    } finally{ setBusy(false) }
  }

  const onServerExportAll = async ()=>{
    setBusy(true)
    try{
      const data = await exportBatch({ format, headline, subhead, value_text: valueText, logo, packshots })
      const urls = Object.entries(data).map(([fmt, v]) => ({ format: fmt, url: v.url, fileSizeBytes: v.file_size_bytes }))
      setExportUrls(urls)
    } finally{ setBusy(false) }
  }

  const refreshProjects = async ()=>{
    const items = await listProjects()
    setProjects(items)
  }

  React.useEffect(()=>{ refreshProjects() }, [])

  const onSaveProject = async ()=>{
    await saveProject(projectId || 'untitled', canvas)
    await refreshProjects()
  }

  const onLoadProject = async (id)=>{
    const c = await loadProject(id)
    if (c?.format) setCanvas(c)
  }

  const onRemoveBgLastPackshot = async ()=>{
    if (!packshots.length) return
    const last = packshots[packshots.length - 1]
    const res = await removeBackground(last)
    if (res.url) {
      setPackshots(prev => [...prev.slice(0,-1), res.url])
    }
  }

  const changeFormat = (f)=>{
    setFormat(f)
    const { w, h } = FORMATS[f]
    setCanvas(c => ({ ...c, format: f, width: w, height: h }))
  }

  return (
    <div className="app">
      <header>
        <h1>AIRC – AI Creative Builder</h1>
        <div className="toolbar">
          <label>Format:
            <select value={format} onChange={(e)=>changeFormat(e.target.value)}>
              {Object.keys(FORMATS).map(f=> <option key={f} value={f}>{f}</option>)}
            </select>
          </label>
          <button onClick={onSuggest} disabled={busy}>AI Layout</button>
          <button onClick={onCheck}>Compliance Check</button>
          <button onClick={onApplyFixes} disabled={!issues.length}>Apply Fixes</button>
          <button onClick={onExport}>Export PNG</button>
          <button onClick={onExportAll} disabled={busy}>Export All Formats</button>
          <button onClick={onServerAutofix} disabled={busy}>Server Autofix</button>
          <button onClick={onServerExportAll} disabled={busy}>Server Export All</button>
        </div>
      </header>
      <main>
        <aside className="panel left">
          <h3>Assets</h3>
          <div>
            <label>Logo: <input type="file" accept="image/*" onChange={onUploadLogo} /></label>
          </div>
          <div>
            <label>Packshots (max 3): <input type="file" accept="image/*" multiple onChange={onUploadPackshots} /></label>
          </div>
          <div>
            <button onClick={onRemoveBgLastPackshot}>Remove BG (last packshot)</button>
          </div>
          <h3>Copy</h3>
          <label>Headline<input value={headline} onChange={e=>setHeadline(e.target.value)} /></label>
          <label>Subhead<input value={subhead} onChange={e=>setSubhead(e.target.value)} /></label>
          <label>Value Tile<input value={valueText} onChange={e=>setValueText(e.target.value)} /></label>
          <h3>Project</h3>
          <label>Project ID<input value={projectId} onChange={e=>setProjectId(e.target.value)} /></label>
          <div style={{display:'flex', gap:8}}>
            <button onClick={onSaveProject}>Save</button>
            <button onClick={()=>onLoadProject(projectId)}>Load</button>
          </div>
          <div>
            <small>Recent:</small>
            <ul>
              {projects.map(p => (
                <li key={p.id}><a href="#" onClick={(e)=>{e.preventDefault(); onLoadProject(p.id)}}>{p.id}</a></li>
              ))}
            </ul>
          </div>
        </aside>
        <section className="canvas">
          <CanvasEditor canvas={canvas} onChange={setCanvas} />
        </section>
        <aside className="panel right">
          <h3>Compliance</h3>
          {issues.length === 0 ? <p>No issues yet. Run check.</p> : (
            <ul>
              {issues.map((it, idx)=>(
                <li key={idx}>
                  <b>{it.code}</b>: {it.message}
                  {it.suggestion ? <div><small>Suggestion: {it.suggestion}</small></div> : null}
                </li>
              ))}
            </ul>
          )}
          {exportPath && (
            <p>
              Exported to: <a href={exportPath} target="_blank" rel="noreferrer">{exportPath}</a>
              {typeof exportSizeBytes === 'number' ? <span> ({Math.round(exportSizeBytes/1024)} KB)</span> : null}
            </p>
          )}
          {exportUrls.length > 0 && (
            <>
              <h4>Batch Exports</h4>
              <ul>
                {exportUrls.map((e,i)=> (
                  <li key={i}>
                    {e.format}: <a href={e.url} target="_blank" rel="noreferrer">{e.url}</a>
                    {typeof e.fileSizeBytes === 'number' ? <span> ({Math.round(e.fileSizeBytes/1024)} KB)</span> : null}
                  </li>
                ))}
              </ul>
            </>
          )}
        </aside>
      </main>
    </div>
  )
}
