import React from 'react'
import { Stage, Layer, Rect, Text, Image as KImage, Group } from 'react-konva'

const SAFE_ZONES = {
  // top, right, bottom, left (px)
  FB_STORY: [250, 50, 250, 50],
  IG_STORY: [250, 50, 250, 50],
  SQUARE: [150, 150, 150, 150],
  LANDSCAPE: [200, 200, 200, 200],
  CHECKOUT: [200, 200, 200, 200],
}

function useImage(url) {
  const [image, setImage] = React.useState(null)
  React.useEffect(() => {
    if (!url) return
    const img = new window.Image()
    img.crossOrigin = 'Anonymous'
    img.src = url
    img.onload = () => setImage(img)
  }, [url])
  return image
}

const CanvasImage = ({ el, onDragEnd }) => {
  const src = el.src && el.src.startsWith('/static/') ? `http://localhost:8000${el.src}` : el.src
  const img = useImage(src)
  return (
    <KImage
      x={el.bounds.x}
      y={el.bounds.y}
      width={el.bounds.width}
      height={el.bounds.height}
      image={img}
      draggable
      onDragEnd={(e) => onDragEnd(el.id, e)}
    />
  )
}

const CanvasText = ({ el, onDragEnd }) => {
  const hasBackground = el.background && el.background.a > 0
  const bgColor = hasBackground ? `rgba(${el.background.r},${el.background.g},${el.background.b},${el.background.a})` : null
  const textColor = `rgba(${el.color.r},${el.color.g},${el.color.b},${el.color.a})`

  if (hasBackground) {
    // Manual vertical centering calculation
    const textY = (el.bounds.height - el.font_size) / 2
    
    return (
      <Group
        x={el.bounds.x}
        y={el.bounds.y}
        width={el.bounds.width}
        height={el.bounds.height}
        draggable
        onDragEnd={(e) => onDragEnd(el.id, e)}
      >
        <Rect
          width={el.bounds.width}
          height={el.bounds.height}
          fill={bgColor}
        />
        <Text
          y={textY}
          width={el.bounds.width}
          text={el.text}
          fontSize={el.font_size}
          fontFamily={el.font_family}
          fontStyle={el.font_weight === 'bold' ? 'bold' : 'normal'}
          align="center"
          fill={textColor}
        />
      </Group>
    )
  }

  return (
    <Text
      x={el.bounds.x}
      y={el.bounds.y}
      width={el.bounds.width}
      height={el.bounds.height}
      text={el.text}
      fontSize={el.font_size}
      fontFamily={el.font_family}
      fontStyle={el.font_weight === 'bold' ? 'bold' : 'normal'}
      align={el.align}
      fill={textColor}
      draggable
      onDragEnd={(e) => onDragEnd(el.id, e)}
    />
  )
}

export default function CanvasEditor({ canvas, onChange }) {
  const w = canvas.width
  const h = canvas.height
  const [top, right, bottom, left] = SAFE_ZONES[canvas.format] || [0, 0, 0, 0]
  const safeX = left
  const safeY = top
  const safeW = Math.max(0, w - left - right)
  const safeH = Math.max(0, h - top - bottom)

  const handleDragEnd = (id, e) => {
    const { x, y } = e.target.position()
    const updated = canvas.elements.map(el => el.id === id ? { ...el, bounds: { ...el.bounds, x: Math.round(x), y: Math.round(y) } } : el)
    onChange({ ...canvas, elements: updated })
  }

  // Sort elements by z-index to ensure correct layering
  const sortedElements = [...canvas.elements].sort((a, b) => (a.z || 0) - (b.z || 0))

  return (
    <Stage width={w} height={h} style={{border: '1px solid #ddd', background: `rgba(${canvas.background_color.r},${canvas.background_color.g},${canvas.background_color.b},${canvas.background_color.a})`}}>
      <Layer>
        {/* Safe zone overlay */}
        <Rect x={0} y={0} width={w} height={h} stroke="#ff5252" strokeWidth={4} />
        <Rect x={safeX} y={safeY} width={safeW} height={safeH} stroke="#4caf50" strokeWidth={2} dash={[8,6]} />
        <Text x={safeX + 10} y={safeY + 10} text="SAFE ZONE" fontSize={14} fill="#4caf50" fontStyle="bold" />
        {sortedElements.map(el => {
          if (el.type === 'text' || el.type === 'value_tile') {
            return <CanvasText key={el.id} el={el} onDragEnd={handleDragEnd} />
          }
          if (el.type === 'image' || el.type === 'logo' || el.type === 'packshot') {
            return <CanvasImage key={el.id} el={el} onDragEnd={handleDragEnd} />
          }
          return null
        })}
      </Layer>
    </Stage>
  )
}
