// Cola de mutaciones offline: almacena operaciones cuando no hay conexión y las reintenta.
// Estrategia: guardar en localStorage para simplicidad inicial; futuro: mover a IndexedDB si crece.
const OUTBOX_KEY = 'inventario_outbox_v1';
const MAX_RETRIES = 5;
function load() {
    try {
        const raw = localStorage.getItem(OUTBOX_KEY);
        if (!raw)
            return [];
        return JSON.parse(raw);
    }
    catch {
        return [];
    }
}
function save(entries) {
    localStorage.setItem(OUTBOX_KEY, JSON.stringify(entries));
}
export function enqueue(method, url, body) {
    const entries = load();
    entries.push({ id: crypto.randomUUID(), method, url, body, createdAt: Date.now(), retries: 0 });
    save(entries);
}
export function listOutbox() {
    return load();
}
export async function flush(token) {
    const entries = load();
    if (entries.length === 0)
        return;
    const remaining = [];
    for (const entry of entries) {
        try {
            const res = await fetch(entry.url, {
                method: entry.method,
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: entry.body ? JSON.stringify(entry.body) : undefined,
            });
            if (!res.ok) {
                throw new Error('Respuesta no OK');
            }
            // Éxito: no re-agregar
        }
        catch (e) {
            const retries = entry.retries + 1;
            if (retries < MAX_RETRIES) {
                remaining.push({ ...entry, retries });
            }
            else {
                console.warn('Descartando mutación tras reintentos fallidos', entry);
            }
        }
    }
    save(remaining);
}
export function hasPending() {
    return load().length > 0;
}
