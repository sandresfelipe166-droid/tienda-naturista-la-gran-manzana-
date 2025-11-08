export function unwrapApi(payload) {
    const maybe = payload;
    if (typeof maybe === 'object' && maybe !== null && 'success' in maybe) {
        // It's an ApiResponse
        if (maybe.success && typeof maybe.data !== 'undefined')
            return maybe.data;
        // If backend returned plain T in data, or directly T, fallback
        return maybe.data ?? maybe;
    }
    return payload;
}
