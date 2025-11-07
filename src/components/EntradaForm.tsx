import { useMemo, useState } from 'react'
import { useProducts } from '@/hooks/useProducts'
import { useLotes } from '@/hooks/useLotes'

interface EntradaFormValues {
  fecha: string
  id_producto: number
  id_lote: number
  cantidad: number
  proveedor: string
  costo: number
  observaciones?: string
}

interface EntradaFormProps {
  onSubmit: (values: EntradaFormValues) => Promise<void> | void
  onCancel?: () => void
  loading?: boolean
}

const initial: EntradaFormValues = {
  fecha: new Date().toISOString().slice(0, 10),
  id_producto: 0,
  id_lote: 0,
  cantidad: 1,
  proveedor: '',
  costo: 0,
  observaciones: '',
}

export default function EntradaForm({ onSubmit, onCancel, loading }: EntradaFormProps) {
  const [values, setValues] = useState<EntradaFormValues>(initial)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Obtener todos los productos activos
  const { data: productosData } = useProducts({})
  const productos = Array.isArray(productosData?.items) ? productosData.items : []

  // Obtener lotes del producto seleccionado
  const { data: lotes = [] } = useLotes(values.id_producto > 0 ? values.id_producto : undefined)

  const isValid = useMemo(() => {
    const e: Record<string, string> = {}
    if (values.id_producto <= 0) e.id_producto = 'Producto requerido'
    if (values.id_lote <= 0) e.id_lote = 'Lote requerido'
    if (values.cantidad <= 0) e.cantidad = 'Cantidad debe ser mayor a 0'
    if (values.costo < 0) e.costo = 'Costo no puede ser negativo'
    if (!values.proveedor.trim()) e.proveedor = 'Proveedor requerido'
    setErrors(e)
    return Object.keys(e).length === 0
  }, [values])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setValues((v) => ({
      ...v,
      [name]: name === 'cantidad' || name === 'costo' || name === 'id_producto' || name === 'id_lote' ? Number(value) : value,
    }))
    // Si cambió el producto, resetear el lote
    if (name === 'id_producto') {
      setValues((v) => ({ ...v, id_producto: Number(value), id_lote: 0 }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid || loading) return
    await onSubmit(values)
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <div className="form-field">
          <label>Fecha</label>
          <input type="date" name="fecha" value={values.fecha} onChange={handleChange} />
        </div>

        <div className="form-field">
          <label>Producto *</label>
          <select name="id_producto" value={values.id_producto} onChange={handleChange}>
            <option value={0}>-- Selecciona un producto --</option>
            {productos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre} (Stock actual: {p.cantidad})
              </option>
            ))}
          </select>
          {errors.id_producto && <span className="form-error">{errors.id_producto}</span>}
        </div>

        <div className="form-field">
          <label>Lote *</label>
          <select name="id_lote" value={values.id_lote} onChange={handleChange} disabled={values.id_producto <= 0}>
            <option value={0}>-- Selecciona un lote --</option>
            {lotes.map((lote) => (
              <option key={lote.id_lote} value={lote.id_lote}>
                {lote.numero_lote} (Disp: {lote.cantidad_disponible}, Venc: {new Date(lote.fecha_vencimiento).toLocaleDateString()})
              </option>
            ))}
          </select>
          {errors.id_lote && <span className="form-error">{errors.id_lote}</span>}
        </div>

        <div className="form-field">
          <label>Cantidad *</label>
          <input type="number" name="cantidad" value={values.cantidad} onChange={handleChange} min={1} />
          {errors.cantidad && <span className="form-error">{errors.cantidad}</span>}
        </div>

        <div className="form-field">
          <label>Proveedor *</label>
          <input name="proveedor" value={values.proveedor} onChange={handleChange} placeholder="Nombre del proveedor" />
          {errors.proveedor && <span className="form-error">{errors.proveedor}</span>}
        </div>

        <div className="form-field">
          <label>Costo Unitario *</label>
          <input type="number" name="costo" step="0.01" value={values.costo} onChange={handleChange} min={0} />
          {errors.costo && <span className="form-error">{errors.costo}</span>}
        </div>

        <div className="form-field form-field-full">
          <label>Observaciones</label>
          <textarea name="observaciones" rows={3} value={values.observaciones} onChange={handleChange} placeholder="Notas adicionales (opcional)" />
        </div>
      </div>
      <div className="form-actions">
        {onCancel && (
          <button type="button" className="btn-outline" onClick={onCancel} disabled={loading}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={!isValid || loading}>
          {loading ? 'Guardando…' : 'Registrar Entrada'}
        </button>
      </div>
    </form>
  )
}
