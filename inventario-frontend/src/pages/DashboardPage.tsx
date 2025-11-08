import { useEffect, useMemo, useState } from 'react'
import { useSecciones, useLaboratorios } from '@/hooks/useCatalogs'
import Modal from '@/components/Modal'
import ProductForm from '@/components/ProductForm'
import EntradaForm from '@/components/EntradaForm'
import VentaForm from '@/components/VentaForm'
import { useCreateProduct, useUpdateProduct, useDeleteProduct } from '@/hooks/useProducts'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useProducts } from '@/hooks/useProducts'
import './DashboardPage.css'
import { useVentasMes, useVentasAnio, useGastosMes, useGastosAnio } from '@/hooks/useStats'
import { useVentasListado } from '@/hooks/useVentas'
import { useGastosListado } from '@/hooks/useGastos'
import { useCreateVenta } from '@/hooks/useCreateVenta'
import { useCreateGasto } from '@/hooks/useCreateGasto'
import { useCrearEntrada, useEntradasListado, useEntradasMes, useEntradasAnio } from '@/hooks/useEntradas'
import { useCotizacionesListado, useCotizacionEstadisticas, useCrearCotizacion, useConvertirCotizacionAVenta } from '@/hooks/useCotizaciones'
import { NotificationPanel } from '@/components/NotificationPanel'
import { useInventoryNotifications, useNotificationPermission } from '@/hooks/useInventoryNotifications'
import { usePermissions } from '@/hooks/usePermissions'
import { AdminPanelPage } from '@/pages/AdminPanelPage'

