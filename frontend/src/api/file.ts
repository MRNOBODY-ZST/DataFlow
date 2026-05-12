import http from './http'

export const fileApi = {
  presignUpload: (filename: string): Promise<{ url: string; key: string }> =>
    http.post('/files/presign-upload', null, { params: { filename } }).then((r) => r.data),

  presignDownload: (key: string, bucket = 'output'): Promise<{ url: string }> =>
    http.get('/files/presign-download', { params: { key, bucket } }).then((r) => r.data),

  uploadToMinio: (presignedUrl: string, file: File, onProgress?: (pct: number) => void) =>
    fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
    }),
}
