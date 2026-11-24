import type { NodeFieldDef } from '@/stores/nodeSchema'

export const manualScene = '按角色选择五张图'
export function inputMode(data: Record<string, any>, hasUpstream = false) {
  return data.input_type || (data.key || hasUpstream ? 'auto' : manualScene)
}
export function visibleField(type: string | undefined, field: NodeFieldDef, mode: string) {
  if (type !== 'uav_multispectral') return true
  if (field.widget === 'tiff-role') return mode === manualScene
  return field.key !== 'key' || mode !== manualScene
}
export function roleError(fields: NodeFieldDef[], data: Record<string, any>) {
  const seen = new Set<string>()
  for (const f of fields.filter(f => f.widget === 'tiff-role')) {
    const key = data[f.key]
    if (!key || !/\.tiff?$/i.test(key)) return `请为${f.label}选择一张 TIFF`
    if (seen.has(key)) return `${f.label}与其他角色不能使用同一张图片`
    seen.add(key)
  }
  return ''
}
