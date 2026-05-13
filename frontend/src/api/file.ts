import http from './http'

export type FileBucket = 'input' | 'output' | 'temp'

export interface FileMetadata {
  key: string
  size: number
  lastModified: string
  bucket: FileBucket
}

export const fileApi = {
  presignUpload: (filename: string): Promise<{ url: string; key: string }> =>
    http.post('/files/presign-upload', null, { params: { filename } }).then((r) => r.data),

  presignDownload: (key: string, bucket: FileBucket = 'output'): Promise<{ url: string }> =>
    http.get('/files/presign-download', { params: { key, bucket } }).then((r) => r.data),

  listFiles: (bucket: FileBucket, prefix = ''): Promise<FileMetadata[]> =>
    http.get('/files', { params: { bucket, prefix } }).then((r) => r.data),

  statFile: (bucket: FileBucket, key: string): Promise<FileMetadata> =>
    http.get('/files/stat', { params: { bucket, key } }).then((r) => r.data),

  deleteFile: (bucket: FileBucket, key: string): Promise<void> =>
    http.delete('/files', { params: { bucket, key } }).then(() => undefined),

  uploadToMinio: (presignedUrl: string, file: File, onProgress?: (pct: number) => void) =>
    new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('PUT', presignedUrl)
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream')
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      })
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve()
          return
        }
        reject(new Error(`Upload failed: ${xhr.status}`))
      }
      xhr.onerror = () => reject(new Error('Upload network error'))
      xhr.send(file)
    }),
}
