import { useEffect, useMemo, useState } from 'react'
import { CreateProductoRequest, Producto } from '@/types'
import { useSecciones, useLaboratorios } from '@/hooks/useCatalogs'

type ProductFormValues = CreateProductoRequest

interface ProductFormProps {
  initialValues?: Partial<Producto>
  loading?: boolean
  onSubmit: (values: ProductFormValues) => Promise<void> | void
  onCancel?: () => void
}

const emptyValues: ProductFormValues = {
  nombre: '',
  descripcion: '',
  precio: 0,
  cantidad: 0,
}

export default function ProductForm({ initialValues, loading, onSubmit, onCancel }: ProductFormProps) {
  const [values, setValues] = useState<ProductFormValues>({ ...emptyValues, id_seccion: undefined, id_laboratorio: undefined })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const { data: secciones = [] } = useSecciones()
  const { data: laboratorios = [] } = useLaboratorios()

  useEffect(() => {
    if (initialValues) {
      setValues({
        nombre: initialValues.nombre ?? '',
        descripcion: initialValues.descripcion ?? '',
        precio: typeof initialValues.precio === 'number' ? initialValues.precio : 0,
        cantidad: typeof initialValues.cantidad === 'number' ? initialValues.cantidad : 0,
        id_seccion: initialValues.id_seccion,
        id_laboratorio: initialValues.id_laboratorio,
      })
    }
  }, [initialValues])

  const isValid = useMemo(() => {
    const e: Record<string, string> = {}
    if (!values.nombre || values.nombre.trim().length < 2) e.nombre = 'Ingresa un nombre válido'
    if (values.precio <= 0) e.precio = 'El precio debe ser mayor a 0'
    if (values.cantidad < 0) e.cantidad = 'La cantidad no puede ser negativa'
  if (!values.id_seccion) e.id_seccion = 'Selecciona una sección'
  if (!values.id_laboratorio) e.id_laboratorio = 'Selecciona un laboratorio'
    setErrors(e)
    return Object.keys(e).length === 0
  }, [values])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    const numeric = new Set(['precio', 'cantidad', 'id_seccion', 'id_laboratorio'])
    setValues((v) => ({
      ...v,
      [name]: numeric.has(name) ? (value === '' ? undefined : Number(value)) : value,
    }))
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
          <label>Nombre</label>
          <input name="nombre" value={values.nombre} onChange={handleChange} placeholder="Ej. Té de Manzanilla 20 sobres" />
          {errors.nombre && <span className="form-error">{errors.nombre}</span>}
        </div>
        
        <div className="form-field">
          <label>Sección</label>
          <select name="id_seccion" value={values.id_seccion ?? ''} onChange={handleChange}>
            <option value="">Selecciona sección</option>
            {secciones.map((s) => (
              <option key={s.id_seccion} value={s.id_seccion}>{s.nombre_seccion}</option>
            ))}
          </select>
          {errors.id_seccion && <span className="form-error">{errors.id_seccion}</span>}
        </div>
        <div className="form-field">
          <label>Laboratorio</label>
          <select name="id_laboratorio" value={values.id_laboratorio ?? ''} onChange={handleChange}>
            <option value="">Selecciona laboratorio</option>
            {laboratorios.map((l) => (
              <option key={l.id_laboratorio} value={l.id_laboratorio}>{l.nombre_laboratorio}</option>
            ))}
          </select>
          {errors.id_laboratorio && <span className="form-error">{errors.id_laboratorio}</span>}
        </div>
        <div className="form-field">
          <label>Precio</label>
          <input name="precio" type="number" step="0.01" value={values.precio} onChange={handleChange} />
          {errors.precio && <span className="form-error">{errors.precio}</span>}
        </div>
        <div className="form-field">
          <label>Cantidad</label>
          <input name="cantidad" type="number" step="1" value={values.cantidad} onChange={handleChange} />
          {errors.cantidad && <span className="form-error">{errors.cantidad}</span>}
        </div>
        <div className="form-field form-field-full">
          <label>Descripción</label>
          <textarea name="descripcion" rows={3} value={values.descripcion} onChange={handleChange} placeholder="Detalles del producto" />
        </div>
      </div>

      <div className="form-actions">
        {onCancel && (
          <button type="button" className="btn-outline" onClick={onCancel} disabled={loading}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={!isValid || loading}>
          {loading ? 'Guardando…' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
