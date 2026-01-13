import React from 'react'
import CanvasEditor from './components/CanvasEditor'
import { uploadAssets, suggestLayouts, checkCompliance, exportImage, serverAutofix, exportBatch, listProjects, saveProject, loadProject, deleteProject, duplicateProject, renameProject, removeBackground, generateCopy } from './api'
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
  const [selectedId, setSelectedId] = React.useState(null)

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
    } catch(e) {
      console.error(e)
      alert("Failed to generate layout. Ensure backend is running and accessible.")
    } finally{ setBusy(false) }
  }

  const onCheck = async ()=>{
    try {
      const res = await checkCompliance(canvas)
      setIssues(res.issues)
    } catch(e) {
      console.error(e)
      alert("Compliance check failed.")
    }
  }

  const onExport = async ()=>{
    try {
      const { url, fileSizeBytes } = await exportImage(canvas, 'PNG')
      setExportPath(url)
      setExportSizeBytes(fileSizeBytes ?? null)
    } catch(e) {
      console.error(e)
      alert("Export failed.")
    }
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
    } catch(e) {
      console.error(e)
      alert("Batch export failed.")
    } finally{ setBusy(false) }
  }

  const onServerAutofix = async ()=>{
    setBusy(true)
    try{
      const fixed = await serverAutofix(canvas)
      setCanvas(fixed)
      setIssues([])
    } catch(e) {
      console.error(e)
      alert("Server autofix failed.")
    } finally{ setBusy(false) }
  }

  const onServerExportAll = async ()=>{
    setBusy(true)
    try{
      const data = await exportBatch({ format, headline, subhead, value_text: valueText, logo, packshots })
      const urls = Object.entries(data).map(([fmt, v]) => ({ format: fmt, url: v.url, fileSizeBytes: v.file_size_bytes }))
      setExportUrls(urls)
    } catch(e) {
      console.error(e)
      alert("Server batch export failed.")
    } finally{ setBusy(false) }
  }

  const refreshProjects = async ()=>{
    try {
      const items = await listProjects()
      setProjects(items)
    } catch (e) {
      console.error("Failed to load projects", e)
    }
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

  const onDeleteProject = async ()=>{
    if(!projectId) return
    if(!window.confirm(`Delete project "${projectId}"?`)) return
    try {
      await deleteProject(projectId)
      await refreshProjects()
      alert('Project deleted')
    } catch(e) {
      console.error(e)
      alert('Failed to delete project')
    }
  }

  const onDuplicateProject = async ()=>{
    if(!projectId) return
    const newId = prompt('Enter new project ID:', projectId + '_copy')
    if(!newId) return
    try {
      const res = await duplicateProject(projectId, newId)
      if(res.error) return alert('Duplication failed: ' + res.error)
      await refreshProjects()
      setProjectId(newId)
      alert('Project duplicated')
    } catch(e) {
      console.error(e)
      alert('Failed to duplicate project')
    }
  }

  const onRenameProject = async ()=>{
    if(!projectId) return
    const newId = prompt('Enter new project ID:', projectId)
    if(!newId || newId === projectId) return
    try {
      const res = await renameProject(projectId, newId)
      if(res.error) return alert('Rename failed: ' + res.error)
      await refreshProjects()
      setProjectId(newId)
      alert('Project renamed')
    } catch (e) {
      console.error(e)
      alert('Failed to rename project')
    }
  }

  const onBringToFront = () => {
    if (!selectedId) return
    setCanvas(curr => {
      const maxZ = Math.max(...curr.elements.map(e => e.z || 0), 0)
      return {
        ...curr,
        elements: curr.elements.map(e => 
          e.id === selectedId ? { ...e, z: maxZ + 1 } : e
        )
      }
    })
  }

  const onSendToBack = () => {
    if (!selectedId) return
    setCanvas(curr => {
      const minZ = Math.min(...curr.elements.map(e => e.z || 0), 0)
      return {
        ...curr,
        elements: curr.elements.map(e => 
          e.id === selectedId ? { ...e, z: minZ - 1 } : e
        )
      }
    })
  }


  const onRemoveBgLastPackshot = async ()=>{
    if (!packshots.length) return
    const last = packshots[packshots.length - 1]
    const res = await removeBackground(last)
    if (res.url) {
      setPackshots(prev => [...prev.slice(0,-1), res.url])
    }
  }

  const onGenerateCopy = async () => {
    const topic = prompt("Enter product name/topic:", "Organic Apples in Summer")
    if (!topic) return
    setBusy(true)
    try {
      const copy = await generateCopy(topic, "retail promotion")
      setHeadline(copy.headline)
      setSubhead(copy.subhead)
      setValueText(copy.value_text)
    } catch(e){
      console.error(e)
      alert('Copy generation failed')
    } finally {
      setBusy(false)
    }
  }

  const changeFormat = (f)=>{
    setFormat(f)
    const { w, h } = FORMATS[f]
    setCanvas(c => ({ ...c, format: f, width: w, height: h }))
  }

  const onResetCanvas = () => {
    if (!window.confirm("Are you sure you want to reset the canvas? All elements will be removed.")) return
    const { w, h } = FORMATS[format]
    setCanvas({
      format: format,
      width: w,
      height: h,
      background_color: { r: 255, g: 255, b: 255, a: 1 },
      elements: []
    })
    setIssues([])
    setExportPath('')
    setExportUrls([])
  }

  return (
    <div className="app">
      <header>
        <h1>AIRC – AI Creative Builder</h1>
        <div className="toolbar">
          <label title="Format determines platform (Instagram, Web, Mobile)">Format:
            <select value={format} onChange={(e)=>changeFormat(e.target.value)}>
              {Object.keys(FORMATS).map(f=> <option key={f} value={f}>{f}</option>)}
            </select>
          </label>
          <button onClick={onSuggest} disabled={busy}>AI Layout</button>
          <button onClick={onResetCanvas} disabled={busy} style={{backgroundColor:'#f0f0f0', color:'#333'}}>Reset</button>
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
            <small style={{display:'block', color:'#666', fontSize:'0.8em', marginTop:'2px'}}>Represents Brand Identity (e.g., FreshFarm)</small>
          </div>
          <div>
            <label>Packshots (max 3): <input type="file" accept="image/*" multiple onChange={onUploadPackshots} /></label>
            <small style={{display:'block', color:'#666', fontSize:'0.8em', marginTop:'2px'}}>Represents Product Images (e.g., Organic Apples)</small>
          </div>
          <div>
            <button onClick={onRemoveBgLastPackshot}>Remove BG (last packshot)</button>
          </div>
          <h3>Copy</h3>
          <button onClick={onGenerateCopy} disabled={busy} style={{width:'100%', marginBottom:'8px'}}>✨ Magic Copy</button>
          <label>Headline<input value={headline} onChange={e=>setHeadline(e.target.value)} /></label>
          <label>Subhead<input value={subhead} onChange={e=>setSubhead(e.target.value)} /></label>
          <label>Value Tile<input value={valueText} onChange={e=>setValueText(e.target.value)} /></label>
          <h3>Project</h3>
          <label>Project ID<input value={projectId} onChange={e=>setProjectId(e.target.value)} /></label>
          <label>Description
            <textarea 
              value={canvas.metadata?.description || ''} 
              onChange={e=>setCanvas(c => ({...c, metadata: {...c.metadata, description: e.target.value}}))}
              rows={2}
              style={{width:'100%', fontSize:'0.9em'}}
            />
          </label>
          <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
            <button onClick={onSaveProject}>Save</button>
            <button onClick={()=>onLoadProject(projectId)}>Load</button>
            <button onClick={onDuplicateProject}>Duplicate</button>
            <button onClick={onRenameProject}>Rename</button>
            <button onClick={onDeleteProject} style={{backgroundColor:'#d9534f', color:'white'}}>Delete</button>
          </div>
          <div>
            <small>Recent:</small>
            <ul style={{maxHeight:'200px', overflowY:'auto', paddingLeft:'1em'}}>
              {projects.map(p => (
                <li key={p.id} style={{marginBottom:'4px'}}>
                  <a href="#" onClick={(e)=>{e.preventDefault(); onLoadProject(p.id)}}>{p.id}</a>
                  {p.updated_at && (
                    <span style={{fontSize:'0.7em', color:'#888', marginLeft:'8px'}}>
                      {new Date(p.updated_at * 1000).toLocaleDateString()}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </aside>
        <section className="canvas">
          <CanvasEditor canvas={canvas} onChange={setCanvas} selectedId={selectedId} onSelect={setSelectedId} />
        </section>
        <aside className="panel right">
          {selectedId && (
            <div style={{marginBottom:'1rem', padding:'10px', border:'1px solid #ccc', borderRadius:'4px'}}>
              <h4>Layer Controls</h4>
              <div style={{display:'flex', gap:'5px'}}>
                <button onClick={onBringToFront}>Bring to Front</button>
                <button onClick={onSendToBack}>Send to Back</button>
              </div>
            </div>
          )}
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
              Exported to: <a href={exportPath.startsWith('http') ? exportPath : `${import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/?$/, '') || 'http://localhost:8000'}${exportPath}`} target="_blank" rel="noreferrer">Download Image</a>
              {typeof exportSizeBytes === 'number' ? <span> ({Math.round(exportSizeBytes/1024)} KB)</span> : null}
            </p>
          )}
          {exportUrls.length > 0 && (
            <>
              <h4>Batch Exports</h4>
              <ul>
                {exportUrls.map((e,i)=> (
                  <li key={i}>
                    {e.format}: <a href={e.url.startsWith('http') ? e.url : `${import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/?$/, '') || 'http://localhost:8000'}${e.url}`} target="_blank" rel="noreferrer">Download</a>
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
