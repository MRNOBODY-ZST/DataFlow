import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import http from '@/api/http'

export interface WidgetConfig {
  keyPlaceholder?: string
  valuePlaceholder?: string
  valueType?: string
  valueOptions?: string[]
}

export interface NodeFieldDef {
  key: string
  label: string
  type: 'text' | 'number' | 'textarea' | 'select' | 'file-picker'
  placeholder: string
  required: boolean
  autoFilled: boolean
  options?: string[] | null
  widget?: string | null
  widgetConfig?: WidgetConfig | null
}

export interface NodeSchema {
  type: string
  label: string
  category: 'readers' | 'transforms' | 'media' | 'writers'
  icon: string
  fields: NodeFieldDef[]
}

export const useNodeSchemaStore = defineStore('nodeSchema', () => {
  const schemas = ref<NodeSchema[]>([])
  const loading = ref(false)

  const byType = computed<Record<string, NodeSchema>>(() =>
    Object.fromEntries(schemas.value.map((schema) => [schema.type, schema])),
  )

  const byCategory = computed<Record<string, NodeSchema[]>>(() => {
    const grouped: Record<string, NodeSchema[]> = {}
    for (const schema of schemas.value) {
      const items = grouped[schema.category] ?? (grouped[schema.category] = [])
      items.push(schema)
    }
    return grouped
  })

  async function fetch() {
    if (loading.value || schemas.value.length > 0) return
    loading.value = true
    try {
      const { data } = await http.get<NodeSchema[]>('/nodes/schema')
      schemas.value = data
    } finally {
      loading.value = false
    }
  }

  return { schemas, loading, byType, byCategory, fetch }
})
