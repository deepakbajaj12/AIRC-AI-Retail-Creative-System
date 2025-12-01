import React from 'react'
import { Stage, Layer, Rect, Text, Image as KImage } from 'react-konva'

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

export default function CanvasEditor({ canvas, onChange }) {
  const w = canvas.width
  const h = canvas.height

  const handleDragEnd = (id, e) => {
    const { x, y } = e.target.position()
    const updated = canvas.elements.map(el => el.id === id ? { ...el, bounds: { ...el.bounds, x: Math.round(x), y: Math.round(y) } } : el)
    onChange({ ...canvas, elements: updated })
  }

  return (
    <Stage width={w} height={h} style={{border: '1px solid #ddd', background: `rgba(${canvas.background_color.r},${canvas.background_color.g},${canvas.background_color.b},${canvas.background_color.a})`}}>
      <Layer>
        {/* Safe zone overlay */}
        <Rect x={0} y={0} width={w} height={h} stroke="#00bcd4" strokeWidth={1} dash={[6,4]} />
        {canvas.elements.map(el => {
          if (el.type === 'text' || el.type === 'value_tile') {
            return (
              <Text key={el.id}
                x={el.bounds.x}
                y={el.bounds.y}
                width={el.bounds.width}
                height={el.bounds.height}
                text={el.text}
                fontSize={el.font_size}
                fontFamily={el.font_family}
                fontStyle={el.font_weight === 'bold' ? 'bold' : 'normal'}
                align={el.align}
                fill={`rgba(${el.color.r},${el.color.g},${el.color.b},${el.color.a})`}
                draggable
                onDragEnd={(e)=>handleDragEnd(el.id, e)}
              />)
          }
          if (el.type === 'image' || el.type === 'logo' || el.type === 'packshot') {
            const img = useImage(el.src)
            return (
              <KImage key={el.id}
                x={el.bounds.x}
                y={el.bounds.y}
                width={el.bounds.width}
                height={el.bounds.height}
                image={img}
                draggable
                onDragEnd={(e)=>handleDragEnd(el.id, e)}
              />)
          }
          return null
        })}
      </Layer>
    </Stage>
  )
}
