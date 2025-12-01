export function applyAutofixes(canvas, issues) {
  let updated = { ...canvas, elements: canvas.elements.map(e => ({...e, bounds: {...e.bounds}})) }
  for (const issue of issues) {
    const fx = issue.autofix || {}
    switch (fx.action) {
      case 'nudge_inside': {
        const el = updated.elements.find(e => e.id === fx.id)
        if (!el) break
        const nx = Math.min(Math.max(fx.min_x ?? el.bounds.x, 0), fx.max_x ?? el.bounds.x)
        const ny = Math.min(Math.max(fx.min_y ?? el.bounds.y, 0), fx.max_y ?? el.bounds.y)
        el.bounds.x = Math.round(nx)
        el.bounds.y = Math.round(ny)
        break
      }
      case 'set_font_size': {
        const el = updated.elements.find(e => e.id === fx.id)
        if (!el) break
        el.font_size = fx.size || el.font_size
        break
      }
      case 'move_to': {
        const el = updated.elements.find(e => e.id === fx.id)
        if (!el) break
        if (typeof fx.x === 'number') el.bounds.x = fx.x
        if (typeof fx.y === 'number') el.bounds.y = fx.y
        break
      }
      case 'limit_packshots': {
        const keep = fx.keep ?? 3
        let count = 0
        updated.elements = updated.elements.filter(e => {
          if (e.type !== 'packshot') return true
          if (count < keep) { count++; return true }
          return false
        })
        break
      }
      case 'increase_contrast': {
        const el = updated.elements.find(e => e.id === fx.id)
        if (!el) break
        // Simple approach: force dark background and white text for tiles
        if (el.type === 'value_tile' || el.type === 'text') {
          el.background = { r: 0, g: 0, b: 0, a: 1 }
          el.color = { r: 255, g: 255, b: 255, a: 1 }
        }
        break
      }
      default:
        break
    }
  }
  return updated
}