const sidebarMenu = [
  { id: 'panel', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1" fill="currentColor"/><rect x="14" y="3" width="7" height="7" rx="1" fill="currentColor"/><rect x="14" y="14" width="7" height="7" rx="1" fill="currentColor"/><rect x="3" y="14" width="7" height="7" rx="1" fill="currentColor"/></svg>, label: 'PANEL DE CONTROL', permission: null },
  { id: 'productos', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="4" y="7" width="16" height="11" rx="2" stroke="currentColor" strokeWidth="2" fill="none"/><rect x="7" y="4" width="10" height="3" rx="1.5" fill="currentColor"/></svg>, label: 'PRODUCTOS', permission: 'productos' },
  { id: 'entradas', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><path d="M12 5l-4 4M12 5l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>, label: 'ENTRADAS', permission: 'entradas' },
  { id: 'ventas', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>, label: 'VENTAS', permission: 'ventas' },
  { id: 'gastos', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" fill="none"/><path d="M8 12h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>, label: 'GASTOS', permission: 'gastos' },
  { id: 'cotizacion', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 7h16M4 12h16M4 17h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>, label: 'COTIZACIÓN', permission: 'cotizaciones' },
  { id: 'devoluciones', icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 14l-4-4 4-4M5 10h10a4 4 0 014 4v0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>, label: 'DEVOLUCIONES', permission: null },
  { id: 'admin', icon: '👑', label: 'ADMINISTRACIÓN', requireAdmin: true },
]

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { can, isAdmin, getRoleName } = usePermissions()
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [seccionId, setSeccionId] = useState<number | undefined>(undefined)
  const [laboratorioId, setLaboratorioId] = useState<number | undefined>(undefined)
  const [soloStockBajo, setSoloStockBajo] = useState(false)
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false)

  // Solicitar permisos de notificación al cargar el dashboard
  const { permission, requestPermission } = useNotificationPermission()
  const { unreadCount } = useInventoryNotifications()

  useEffect(() => {
    if (permission === 'default') {
      requestPermission()
    }
  }, [permission, requestPermission])
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search.trim()), 350)
    return () => clearTimeout(t)
  }, [search])
  const productFilters = useMemo(
    () => ({
      nombre: debouncedSearch || undefined,
      id_seccion: seccionId,
      id_laboratorio: laboratorioId,
      stock_bajo: soloStockBajo ? true : undefined,
    }),
    [debouncedSearch, seccionId, laboratorioId, soloStockBajo]
  )
  const { data: productsData, isLoading: productsLoading } = useProducts(productFilters)
  const { data: secciones = [] } = useSecciones()
  const { data: laboratorios = [] } = useLaboratorios()
  const [activeView, setActiveView] = useState('panel')
  const [isProductModalOpen, setProductModalOpen] = useState(false)
  const [isEntradaModalOpen, setEntradaModalOpen] = useState(false)
  type Toast = { message: string; type: 'success' | 'error' }
  const [toast, setToast] = useState<Toast | null>(null)
  const [isEditModalOpen, setEditModalOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<any | null>(null)
  const [isDeleteModalOpen, setDeleteModalOpen] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const createProduct = useCreateProduct()
  const updateProduct = useUpdateProduct()
  const deleteProduct = useDeleteProduct()
  const createVenta = useCreateVenta()
  const createGasto = useCreateGasto()
  const crearEntrada = useCrearEntrada()
  const crearCotizacion = useCrearCotizacion()
  const convertirCotizacion = useConvertirCotizacionAVenta()
  const [isVentaModalOpen, setVentaModalOpen] = useState(false)
  const [isGastoModalOpen, setGastoModalOpen] = useState(false)
  const [isCotizacionModalOpen, setCotizacionModalOpen] = useState(false)
  // Control de sidebar en móvil
  const [sidebarExpanded, setSidebarExpanded] = useState(false)

  // Fecha actual para filtros de estadísticas
  const now = new Date()
  const currentMonth = now.getMonth() + 1
  const currentYear = now.getFullYear()
  // Filtros de fecha para Ventas
  const [ventasMonth, setVentasMonth] = useState<number>(currentMonth)
  const [ventasYear, setVentasYear] = useState<number>(currentYear)
  // Filtros de fecha para Gastos
  const [gastosMonth, setGastosMonth] = useState<number>(currentMonth)
  const [gastosYear, setGastosYear] = useState<number>(currentYear)
  // Filtros de fecha para Entradas
  const [entradasMonth, setEntradasMonth] = useState<number>(currentMonth)
  const [entradasYear, setEntradasYear] = useState<number>(currentYear)

  const { data: ventasMes } = useVentasMes(ventasMonth, ventasYear, true)
  const { data: ventasAnio } = useVentasAnio(ventasYear, true)
  const { data: gastosMes } = useGastosMes(gastosMonth, gastosYear, true)
  const { data: gastosAnio } = useGastosAnio(gastosYear, true)
  const { data: entradasMes } = useEntradasMes(entradasMonth, entradasYear, true)
  const { data: entradasAnio } = useEntradasAnio(entradasYear, true)
  const { data: ventasLista = [] } = useVentasListado({ mes: ventasMonth, año: ventasYear, limit: 50 })
  const { data: gastosLista = [] } = useGastosListado({ mes: gastosMonth, año: gastosYear, limit: 50 })
  const { data: entradasLista = [] } = useEntradasListado({ mes: entradasMonth, año: entradasYear, limit: 50 })
  const { data: cotizacionesLista = [] } = useCotizacionesListado({ limit: 50 })
  const { data: cotizacionesStats } = useCotizacionEstadisticas(true)

  const yearOptions = useMemo(() => {
    const years: number[] = []
    for (let y = currentYear; y >= currentYear - 5; y--) years.push(y)
    return years
  }, [currentYear])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const productos = Array.isArray(productsData?.items)
    ? productsData.items
    : Array.isArray(productsData)
      ? productsData
      : []
  const visibleProductos = soloStockBajo ? productos.filter(p => p.cantidad <= 5) : productos

  // Calcular métricas reales
  const totalProductos = productos.length
  const stockBajo = productos.filter(p => p.cantidad <= 5).length

  // Métricas con iconos coloridos (estilo primera imagen)
  const metrics = [
    {
      label: 'Total Productos',
      value: totalProductos.toString(),
      icon: <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="3" y="6" width="18" height="15" rx="2" fill="#7c3aed"/><path d="M8 11h8M8 14h5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>,
      bgColor: '#ede9fe',
      iconColor: '#7c3aed',
    },
    {
      label: 'Stock Bajo',
      value: stockBajo.toString(),
      icon: <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M12 8v4m0 4h.01" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round"/><circle cx="12" cy="12" r="9" stroke="#f59e0b" strokeWidth="2" fill="none"/></svg>,
      bgColor: '#fef3c7',
      iconColor: '#f59e0b',
    },
    {
      label: 'Laboratorios Activos',
      value: laboratorios.length.toString(),
      icon: <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="4" y="6" width="16" height="12" rx="2" fill="#06b6d4"/><path d="M7 10h10M7 13h7" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>,
      bgColor: '#cffafe',
      iconColor: '#06b6d4',
    },
    {
      label: 'Secciones Activas',
      value: secciones.length.toString(),
      icon: <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="4" y="6" width="16" height="12" rx="2" fill="#f59e42"/><path d="M7 10h10M7 13h7" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>,
      bgColor: '#fef3c7',
      iconColor: '#f59e42',
    },
  ]

  // Función para renderizar contenido según la vista activa
  const renderContent = () => {
    // Vista: PRODUCTOS
    if (activeView === 'productos') {
      return (
        <div className="dashboard-grid">
          {/* Columna izquierda: tabla de productos */}
          <div className="dashboard-column">
            <div className="productos-view">
              <div className="section-header">
                <h2>🌿 Productos Naturistas</h2>
                {can('productos', 'create') && (
                  <button className="add-btn" onClick={() => setProductModalOpen(true)}>+ Nuevo Producto</button>
                )}
              </div>
              <div className="section-toolbar">
                <div className="search-bar">
                  <input
                    type="search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Buscar por nombre, ej. 'Moringa', 'Manzanilla'"
                  />
                </div>
                <div className="filters">
                  <select value={seccionId ?? ''} onChange={(e) => setSeccionId(e.target.value ? Number(e.target.value) : undefined)}>
                    <option value="">Sección (todas)</option>
                    {secciones.map(s => (
                      <option key={s.id_seccion} value={s.id_seccion}>{s.nombre_seccion}</option>
                    ))}
                  </select>
                  <select value={laboratorioId ?? ''} onChange={(e) => setLaboratorioId(e.target.value ? Number(e.target.value) : undefined)}>
                    <option value="">Laboratorio (todos)</option>
                    {laboratorios.map(l => (
                      <option key={l.id_laboratorio} value={l.id_laboratorio}>{l.nombre_laboratorio}</option>
                    ))}
                  </select>
                  <label className="toggle-stock-bajo">
                    <input type="checkbox" checked={soloStockBajo} onChange={(e) => setSoloStockBajo(e.target.checked)} />
                    <span>Solo stock bajo</span>
                  </label>
                </div>
              </div>
              {productsLoading ? (
                <p>Cargando productos...</p>
              ) : visibleProductos.length > 0 ? (
                <div className="products-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Stock</th>
                        <th>Precio</th>
                        <th>Total</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visibleProductos.map((producto) => {
                        const isLowStock = producto.cantidad <= 5
                        const total = producto.precio * producto.cantidad
                        return (
                          <tr key={producto.id} className={isLowStock ? 'low-stock-row' : ''}>
                            <td>{producto.nombre}</td>
                            <td className={isLowStock ? 'stock-alert' : ''}>{producto.cantidad}</td>
                            <td>${producto.precio.toFixed(2)}</td>
                            <td>${total.toFixed(2)}</td>
                            <td>
                              {isLowStock ? (
                                <span className="badge badge-warning">⚠️ Stock Bajo</span>
                              ) : (
                                <span className="badge badge-success">✓ Disponible</span>
                              )}
                            </td>
                            <td className="actions">
                              <button
                                className="btn-edit"
                                title="Editar"
                                onClick={() => {
                                  setEditingProduct(producto)
                                  setEditModalOpen(true)
                                }}
                              >
                                ✏️
                              </button>
                              <button
                                className="btn-delete"
                                title="Eliminar"
                                onClick={() => {
                                  setDeletingId(producto.id)
                                  setDeleteModalOpen(true)
                                }}
                              >
                                🗑️
                              </button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  <p>🌱 No hay productos registrados</p>
                  <button className="add-btn">+ Agregar primer producto</button>
                </div>
              )}
            </div>
          </div>
          {/* Columna derecha: panel de detalles/formulario */}
          <div className="dashboard-column">
            {/* Aquí puedes renderizar el panel de detalles, formulario, preview, etc. */}
            {isEditModalOpen && editingProduct ? (
              <Modal
                isOpen={isEditModalOpen}
                onClose={() => setEditModalOpen(false)}
                title="Editar Producto"
                width={720}
              >
                <ProductForm
                  initialValues={editingProduct}
                  loading={updateProduct.isPending}
                  onCancel={() => setEditModalOpen(false)}
                  onSubmit={async (values) => {
                    try {
                      await updateProduct.mutateAsync({ id: editingProduct.id, data: values })
                      setEditModalOpen(false)
                      setEditingProduct(null)
                      setActiveView('productos')
                      setToast({ message: 'Producto actualizado con éxito', type: 'success' })
                    } catch (e: any) {
                      const msg = e?.response?.data?.detail || e?.message || 'Error al actualizar producto'
                      setToast({ message: msg, type: 'error' })
                    } finally {
                      setTimeout(() => setToast(null), 2500)
                    }
                  }}
                />
              </Modal>
            ) : (
              <div className="info-card">
                <p>Selecciona un producto para ver detalles o editar.</p>
              </div>
            )}
          </div>
        </div>
      )
    }

    // Vista: ENTRADAS (Pedidos/Compras)
    if (activeView === 'entradas') {
      return (
        <div className="entradas-view">
          <div className="section-header">
            <h2>📥 Entradas de Inventario</h2>
            {can('entradas', 'create') && (
              <button className="add-btn" onClick={() => setEntradaModalOpen(true)}>+ Nueva Entrada</button>
            )}
          </div>
          <div className="section-toolbar">
            <div className="filters">
              <select value={entradasMonth} onChange={(e) => setEntradasMonth(Number(e.target.value))}>
                {Array.from({ length: 12 }).map((_, idx) => (
                  <option key={idx + 1} value={idx + 1}>Mes {idx + 1}</option>
                ))}
              </select>
              <select value={entradasYear} onChange={(e) => setEntradasYear(Number(e.target.value))}>
                {yearOptions.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="stats-mini">
            <div className="stat-mini-card">
              <span className="stat-mini-label">Compras Mensuales</span>
              <span className="stat-mini-value">${(entradasMes?.total_compras ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Compras Anuales</span>
              <span className="stat-mini-value">${(entradasAnio?.total_compras ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Unidades Recibidas (mes)</span>
              <span className="stat-mini-value">{entradasMes?.total_unidades ?? 0}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label"># Entradas (mes)</span>
              <span className="stat-mini-value">{entradasMes?.cantidad_entradas ?? 0}</span>
            </div>
          </div>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Lote</th>
                  <th>Cantidad</th>
                  <th>Proveedor</th>
                  <th>Costo</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {entradasLista.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center">No hay registros de entradas</td>
                  </tr>
                ) : (
                  entradasLista.map((e: any) => (
                    <tr key={e.id_entrada}>
                      <td>{new Date(e.fecha_entrada).toLocaleDateString()}</td>
                      <td>#{e.id_lote}</td>
                      <td>{e.cantidad}</td>
                      <td>{e.proveedor ?? '-'}</td>
                      <td>${(e.precio_compra_unitario ?? 0).toFixed(2)}</td>
                      <td>${(e.precio_compra_total ?? 0).toFixed(2)}</td>
                      <td>-</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )
    }

    // Vista: VENTAS
    if (activeView === 'ventas') {
      return (
        <div className="ventas-view">
          <div className="section-header">
            <h2>💰 Registro de Ventas</h2>
            {can('ventas', 'create') && (
              <button className="add-btn" onClick={() => setVentaModalOpen(true)}>+ Nueva Venta</button>
            )}
          </div>
          <div className="section-toolbar">
            <div className="filters">
              <select value={ventasMonth} onChange={(e) => setVentasMonth(Number(e.target.value))}>
                {Array.from({ length: 12 }).map((_, idx) => (
                  <option key={idx + 1} value={idx + 1}>Mes {idx + 1}</option>
                ))}
              </select>
              <select value={ventasYear} onChange={(e) => setVentasYear(Number(e.target.value))}>
                {yearOptions.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="stats-mini">
            <div className="stat-mini-card">
              <span className="stat-mini-label">Ventas Mensuales</span>
              <span className="stat-mini-value">${(ventasMes?.total_ventas ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Ventas Anuales</span>
              <span className="stat-mini-value">${(ventasAnio?.total_ventas ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Promedio Ticket (mes)</span>
              <span className="stat-mini-value">${(ventasMes?.promedio_venta ?? 0).toFixed(2)}</span>
            </div>
          </div>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Total</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {ventasLista.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="text-center">No hay registros de ventas</td>
                  </tr>
                ) : (
                  ventasLista.map((v) => (
                    <tr key={v.id_venta}>
                      <td>{new Date(v.fecha_venta).toLocaleDateString()}</td>
                      <td>{v.cliente}</td>
                      <td>${v.total.toFixed(2)}</td>
                      <td>{v.estado}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )
    }

    // Vista: GASTOS
    if (activeView === 'gastos') {
      return (
        <div className="gastos-view">
          <div className="section-header">
            <h2>💸 Control de Gastos</h2>
            {can('gastos', 'create') && (
              <button className="add-btn" onClick={() => setGastoModalOpen(true)}>+ Nuevo Gasto</button>
            )}
          </div>
          <div className="section-toolbar">
            <div className="filters">
              <select value={gastosMonth} onChange={(e) => setGastosMonth(Number(e.target.value))}>
                {Array.from({ length: 12 }).map((_, idx) => (
                  <option key={idx + 1} value={idx + 1}>Mes {idx + 1}</option>
                ))}
              </select>
              <select value={gastosYear} onChange={(e) => setGastosYear(Number(e.target.value))}>
                {yearOptions.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="stats-mini">
            <div className="stat-mini-card">
              <span className="stat-mini-label">Gastos Mensuales</span>
              <span className="stat-mini-value">${(gastosMes?.total_gastos ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Gastos Anuales</span>
              <span className="stat-mini-value">${(gastosAnio?.total_gastos ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label"># Registros (mes)</span>
              <span className="stat-mini-value">{gastosMes?.cantidad_gastos ?? 0}</span>
            </div>
          </div>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Concepto</th>
                  <th>Categoría</th>
                  <th>Monto</th>
                  <th>Método Pago</th>
                </tr>
              </thead>
              <tbody>
                {gastosLista.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center">No hay registros de gastos</td>
                  </tr>
                ) : (
                  gastosLista.map((g) => (
                    <tr key={g.id_gasto}>
                      <td>{new Date(g.fecha_gasto).toLocaleDateString()}</td>
                      <td>{g.concepto}</td>
                      <td>{g.categoria}</td>
                      <td>${g.monto.toFixed(2)}</td>
                      <td>{g.metodo_pago ?? '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )
    }

    // Vista: COTIZACIÓN
    if (activeView === 'cotizacion') {
      return (
        <div className="cotizacion-view">
          <div className="section-header">
            <h2>📋 Cotizaciones</h2>
            {can('cotizaciones', 'create') && (
              <button className="add-btn" onClick={() => setCotizacionModalOpen(true)}>+ Nueva Cotización</button>
            )}
          </div>
          <div className="stats-mini">
            <div className="stat-mini-card">
              <span className="stat-mini-label">Total Cotizaciones</span>
              <span className="stat-mini-value">{cotizacionesStats?.total_cotizaciones ?? 0}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Monto Cotizado</span>
              <span className="stat-mini-value">${(cotizacionesStats?.total_monto_cotizado ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Pendientes</span>
              <span className="stat-mini-value">{cotizacionesStats?.cotizaciones_pendientes ?? 0}</span>
            </div>
            <div className="stat-mini-card">
              <span className="stat-mini-label">Tasa Conversión</span>
              <span className="stat-mini-value">{((cotizacionesStats?.tasa_conversion ?? 0) * 100).toFixed(1)}%</span>
            </div>
          </div>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>N° Cotización</th>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {cotizacionesLista.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center">No hay cotizaciones registradas</td>
                  </tr>
                ) : (
                  cotizacionesLista.map((cot) => (
                    <tr key={cot.id_cotizacion}>
                      <td>{cot.numero_cotizacion}</td>
                      <td>{new Date(cot.fecha_cotizacion).toLocaleDateString()}</td>
                      <td>Cliente #{cot.id_cliente}</td>
                      <td>${cot.total.toFixed(2)}</td>
                      <td>
                        <span className={`badge ${cot.estado === 'Pendiente' ? 'badge-warning' : cot.estado === 'Aprobada' ? 'badge-success' : 'badge-error'}`}>
                          {cot.estado}
                        </span>
                      </td>
                      <td>
                        {cot.estado === 'Aprobada' && (
                          <button
                            className="btn-primary"
                            style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem' }}
                            onClick={async () => {
                              try {
                                await convertirCotizacion.mutateAsync(cot.id_cotizacion)
                                setToast({ message: 'Cotización convertida a venta', type: 'success' })
                              } catch (e: any) {
                                setToast({ message: e?.response?.data?.detail || 'Error al convertir', type: 'error' })
                              } finally {
                                setTimeout(() => setToast(null), 2500)
                              }
                            }}
                          >
                            Convertir a Venta
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )
    }

    // Vista: DEVOLUCIONES
    if (activeView === 'devoluciones') {
      return (
        <div className="devoluciones-view">
          <div className="section-header">
            <h2>↩️ Devoluciones</h2>
            <button className="add-btn">+ Nueva Devolución</button>
          </div>
          <div className="info-card">
            <p>Registra las devoluciones de productos (clientes o proveedores)</p>
          </div>
          <div className="products-table">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Cliente/Proveedor</th>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Motivo</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan={7} className="text-center">No hay registros de devoluciones</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )
    }

    // Vista: ADMINISTRACI�N  
    if (activeView === 'admin') {
      return <AdminPanelPage />
    }

    // Vista por defecto: Panel de control
    return (
      <>
        {/* Layout de 2 columnas */}
        <div className="dashboard-grid">
          {/* Columna izquierda */}
          <div className="dashboard-column">
            <div className="dashboard-section">
              <h2>Panel de Control</h2>
              <div className="welcome-card">
                <div className="welcome-content">
                  <div className="welcome-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" fill="#2E8B57"/>
                      <path d="M8 12l2 2 4-4" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </div>
                  <div className="welcome-text">
                    <h3>¡Bienvenido, {user?.nombre}!</h3>
                    <p>Gestiona tu inventario de forma eficiente y profesional.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="dashboard-section">
              <div className="section-header">
                <h2>Actividad Reciente</h2>
              </div>
              <div className="activity-card">
                <div className="activity-item">
                  <div className="activity-icon">📦</div>
                  <div className="activity-text">
                    <p className="activity-title">Producto agregado</p>
                    <p className="activity-time">Hace 2 horas</p>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">✅</div>
                  <div className="activity-text">
                    <p className="activity-title">Venta realizada</p>
                    <p className="activity-time">Hace 4 horas</p>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">⚠️</div>
                  <div className="activity-text">
                    <p className="activity-title">Stock bajo detectado</p>
                    <p className="activity-time">Hace 1 día</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Columna derecha */}
          <div className="dashboard-column">
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Productos Destacados</h2>
                <button className="view-all-btn">Ver todos →</button>
              </div>
              {productsLoading ? (
                <p>Cargando productos...</p>
              ) : productos.length > 0 ? (
                <div className="products-list">
                  {productos.slice(0, 6).map((producto) => {
                    const isLowStock = producto.cantidad <= 5;
                    return (
                      <div key={producto.id} className={`product-card compact${isLowStock ? ' low-stock' : ''}`}>
                        <div className="product-card-header">
                          <span className="product-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                              <rect x="4" y="7" width="16" height="11" rx="2" fill="#2E8B57"/>
                              <rect x="7" y="4" width="10" height="3" rx="1.5" fill="#86c8bc"/>
                            </svg>
                          </span>
                          <h3>{producto.nombre}</h3>
                        </div>
                        <div className="product-info">
                          <span className={`cantidad${isLowStock ? ' alert' : ''}`}>
                            Stock: {producto.cantidad}
                            {isLowStock && <span className="alert-icon">⚠️</span>}
                          </span>
                          <span className="precio">${producto.precio}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p>No hay productos disponibles</p>
              )}
            </div>
          </div>
        </div>
      </>
    )
  }

  return (
    <div className={`dashboard-layout${sidebarExpanded ? ' sidebar-expanded' : ''}`}>
      <aside className={`sidebar${sidebarExpanded ? ' expanded' : ''}`}>
        <div className="sidebar-logo">
          <img src="/images/logo.png" alt="Logo" />
        </div>
  <nav className="sidebar-menu" role="navigation" aria-label="Menú principal">
          {sidebarMenu.map((item) => {
            // DEBUG: Ver qué está pasando con el menú admin
            if (item.id === 'admin') {
              console.log('🔍 Item admin encontrado:', {
                item,
                isAdmin: isAdmin(),
                user,
                requireAdmin: item.requireAdmin
              })
            }
            
            // Verificar permisos: si tiene permission y no tiene el permiso, no mostrar
            if (item.permission && !can(item.permission as any, 'read')) {
              return null
            }
            
            // Si requiere ser admin y no lo es, no mostrar
            if (item.requireAdmin && !isAdmin()) {
              console.log('❌ Usuario NO es admin, ocultando botón')
              return null
            }
            
            // Tooltip preview for Productos
            let tooltipContent: React.ReactNode = null
            if (item.id === 'productos') {
              tooltipContent = (
                <div className="sidebar-tooltip">
                  <div className="tooltip-title">Productos</div>
                  <div className="tooltip-count">Total: <b>{productos.length}</b></div>
                  {productos.length > 0 && (
                    <div className="tooltip-list">
                      {productos.slice(0,2).map(p => (
                        <div key={p.id} className="tooltip-product">
                          <span className="tp-name">{p.nombre}</span>
                          <span className="tp-stock">Stock: {p.cantidad}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            }
            return (
              <div
                key={item.label}
                className={`sidebar-item ${activeView === item.id ? 'active' : ''}`}
                title={item.label}
                onClick={() => {
                  // Si es el botón de admin, cambiar la vista a 'admin'
                  if (item.id === 'admin') {
                    setActiveView('admin')
                  } else {
                    setActiveView(item.id)
                  }
                }}
              >
                <span className="sidebar-icon" aria-hidden="true">{item.icon}</span>
                <span className="sidebar-label">{item.label}</span>
                {tooltipContent && (
                  <div className="sidebar-tooltip-container">
                    {tooltipContent}
                  </div>
                )}
              </div>
            )
          })}
        </nav>
      </aside>

      <div className={`dashboard-main-area${sidebarExpanded ? ' expanded' : ''}`}>
        <header className="dashboard-header">
          <div className="header-content">
            <div className="row" style={{ alignItems: 'center', gap: '.5rem' }}>
              {/* Botón hamburguesa para móvil */}
              <button
                className="sidebar-toggle-btn"
                aria-label={sidebarExpanded ? 'Contraer menú' : 'Expandir menú'}
                onClick={() => setSidebarExpanded(v => !v)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  border: '1px solid #e2e8f0',
                  background: '#fff',
                  cursor: 'pointer'
                }}
              >
                {/* ícono hamburguesa simple */}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path d="M4 7h16M4 12h16M4 17h16" stroke="#2E8B57" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
              <h1 style={{ margin: 0 }}>Sistema de Inventario</h1>
            </div>
            <div className="user-info">
              {/* Campana de notificaciones */}
              <div className="notification-bell-wrapper" style={{ position: 'relative', marginRight: '1rem' }}>
                <button 
                  className="notification-bell-btn" 
                  onClick={() => setIsNotificationPanelOpen(!isNotificationPanelOpen)}
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    cursor: 'pointer',
                    fontSize: '1.5rem',
                    position: 'relative'
                  }}
                  title="Notificaciones"
                >
                  🔔
                  {unreadCount > 0 && (
                    <span 
                      className="notification-badge"
                      style={{
                        position: 'absolute',
                        top: '-5px',
                        right: '-5px',
                        background: '#ef4444',
                        color: 'white',
                        borderRadius: '50%',
                        width: '18px',
                        height: '18px',
                        fontSize: '0.7rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold'
                      }}
                    >
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
              </div>
              <span className="user-name">
                {getRoleName() === 'admin' && '👑 '}
                {getRoleName() === 'gestor' && '� '}
                {getRoleName() === 'viewer' && '�️ '}
                {user?.nombre || 'Usuario'} ({getRoleName()})
              </span>
              {isAdmin() && (
                <button 
                  onClick={() => navigate('/admin')} 
                  className="admin-button"
                  style={{ 
                    marginRight: '0.5rem',
                    padding: '0.5rem 1rem',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  👑 Admin
                </button>
              )}
              <button onClick={handleLogout} className="logout-button">
                Cerrar Sesión
              </button>
            </div>
          </div>
        </header>

        <main className="dashboard-main">
          {/* Métricas: solo en Panel de Control */}
          {activeView === 'panel' && (
            <div className="metrics-row">
              {metrics.map((m) => (
                <div className="metric-card modern" key={m.label} style={{ backgroundColor: m.bgColor }}>
                  <div className="metric-icon-circle" style={{ backgroundColor: m.iconColor }}>
                    {m.icon}
                  </div>
                  <div className="metric-info">
                    <span className="metric-label">{m.label}</span>
                    <span className="metric-value">{m.value}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Contenido dinámico según vista activa */}
          {renderContent()}
        </main>

        {/* Modales globales */}
        <Modal
          isOpen={isProductModalOpen}
          onClose={() => setProductModalOpen(false)}
          title="Nuevo Producto"
          width={720}
        >
          <ProductForm
            loading={createProduct.isPending}
            onCancel={() => setProductModalOpen(false)}
            onSubmit={async (values) => {
              try {
                await createProduct.mutateAsync(values)
                setProductModalOpen(false)
                setActiveView('productos')
                setToast({ message: 'Producto guardado con éxito', type: 'success' })
              } catch (e: any) {
                const msg = e?.response?.data?.detail || e?.message || 'Error al crear producto'
                setToast({ message: msg, type: 'error' })
              } finally {
                setTimeout(() => setToast(null), 2500)
              }
            }}
          />
        </Modal>

        {/* Crear Venta */}
        <Modal isOpen={isVentaModalOpen} onClose={() => setVentaModalOpen(false)} title="Nueva Venta" width={820}>
          <VentaForm
            loading={createVenta.isPending}
            onCancel={() => setVentaModalOpen(false)}
            onSubmit={async (values) => {
              try {
                await createVenta.mutateAsync({
                  id_cliente: values.id_cliente,
                  metodo_pago: values.metodo_pago,
                  detalles: values.detalles.map(d => ({
                    id_lote: d.id_lote,
                    cantidad: d.cantidad,
                    precio_unitario: d.precio_unitario,
                  }))
                })
                setVentaModalOpen(false)
                setToast({ message: 'Venta registrada con éxito', type: 'success' })
              } catch (e: any) {
                const msg = e?.response?.data?.detail || e?.message || 'Error al crear venta'
                setToast({ message: msg, type: 'error' })
              } finally {
                setTimeout(() => setToast(null), 2500)
              }
            }}
          />
        </Modal>

        {/* Crear Gasto */}
        <Modal isOpen={isGastoModalOpen} onClose={() => setGastoModalOpen(false)} title="Nuevo Gasto" width={720}>
          <div className="form-grid">
            <div className="form-row">
              <label>Fecha</label>
              <input id="gasto-fecha" type="datetime-local" defaultValue={new Date().toISOString().slice(0,16)} />
            </div>
            <div className="form-row">
              <label>Concepto</label>
              <input id="gasto-concepto" type="text" />
            </div>
            <div className="form-row">
              <label>Categoría</label>
              <input id="gasto-categoria" type="text" defaultValue="Otros" />
            </div>
            <div className="form-row">
              <label>Monto</label>
              <input id="gasto-monto" type="number" min={0} step="0.01" />
            </div>
            <div className="form-row">
              <label>Método de pago</label>
              <input id="gasto-metodo" type="text" defaultValue="Efectivo" />
            </div>
            <div className="form-actions">
              <button className="add-btn" onClick={async () => {
                const fecha_gasto = (document.getElementById('gasto-fecha') as HTMLInputElement).value
                const concepto = (document.getElementById('gasto-concepto') as HTMLInputElement).value
                const categoria = (document.getElementById('gasto-categoria') as HTMLInputElement).value
                const monto = Number((document.getElementById('gasto-monto') as HTMLInputElement).value)
                const metodo_pago = (document.getElementById('gasto-metodo') as HTMLInputElement).value
                try {
                  await createGasto.mutateAsync({ fecha_gasto, concepto, categoria, monto, metodo_pago })
                  setGastoModalOpen(false)
                  setToast({ message: 'Gasto creado', type: 'success' })
                } catch (e: any) {
                  setToast({ message: e?.response?.data?.detail || e?.message || 'Error al crear gasto', type: 'error' })
                } finally {
                  setTimeout(() => setToast(null), 2500)
                }
              }}>Crear</button>
            </div>
          </div>
        </Modal>
        <Modal
          isOpen={isEntradaModalOpen}
          onClose={() => setEntradaModalOpen(false)}
          title="Registrar Entrada"
          width={720}
        >
          <EntradaForm
            loading={crearEntrada.isPending}
            onCancel={() => setEntradaModalOpen(false)}
            onSubmit={async (values) => {
              try {
                await crearEntrada.mutateAsync({
                  id_lote: values.id_lote,
                  cantidad: values.cantidad,
                  precio_compra_unitario: values.costo,
                  fecha_entrada: new Date(values.fecha).toISOString(),
                  proveedor: values.proveedor,
                  observaciones: values.observaciones,
                })
                setEntradaModalOpen(false)
                setToast({ message: 'Entrada registrada con éxito', type: 'success' })
              } catch (e: any) {
                const msg = e?.response?.data?.detail || e?.message || 'Error al registrar entrada'
                setToast({ message: msg, type: 'error' })
              } finally {
                setTimeout(() => setToast(null), 2500)
              }
            }}
          />
        </Modal>

        {/* Crear Cotización */}
        <Modal isOpen={isCotizacionModalOpen} onClose={() => setCotizacionModalOpen(false)} title="Nueva Cotización" width={720}>
          <div className="form-grid">
            <div className="form-row">
              <label>ID Cliente *</label>
              <input id="cot-id-cliente" type="number" min={1} defaultValue={1} />
            </div>
            <div className="form-row">
              <label>ID Producto *</label>
              <input id="cot-id-producto" type="number" min={1} />
            </div>
            <div className="form-row">
              <label>Cantidad *</label>
              <input id="cot-cantidad" type="number" min={1} defaultValue={1} />
            </div>
            <div className="form-row">
              <label>Precio Unitario *</label>
              <input id="cot-precio" type="number" min={0} step="0.01" defaultValue={0} />
            </div>
            <div className="form-row">
              <label>Descuento</label>
              <input id="cot-descuento" type="number" min={0} step="0.01" defaultValue={0} />
            </div>
            <div className="form-row">
              <label>Impuestos</label>
              <input id="cot-impuestos" type="number" min={0} step="0.01" defaultValue={0} />
            </div>
            <div className="form-row form-field-full">
              <label>Observaciones</label>
              <textarea id="cot-observaciones" rows={3} />
            </div>
            <div className="form-actions">
              <button className="btn-outline" onClick={() => setCotizacionModalOpen(false)}>Cancelar</button>
              <button className="add-btn" onClick={async () => {
                const id_cliente = Number((document.getElementById('cot-id-cliente') as HTMLInputElement).value)
                const id_producto = Number((document.getElementById('cot-id-producto') as HTMLInputElement).value)
                const cantidad = Number((document.getElementById('cot-cantidad') as HTMLInputElement).value)
                const precio_unitario = Number((document.getElementById('cot-precio') as HTMLInputElement).value)
                const descuento = Number((document.getElementById('cot-descuento') as HTMLInputElement).value)
                const impuestos = Number((document.getElementById('cot-impuestos') as HTMLInputElement).value)
                const observaciones = (document.getElementById('cot-observaciones') as HTMLTextAreaElement).value
                try {
                  await crearCotizacion.mutateAsync({
                    id_cliente,
                    descuento,
                    impuestos,
                    observaciones,
                    detalles: [{ id_producto, cantidad, precio_unitario }]
                  })
                  setCotizacionModalOpen(false)
                  setToast({ message: 'Cotización creada con éxito', type: 'success' })
                } catch (e: any) {
                  setToast({ message: e?.response?.data?.detail || e?.message || 'Error al crear cotización', type: 'error' })
                } finally {
                  setTimeout(() => setToast(null), 2500)
                }
              }}>Crear Cotización</button>
            </div>
          </div>
        </Modal>

        {/* Editar producto */}
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setEditModalOpen(false)}
          title="Editar Producto"
          width={720}
        >
          {editingProduct && (
            <ProductForm
              initialValues={editingProduct}
              loading={updateProduct.isPending}
              onCancel={() => setEditModalOpen(false)}
              onSubmit={async (values) => {
                try {
                  await updateProduct.mutateAsync({ id: editingProduct.id, data: values })
                  setEditModalOpen(false)
                  setEditingProduct(null)
                  setActiveView('productos')
                  setToast({ message: 'Producto actualizado con éxito', type: 'success' })
                } catch (e: any) {
                  const msg = e?.response?.data?.detail || e?.message || 'Error al actualizar producto'
                  setToast({ message: msg, type: 'error' })
                } finally {
                  setTimeout(() => setToast(null), 2500)
                }
              }}
            />
          )}
        </Modal>

        {/* Confirmar eliminación */}
        <Modal
          isOpen={isDeleteModalOpen}
          onClose={() => setDeleteModalOpen(false)}
          title="Confirmar eliminación"
          width={520}
        >
          <div className="confirm-body">
            <p>¿Seguro que deseas eliminar este producto? Esta acción no se puede deshacer.</p>
            <div className="confirm-actions">
              <button className="btn-outline" onClick={() => setDeleteModalOpen(false)}>Cancelar</button>
              <button
                className="btn-danger"
                onClick={async () => {
                  try {
                    if (deletingId != null) {
                      await deleteProduct.mutateAsync(deletingId)
                    }
                    setToast({ message: 'Producto eliminado con éxito', type: 'success' })
                  } catch (e: any) {
                    const msg = e?.response?.data?.detail || e?.message || 'Error al eliminar producto'
                    setToast({ message: msg, type: 'error' })
                  } finally {
                    setDeleteModalOpen(false)
                    setDeletingId(null)
                    setTimeout(() => setToast(null), 2500)
                  }
                }}
                disabled={deleteProduct.isPending}
              >
                {deleteProduct.isPending ? 'Eliminando…' : 'Eliminar'}
              </button>
            </div>
          </div>
        </Modal>
      </div>
      {toast && (
        <div className={`toast ${toast.type === 'error' ? 'toast-error' : 'toast-success'}`}>{toast.message}</div>
      )}

      {/* Panel de notificaciones en tiempo real - solo si está abierto */}
      {isNotificationPanelOpen && (
        <NotificationPanel onClose={() => setIsNotificationPanelOpen(false)} />
      )}
    </div>
  )
}

