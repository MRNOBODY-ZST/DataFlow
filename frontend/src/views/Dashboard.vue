<template>
  <AppLayout :title="t('dashboard.title')">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <!-- Stats with shared borders -->
      <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('dashboard.overview') }}</h3>
      <dl class="mt-5 grid grid-cols-1 divide-gray-200 overflow-hidden rounded-lg bg-white shadow-sm md:grid-cols-4 md:divide-x md:divide-y-0 dark:divide-white/10 dark:bg-gray-800/75 dark:shadow-none dark:inset-ring dark:inset-ring-white/10">
        <div v-for="item in stats" :key="item.name" class="px-4 py-5 sm:p-6">
          <dt class="text-base font-normal text-gray-900 dark:text-gray-100">{{ item.name }}</dt>
          <dd class="mt-1 flex items-baseline justify-between md:block lg:flex">
            <div class="flex items-baseline text-2xl font-semibold text-indigo-600 dark:text-indigo-400">
              {{ item.stat }}
            </div>
            <div :class="[item.changeType === 'increase' ? 'bg-green-100 text-green-800 dark:bg-green-400/10 dark:text-green-400' : item.changeType === 'decrease' ? 'bg-red-100 text-red-800 dark:bg-red-400/10 dark:text-red-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-400/10 dark:text-gray-400', 'inline-flex items-baseline rounded-full px-2.5 py-0.5 text-sm font-medium md:mt-2 lg:mt-0']">
              <ArrowUpIcon v-if="item.changeType === 'increase'" class="mr-0.5 -ml-1 size-5 shrink-0 self-center text-green-500 dark:text-green-400" aria-hidden="true" />
              <ArrowDownIcon v-else-if="item.changeType === 'decrease'" class="mr-0.5 -ml-1 size-5 shrink-0 self-center text-red-500 dark:text-red-400" aria-hidden="true" />
              {{ item.change }}
            </div>
          </dd>
        </div>
      </dl>

      <!-- Bento Grid with ECharts -->
      <div class="mt-10">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('dashboard.statistics') }}</h3>
        <div class="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-6 lg:grid-rows-2">
          <!-- Task Runs - large card -->
          <div class="flex p-px lg:col-span-4">
            <div class="w-full overflow-hidden rounded-lg bg-white shadow-sm outline outline-black/5 max-lg:rounded-t-4xl lg:rounded-tl-4xl dark:bg-gray-800 dark:shadow-none dark:outline-white/15">
              <div class="p-6">
                <h4 class="text-sm/4 font-semibold text-gray-500 dark:text-gray-400">{{ t('dashboard.taskRuns') }}</h4>
                <p class="mt-2 text-lg font-medium tracking-tight text-gray-900 dark:text-white">{{ t('dashboard.recentHistory') }}</p>
                <div ref="taskRunsEl" class="mt-4 h-64 w-full"></div>
              </div>
            </div>
          </div>
          <!-- Task Status - small card -->
          <div class="flex p-px lg:col-span-2">
            <div class="w-full overflow-hidden rounded-lg bg-white shadow-sm outline outline-black/5 lg:rounded-tr-4xl dark:bg-gray-800 dark:shadow-none dark:outline-white/15">
              <div class="p-6">
                <h4 class="text-sm/4 font-semibold text-gray-500 dark:text-gray-400">{{ t('dashboard.taskStatus') }}</h4>
                <p class="mt-2 text-lg font-medium tracking-tight text-gray-900 dark:text-white">{{ t('dashboard.distribution') }}</p>
                <div ref="statusPieEl" class="mt-4 h-64 w-full"></div>
              </div>
            </div>
          </div>
          <!-- Storage usage - small card -->
          <div class="flex p-px lg:col-span-2">
            <div class="w-full overflow-hidden rounded-lg bg-white shadow-sm outline outline-black/5 lg:rounded-bl-4xl dark:bg-gray-800 dark:shadow-none dark:outline-white/15">
              <div class="p-6">
                <h4 class="text-sm/4 font-semibold text-gray-500 dark:text-gray-400">{{ t('dashboard.storage') }}</h4>
                <p class="mt-2 text-lg font-medium tracking-tight text-gray-900 dark:text-white">{{ t('dashboard.bucketUsage') }}</p>
                <div ref="storageEl" class="mt-4 h-64 w-full"></div>
              </div>
            </div>
          </div>
          <!-- Recent activity - large card -->
          <div class="flex p-px lg:col-span-4">
            <div class="w-full overflow-hidden rounded-lg bg-white shadow-sm outline outline-black/5 max-lg:rounded-b-4xl lg:rounded-br-4xl dark:bg-gray-800 dark:shadow-none dark:outline-white/15">
              <div class="p-6">
                <h4 class="text-sm/4 font-semibold text-gray-500 dark:text-gray-400">{{ t('dashboard.pipelineActivity') }}</h4>
                <p class="mt-2 text-lg font-medium tracking-tight text-gray-900 dark:text-white">{{ t('dashboard.recentPipelines') }}</p>
                <div class="mt-4">
                  <div v-if="pipelineStore.loading" class="py-8 text-center text-sm text-gray-500">{{ t('common.loading') }}</div>
                  <div v-else-if="pipelineStore.pipelines.length === 0" class="py-8 text-center">
                    <FolderPlusIcon class="mx-auto size-10 text-gray-400" />
                    <p class="mt-2 text-sm text-gray-500">{{ t('dashboard.noPipelines') }}</p>
                    <button type="button" class="mt-4 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="router.push('/pipelines')">{{ t('dashboard.createPipeline') }}</button>
                  </div>
                  <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-white/10">
                    <li v-for="pipeline in pipelineStore.pipelines.slice(0, 5)" :key="pipeline.id" class="flex items-center justify-between gap-4 py-3">
                      <div class="min-w-0">
                        <p class="truncate text-sm font-semibold text-gray-900 dark:text-white">{{ pipeline.name }}</p>
                        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ pipeline.description || t('dashboard.noDescription') }} · {{ new Date(pipeline.updatedAt).toLocaleString() }}</p>
                      </div>
                      <button type="button" class="shrink-0 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="router.push(`/editor/${pipeline.id}`)">{{ t('common.edit') }}</button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/20/solid'
import { FolderPlusIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/layout/AppLayout.vue'
import { usePipelineStore } from '@/stores/pipeline'
import { useTaskStore } from '@/stores/task'
import { useFileStore } from '@/stores/file'

echarts.use([CanvasRenderer, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

const { t } = useI18n()
const router = useRouter()
const pipelineStore = usePipelineStore()
const taskStore = useTaskStore()
const fileStore = useFileStore()

const taskRunsEl = ref<HTMLElement | null>(null)
const statusPieEl = ref<HTMLElement | null>(null)
const storageEl = ref<HTMLElement | null>(null)

const taskRunsChart = shallowRef<echarts.ECharts | null>(null)
const statusPieChart = shallowRef<echarts.ECharts | null>(null)
const storageChart = shallowRef<echarts.ECharts | null>(null)

onMounted(async () => {
  await Promise.all([
    pipelineStore.fetchAll(),
    taskStore.fetchAll(),
    fileStore.fetchFiles('input'),
    fileStore.fetchFiles('output'),
  ])
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  taskRunsChart.value?.dispose()
  statusPieChart.value?.dispose()
  storageChart.value?.dispose()
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  taskRunsChart.value?.resize()
  statusPieChart.value?.resize()
  storageChart.value?.resize()
}

const taskCounts = computed(() => {
  const counts = { PENDING: 0, RUNNING: 0, SUCCESS: 0, FAILED: 0 }
  for (const task of taskStore.tasks) {
    counts[task.status] = (counts[task.status] || 0) + 1
  }
  return counts
})

const stats = computed(() => [
  { name: t('dashboard.pipelines'), stat: String(pipelineStore.pipelines.length), change: t('common.total'), changeType: 'neutral' },
  { name: t('dashboard.totalTasks'), stat: String(taskStore.tasks.length), change: t('dashboard.running', { n: taskCounts.value.RUNNING }), changeType: taskCounts.value.RUNNING > 0 ? 'increase' : 'neutral' },
  { name: t('dashboard.successRate'), stat: taskStore.tasks.length > 0 ? `${Math.round((taskCounts.value.SUCCESS / taskStore.tasks.length) * 100)}%` : '—', change: t('dashboard.failed', { n: taskCounts.value.FAILED }), changeType: taskCounts.value.FAILED > 0 ? 'decrease' : 'increase' },
  { name: t('dashboard.inputFiles'), stat: String(fileStore.filesByBucket.input.length), change: t('dashboard.outputs', { n: fileStore.filesByBucket.output.length }), changeType: 'neutral' },
])

function initCharts() {
  if (taskRunsEl.value) {
    taskRunsChart.value = echarts.init(taskRunsEl.value)
    updateTaskRunsChart()
  }
  if (statusPieEl.value) {
    statusPieChart.value = echarts.init(statusPieEl.value)
    updateStatusPieChart()
  }
  if (storageEl.value) {
    storageChart.value = echarts.init(storageEl.value)
    updateStorageChart()
  }
}

function updateTaskRunsChart() {
  if (!taskRunsChart.value) return
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return d.toLocaleDateString('en-US', { weekday: 'short' })
  })
  const successByDay = new Array(7).fill(0)
  const failedByDay = new Array(7).fill(0)
  for (const task of taskStore.tasks) {
    const taskDate = new Date(task.createdAt)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - taskDate.getTime()) / (1000 * 60 * 60 * 24))
    if (diffDays >= 0 && diffDays < 7) {
      const idx = 6 - diffDays
      if (task.status === 'SUCCESS') successByDay[idx]++
      else if (task.status === 'FAILED') failedByDay[idx]++
    }
  }
  taskRunsChart.value.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: [t('dashboard.success'), t('task.failed')], textStyle: { color: '#9ca3af' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: days, axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#374151' } } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#374151', opacity: 0.3 } } },
    series: [
      { name: t('dashboard.success'), type: 'bar', stack: 'total', data: successByDay, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] } },
      { name: t('task.failed'), type: 'bar', stack: 'total', data: failedByDay, itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] } },
    ],
  })
}

