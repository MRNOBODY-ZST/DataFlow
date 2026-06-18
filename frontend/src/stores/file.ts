import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fileApi, type FileBucket, type FileMetadata } from '@/api/file'

export const useFileStore = defineStore('file', () => {
  const activeBucket = ref<FileBucket>('input')
  const filesByBucket = ref<Record<FileBucket, FileMetadata[]>>({
    input: [],
    output: [],
    temp: [],
  })
  const loading = ref(false)
  const selectedFile = ref<FileMetadata | null>(null)
  const uploadProgress = ref(0)

  const files = computed(() => filesByBucket.value[activeBucket.value])

  async function fetchFiles(bucket: FileBucket = activeBucket.value, prefix = '') {
    loading.value = true
    try {
      filesByBucket.value[bucket] = await fileApi.listFiles(bucket, prefix)
    } finally {
      loading.value = false
    }
  }

  async function deleteFile(bucket: FileBucket, key: string) {
    await fileApi.deleteFile(bucket, key)
    filesByBucket.value[bucket] = filesByBucket.value[bucket].filter((file) => file.key !== key)
  }

  function setBucket(bucket: FileBucket) {
    activeBucket.value = bucket
  }

  function setSelectedFile(file: FileMetadata | null) {
    selectedFile.value = file
  }

  function resetUploadProgress() {
    uploadProgress.value = 0
  }

  return {
    activeBucket,
    filesByBucket,
    files,
    loading,
    selectedFile,
    uploadProgress,
    fetchFiles,
    deleteFile,
    setBucket,
    setSelectedFile,
    resetUploadProgress,
  }
})
