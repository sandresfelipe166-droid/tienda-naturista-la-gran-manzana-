/// <reference types="vite/client" />

// Optional: extend env typing if you want stricter checks
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_API_V1?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
