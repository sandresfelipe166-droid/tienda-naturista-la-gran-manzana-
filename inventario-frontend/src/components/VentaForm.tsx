import { useState, useMemo } from 'react'
import { useProducts } from '@/hooks/useProducts'
import { useLotes } from '@/hooks/useLotes'

interface DetalleVenta {
  id_lote: number
  cantidad: number
  precio_unitario: number
  // Info adicional para display
  producto_nombre?: string
  lote_numero?: string
  stock_disponible?: number
}

interface VentaFormValues {
  id_cliente: number
  metodo_pago: string
  detalles: DetalleVenta[]
}

interface VentaFormProps {
  onSubmit: (values: VentaFormValues) => Promise<void> | void
  onCancel?: () => void
  loading?: boolean
}

export default function VentaForm({ onSubmit, onCancel, loading }: VentaFormProps) {
  const [id_cliente, setIdCliente] = useState<number>(1)
  const [metodo_pago, setMetodoPago] = useState<string>('Efectivo')
  const [detalles, setDetalles] = useState<DetalleVenta[]>([])
  
  // Estado para agregar nuevo item
  const [nuevoProductoId, setNuevoProductoId] = useState<number>(0)
  const [nuevoLoteId, setNuevoLoteId] = useState<number>(0)
  const [nuevaCantidad, setNuevaCantidad] = useState<number>(1)
  const [nuevoPrecio, setNuevoPrecio] = useState<number>(0)

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Obtener productos
  const { data: productosData } = useProducts({})
  const productos = Array.isArray(productosData?.items) ? productosData.items : []

  // Obtener lotes del producto seleccionado para el nuevo item
  const { data: lotes = [] } = useLotes(nuevoProductoId > 0 ? nuevoProductoId : undefined)

  const productoSeleccionado = productos.find(p => p.id === nuevoProductoId)
  const loteSeleccionado = lotes.find(l => l.id_lote === nuevoLoteId)

  const isValid = useMemo(() => {
    const e: Record<string, string> = {}
    if (id_cliente <= 0) e.id_cliente = 'Cliente requerido'
    if (!metodo_pago.trim()) e.metodo_pago = 'Método de pago requerido'
    if (detalles.length === 0) e.detalles = 'Debe agregar al menos un producto'
    setErrors(e)
    return Object.keys(e).length === 0
  }, [id_cliente, metodo_pago, detalles])

  const agregarDetalle = () => {
    if (nuevoProductoId <= 0 || nuevoLoteId <= 0 || nuevaCantidad <= 0 || nuevoPrecio < 0) {
      setErrors({ nuevo_item: 'Complete todos los campos del producto' })
      return
    }
    if (loteSeleccionado && nuevaCantidad > loteSeleccionado.cantidad_disponible) {
      setErrors({ nuevo_item: `Stock insuficiente. Disponible: ${loteSeleccionado.cantidad_disponible}` })
      return
    }

    const nuevoDetalle: DetalleVenta = {
      id_lote: nuevoLoteId,
      cantidad: nuevaCantidad,
      precio_unitario: nuevoPrecio,
      producto_nombre: productoSeleccionado?.nombre,
      lote_numero: loteSeleccionado?.numero_lote,
      stock_disponible: loteSeleccionado?.cantidad_disponible,
    }

    setDetalles([...detalles, nuevoDetalle])
    // Reset form
    setNuevoProductoId(0)
    setNuevoLoteId(0)
    setNuevaCantidad(1)
    setNuevoPrecio(0)
    setErrors({})
  }

  const eliminarDetalle = (index: number) => {
    setDetalles(detalles.filter((_, i) => i !== index))
  }

  const calcularTotal = () => {
    return detalles.reduce((sum, d) => sum + (d.cantidad * d.precio_unitario), 0)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid || loading) return
    await onSubmit({ id_cliente, metodo_pago, detalles })
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-grid">
        {/* Datos generales de la venta */}
        <div className="form-field">
          <label>ID Cliente *</label>
          <input 
            type="number" 
            value={id_cliente} 
            onChange={(e) => setIdCliente(Number(e.target.value))} 
            min={1}
          />
          {errors.id_cliente && <span className="form-error">{errors.id_cliente}</span>}
        </div>

        <div className="form-field">
          <label>Método de Pago *</label>
          <select value={metodo_pago} onChange={(e) => setMetodoPago(e.target.value)}>
            <option value="Efectivo">Efectivo</option>
            <option value="Tarjeta">Tarjeta</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Crédito">Crédito</option>
          </select>
          {errors.metodo_pago && <span className="form-error">{errors.metodo_pago}</span>}
        </div>

        {/* Agregar productos */}
        <div className="form-field form-field-full" style={{ marginTop: '1rem', borderTop: '2px solid #e5e7eb', paddingTop: '1rem' }}>
          <h3 style={{ marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600 }}>Agregar Productos</h3>
        </div>

        <div className="form-field">
          <label>Producto</label>
          <select value={nuevoProductoId} onChange={(e) => {
            setNuevoProductoId(Number(e.target.value))
            setNuevoLoteId(0)
          }}>
            <option value={0}>-- Selecciona un producto --</option>
            {productos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre} (Stock: {p.cantidad})
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label>Lote</label>
          <select 
            value={nuevoLoteId} 
            onChange={(e) => setNuevoLoteId(Number(e.target.value))}
            disabled={nuevoProductoId <= 0}
          >
            <option value={0}>-- Selecciona un lote --</option>
            {lotes.map((lote) => (
              <option key={lote.id_lote} value={lote.id_lote}>
                {lote.numero_lote} (Disp: {lote.cantidad_disponible}, ${lote.precio_compra.toFixed(2)})
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label>Cantidad</label>
          <input 
            type="number" 
            value={nuevaCantidad} 
            onChange={(e) => setNuevaCantidad(Number(e.target.value))}
            min={1}
            disabled={nuevoLoteId <= 0}
          />
        </div>

        <div className="form-field">
          <label>Precio Unitario</label>
          <input 
            type="number" 
            value={nuevoPrecio} 
            onChange={(e) => setNuevoPrecio(Number(e.target.value))}
            min={0}
            step="0.01"
            disabled={nuevoLoteId <= 0}
          />
        </div>

        <div className="form-field form-field-full">
          {errors.nuevo_item && <span className="form-error">{errors.nuevo_item}</span>}
          <button 
            type="button" 
            className="btn-primary"
            onClick={agregarDetalle}
            disabled={nuevoProductoId <= 0 || nuevoLoteId <= 0}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            ➕ Agregar a la Venta
          </button>
        </div>

        {/* Lista de productos agregados */}
        {detalles.length > 0 && (
          <div className="form-field form-field-full" style={{ marginTop: '1rem' }}>
            <h3 style={{ marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600 }}>Productos en la Venta</h3>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', fontSize: '0.85rem' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '0.5rem', textAlign: 'left' }}>Producto</th>
                    <th style={{ padding: '0.5rem', textAlign: 'left' }}>Lote</th>
                    <th style={{ padding: '0.5rem', textAlign: 'center' }}>Cant.</th>
                    <th style={{ padding: '0.5rem', textAlign: 'right' }}>Precio</th>
                    <th style={{ padding: '0.5rem', textAlign: 'right' }}>Subtotal</th>
                    <th style={{ padding: '0.5rem', textAlign: 'center' }}>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {detalles.map((detalle, idx) => (
                    <tr key={idx} style={{ borderTop: '1px solid #e5e7eb' }}>
                      <td style={{ padding: '0.5rem' }}>{detalle.producto_nombre}</td>
                      <td style={{ padding: '0.5rem' }}>{detalle.lote_numero}</td>
                      <td style={{ padding: '0.5rem', textAlign: 'center' }}>{detalle.cantidad}</td>
                      <td style={{ padding: '0.5rem', textAlign: 'right' }}>${detalle.precio_unitario.toFixed(2)}</td>
                      <td style={{ padding: '0.5rem', textAlign: 'right' }}>
                        ${(detalle.cantidad * detalle.precio_unitario).toFixed(2)}
                      </td>
                      <td style={{ padding: '0.5rem', textAlign: 'center' }}>
                        <button
                          type="button"
                          onClick={() => eliminarDetalle(idx)}
                          style={{ 
                            background: 'none', 
                            border: 'none', 
                            cursor: 'pointer',
                            fontSize: '1.2rem',
                            color: '#dc2626'
                          }}
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                  <tr style={{ backgroundColor: '#f0fdf4', fontWeight: 'bold', borderTop: '2px solid #10b981' }}>
                    <td colSpan={4} style={{ padding: '0.75rem', textAlign: 'right' }}>TOTAL:</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '1.1rem' }}>
                      ${calcularTotal().toFixed(2)}
                    </td>
                    <td></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {errors.detalles && <span className="form-error">{errors.detalles}</span>}
      </div>

      <div className="form-actions">
        {onCancel && (
          <button type="button" className="btn-outline" onClick={onCancel} disabled={loading}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={!isValid || loading}>
          {loading ? 'Procesando…' : `Registrar Venta - $${calcularTotal().toFixed(2)}`}
        </button>
      </div>
    </form>
  )
}
