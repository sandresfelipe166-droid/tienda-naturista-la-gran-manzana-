// Módulo IndexedDB básico para cachear datos de lectura
// Responsable de: abrir DB, crear object stores y exponer helpers CRUD simples.

const DB_NAME = 'inventario_offline'
const DB_VERSION = 1

// Stores planificados
// productos: lista de productos
// metas: otras colecciones futuras (alertas, secciones, laboratorios)

export type StoreName = 'productos'

interface IDBOpenResult {
  db: IDBDatabase
}

function openDB(): Promise<IDBOpenResult> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains('productos')) {
        db.createObjectStore('productos', { keyPath: 'id' })
      }
    }
    req.onsuccess = () => resolve({ db: req.result })
    req.onerror = () => reject(req.error)
  })
}

async function getStore(store: StoreName, mode: IDBTransactionMode = 'readonly') {
  const { db } = await openDB()
  const tx = db.transaction(store, mode)
  return tx.objectStore(store)
}

export async function putAll<T extends { id: number }>(store: StoreName, items: T[]): Promise<void> {
  const os = await getStore(store, 'readwrite')
  await Promise.all(items.map(item => new Promise<void>((resolve, reject) => {
    const r = os.put(item)
    r.onsuccess = () => resolve()
    r.onerror = () => reject(r.error)
  })))
}

export async function getAll<T>(store: StoreName): Promise<T[]> {
  const os = await getStore(store)
  return new Promise((resolve, reject) => {
    const r = os.getAll()
    r.onsuccess = () => resolve(r.result as T[])
    r.onerror = () => reject(r.error)
  })
}

export async function clearStore(store: StoreName): Promise<void> {
  const os = await getStore(store, 'readwrite')
  return new Promise((resolve, reject) => {
    const r = os.clear()
    r.onsuccess = () => resolve(undefined)
    r.onerror = () => reject(r.error)
  })
}

export async function upsert<T extends { id: number }>(store: StoreName, item: T): Promise<void> {
  const os = await getStore(store, 'readwrite')
  return new Promise((resolve, reject) => {
    const r = os.put(item)
    r.onsuccess = () => resolve(undefined)
    r.onerror = () => reject(r.error)
  })
}

export async function remove(store: StoreName, id: number): Promise<void> {
  const os = await getStore(store, 'readwrite')
  return new Promise((resolve, reject) => {
    const r = os.delete(id)
    r.onsuccess = () => resolve(undefined)
    r.onerror = () => reject(r.error)
  })
}

export function isIndexedDBAvailable(): boolean {
  return typeof indexedDB !== 'undefined'
}