function updateStatusPieChart() {
  if (!statusPieChart.value) return
  statusPieChart.value.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, color: '#9ca3af' },
      data: [
        { value: taskCounts.value.SUCCESS, name: t('dashboard.success'), itemStyle: { color: '#22c55e' } },
        { value: taskCounts.value.FAILED, name: t('task.failed'), itemStyle: { color: '#ef4444' } },
        { value: taskCounts.value.RUNNING, name: t('task.running'), itemStyle: { color: '#3b82f6' } },
        { value: taskCounts.value.PENDING, name: t('dashboard.pending'), itemStyle: { color: '#9ca3af' } },
      ].filter(d => d.value > 0),
    }],
  })
}

function updateStorageChart() {
  if (!storageChart.value) return
  storageChart.value.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '65%',
      label: { show: true, color: '#9ca3af' },
      data: [
        { value: fileStore.filesByBucket.input.length, name: t('dashboard.input'), itemStyle: { color: '#6366f1' } },
        { value: fileStore.filesByBucket.output.length, name: t('dashboard.output'), itemStyle: { color: '#8b5cf6' } },
      ].filter(d => d.value > 0),
    }],
  })
}

watch(() => taskStore.tasks.length, () => {
  updateTaskRunsChart()
  updateStatusPieChart()
})

watch(() => fileStore.filesByBucket.input.length + fileStore.filesByBucket.output.length, () => {
  updateStorageChart()
})
</script>
