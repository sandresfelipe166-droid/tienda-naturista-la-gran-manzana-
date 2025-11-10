// Módulo IndexedDB básico para cachear datos de lectura
// Responsable de: abrir DB, crear object stores y exponer helpers CRUD simples.
const DB_NAME = 'inventario_offline';
const DB_VERSION = 1;
function openDB() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains('productos')) {
                db.createObjectStore('productos', { keyPath: 'id' });
            }
        };
        req.onsuccess = () => resolve({ db: req.result });
        req.onerror = () => reject(req.error);
    });
}
async function getStore(store, mode = 'readonly') {
    const { db } = await openDB();
    const tx = db.transaction(store, mode);
    return tx.objectStore(store);
}
export async function putAll(store, items) {
    const os = await getStore(store, 'readwrite');
    await Promise.all(items.map(item => new Promise((resolve, reject) => {
        const r = os.put(item);
        r.onsuccess = () => resolve();
        r.onerror = () => reject(r.error);
    })));
}
export async function getAll(store) {
    const os = await getStore(store);
    return new Promise((resolve, reject) => {
        const r = os.getAll();
        r.onsuccess = () => resolve(r.result);
        r.onerror = () => reject(r.error);
    });
}
export async function clearStore(store) {
    const os = await getStore(store, 'readwrite');
    return new Promise((resolve, reject) => {
        const r = os.clear();
        r.onsuccess = () => resolve(undefined);
        r.onerror = () => reject(r.error);
    });
}
export async function upsert(store, item) {
    const os = await getStore(store, 'readwrite');
    return new Promise((resolve, reject) => {
        const r = os.put(item);
        r.onsuccess = () => resolve(undefined);
        r.onerror = () => reject(r.error);
    });
}
export async function remove(store, id) {
    const os = await getStore(store, 'readwrite');
    return new Promise((resolve, reject) => {
        const r = os.delete(id);
        r.onsuccess = () => resolve(undefined);
        r.onerror = () => reject(r.error);
    });
}
export function isIndexedDBAvailable() {
    return typeof indexedDB !== 'undefined';
}
