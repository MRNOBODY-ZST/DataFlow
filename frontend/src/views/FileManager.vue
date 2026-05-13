<template>
  <AppLayout title="Files">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">File Manager</h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Manage input files and view output/temp files.</p>
        </div>
        <div class="mt-4 flex items-center gap-2 sm:mt-0">
          <button
            type="button"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20"
            @click="showNewFolder = true"
          >
            <span class="flex items-center gap-1.5">
              <FolderPlusIcon class="size-4" />
              New Folder
            </span>
          </button>
          <button
            type="button"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:shadow-none dark:hover:bg-indigo-400"
            @click="showUpload = true"
          >
            Upload
          </button>
        </div>
      </div>

      <!-- Stats -->
      <dl class="mt-6 grid grid-cols-1 divide-gray-200 overflow-hidden rounded-lg bg-white shadow-sm md:grid-cols-4 md:divide-x md:divide-y-0 dark:divide-white/10 dark:bg-gray-800/75 dark:shadow-none dark:inset-ring dark:inset-ring-white/10">
        <div class="px-4 py-5 sm:p-6">
          <dt class="text-base font-normal text-gray-900 dark:text-gray-100">Input Files</dt>
          <dd class="mt-1 text-2xl font-semibold text-indigo-600 dark:text-indigo-400">{{ fileStore.filesByBucket.input.length }}</dd>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <dt class="text-base font-normal text-gray-900 dark:text-gray-100">Output Files</dt>
          <dd class="mt-1 text-2xl font-semibold text-indigo-600 dark:text-indigo-400">{{ fileStore.filesByBucket.output.length }}</dd>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <dt class="text-base font-normal text-gray-900 dark:text-gray-100">Current Path</dt>
          <dd class="mt-1 truncate text-lg font-semibold text-indigo-600 dark:text-indigo-400">{{ currentPrefix || '/' }}</dd>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <dt class="text-base font-normal text-gray-900 dark:text-gray-100">Current Bucket</dt>
          <dd class="mt-1 text-2xl font-semibold text-indigo-600 dark:text-indigo-400">{{ fileStore.activeBucket }}</dd>
        </div>
      </dl>

      <!-- Bucket tabs + toolbar -->
      <div class="mt-6 rounded-lg bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
        <div class="border-b border-gray-200 px-4 py-4 sm:px-6 dark:border-white/10">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <button
                v-for="bucket in buckets"
                :key="bucket"
                type="button"
                class="rounded-full px-3 py-1.5 text-sm font-medium"
                :class="fileStore.activeBucket === bucket
                  ? 'bg-indigo-600 text-white dark:bg-indigo-500'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20'"
                @click="switchBucket(bucket)"
              >
                {{ bucketLabels[bucket] }}
              </button>
            </div>
            <div class="flex items-center gap-2">
              <!-- Selection actions -->
              <template v-if="selectedKeys.size > 0">
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ selectedKeys.size }} selected</span>
                <button type="button" class="rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showMoveDialog = true">
                  <span class="flex items-center gap-1"><ArrowRightIcon class="size-3.5" /> Move</span>
                </button>
                <button type="button" class="rounded-md bg-red-50 px-3 py-1.5 text-sm font-semibold text-red-700 shadow-xs inset-ring inset-ring-red-200 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-400 dark:inset-ring-red-500/20 dark:hover:bg-red-500/20" @click="deleteSelected">
                  <TrashIcon class="size-4" />
                </button>
                <button type="button" class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" @click="selectedKeys.clear()">Clear</button>
              </template>
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search files..."
                  class="w-48 rounded-md bg-white px-3 py-1.5 pl-8 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
                />
                <MagnifyingGlassIcon class="pointer-events-none absolute left-2 top-1/2 size-4 -translate-y-1/2 text-gray-400" />
              </div>
              <button type="button" class="rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="refresh">
                <ArrowPathIcon class="size-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Breadcrumb -->
        <div v-if="currentPrefix" class="flex items-center gap-1 border-b border-gray-200 px-4 py-2 text-sm dark:border-white/10">
          <button type="button" class="text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300" @click="navigateTo('')">
            <HomeIcon class="size-4" />
          </button>
          <template v-for="(seg, i) in breadcrumbs" :key="i">
            <ChevronRightIcon class="size-3 text-gray-400" />
            <button
              type="button"
              class="truncate text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
              @click="navigateTo(breadcrumbs.slice(0, i + 1).join('/') + '/')"
            >
              {{ seg }}
            </button>
          </template>
        </div>

        <!-- Loading / Empty -->
        <div v-if="fileStore.loading" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="folders.length === 0 && currentFiles.length === 0" class="px-6 py-16 text-center">
          <div class="mx-auto max-w-sm rounded-lg border border-dashed border-gray-300 px-6 py-10 dark:border-white/20">
            <FolderIcon class="mx-auto size-10 text-gray-400" />
            <h3 class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">Empty</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">No files or folders here.</p>
            <div class="mt-6 flex justify-center gap-2">
              <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showNewFolder = true">New Folder</button>
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="showUpload = true">Upload</button>
            </div>
          </div>
        </div>

        <!-- Grid: Folders + Files -->
        <div v-else class="grid grid-cols-1 gap-0.5 p-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          <!-- Folders -->
          <div
            v-for="folder in folders"
            :key="'d:' + folder"
            class="group relative flex cursor-pointer flex-col items-center rounded-lg border border-transparent p-4 hover:border-amber-200 hover:bg-amber-50 dark:hover:border-amber-500/30 dark:hover:bg-amber-500/5"
            @click="navigateTo(folder)"
          >
            <FolderIcon class="size-16 text-amber-400" />
            <p class="mt-3 w-full truncate text-center text-sm font-medium text-gray-900 dark:text-white">{{ folderDisplayName(folder) }}</p>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ folderFileCount(folder) }} files</p>
            <div v-if="fileStore.activeBucket === 'input'" class="absolute right-2 top-2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
              <button type="button" class="rounded-md p-1 text-red-400 hover:text-red-600 dark:hover:text-red-300" @click.stop="deleteFolder(folder)">
                <TrashIcon class="size-4" />
              </button>
            </div>
          </div>

          <!-- Files -->
          <div
            v-for="file in currentFiles"
            :key="file.key"
            class="group relative flex cursor-pointer flex-col items-center rounded-lg border p-4 transition-colors"
            :class="selectedKeys.has(file.key)
              ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10'
              : 'border-transparent hover:border-gray-200 hover:bg-gray-50 dark:hover:border-white/10 dark:hover:bg-white/5'"
            @click.exact="openDetails(file)"
            @click.ctrl="toggleSelect(file.key)"
            @click.meta="toggleSelect(file.key)"
          >
            <!-- Select checkbox -->
            <div v-if="fileStore.activeBucket === 'input'" class="absolute left-2 top-2">
              <input
                type="checkbox"
                :checked="selectedKeys.has(file.key)"
                class="size-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600 dark:border-white/20 dark:bg-white/5"
                @click.stop
                @change="toggleSelect(file.key)"
              />
            </div>

            <!-- Thumbnail -->
            <div v-if="isImage(file.key) && previewUrls[previewCacheKey(file)]" class="flex size-16 items-center justify-center overflow-hidden rounded-lg">
              <img :src="previewUrls[previewCacheKey(file)]" :alt="displayName(file.key)" class="size-16 rounded-lg object-cover" />
            </div>
            <div v-else class="flex size-16 items-center justify-center rounded-lg" :class="fileIconBg(file.key)">
              <component :is="fileIcon(file.key)" class="size-8 text-white" />
            </div>
            <p class="mt-3 w-full truncate text-center text-sm font-medium text-gray-900 dark:text-white">{{ displayName(file.key) }}</p>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ prettySize(file.size) }}</p>
            <div v-if="fileStore.activeBucket === 'input'" class="absolute right-2 top-2 opacity-0 transition-opacity group-hover:opacity-100">
              <button type="button" class="rounded-md p-1 text-red-400 hover:text-red-600 dark:hover:text-red-300" @click.stop="remove(file)">
                <TrashIcon class="size-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>

  <UploadModal :open="showUpload" @close="showUpload = false" @uploaded="onUploaded" />

  <!-- New Folder Dialog -->
  <TransitionRoot as="template" :show="showNewFolder">
    <Dialog class="relative z-50" @close="showNewFolder = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>
      <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6 dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div>
                <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-500/10">
                  <FolderPlusIcon class="size-6 text-amber-600 dark:text-amber-400" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">New Folder</DialogTitle>
                  <div class="mt-2">
                    <p v-if="currentPrefix" class="mb-2 text-xs text-gray-500 dark:text-gray-400">Inside: {{ currentPrefix }}</p>
                    <input
                      v-model="newFolderName"
                      type="text"
                      placeholder="Folder name"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
                      @keydown.enter="createFolder"
                    />
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:col-start-2 disabled:opacity-60 dark:bg-indigo-500 dark:hover:bg-indigo-400" :disabled="!newFolderName.trim()" @click="createFolder">Create</button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showNewFolder = false">Cancel</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Move Dialog -->
  <TransitionRoot as="template" :show="showMoveDialog">
    <Dialog class="relative z-50" @close="showMoveDialog = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>
      <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-md sm:p-6 dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div>
                <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-500/10">
                  <ArrowRightIcon class="size-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">Move {{ selectedKeys.size }} file(s)</DialogTitle>
                  <div class="mt-4 space-y-3">
                    <p class="text-xs text-gray-500 dark:text-gray-400">Select destination folder:</p>
                    <!-- Root option -->
                    <button
                      type="button"
                      class="w-full flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm"
                      :class="moveTarget === '' ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10' : 'border-gray-200 hover:bg-gray-50 dark:border-white/10 dark:hover:bg-white/5'"
                      @click="moveTarget = ''"
                    >
                      <HomeIcon class="size-4 text-gray-400" />
                      <span class="text-gray-900 dark:text-white">/ (root)</span>
                    </button>
                    <!-- Folder list -->
                    <button
                      v-for="f in allFolders"
                      :key="f"
                      type="button"
                      class="w-full flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm"
                      :class="moveTarget === f ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10' : 'border-gray-200 hover:bg-gray-50 dark:border-white/10 dark:hover:bg-white/5'"
                      @click="moveTarget = f"
                    >
                      <FolderIcon class="size-4 text-amber-400" />
                      <span class="text-gray-900 dark:text-white">{{ f }}</span>
                    </button>
                    <!-- New folder inline -->
                    <div class="flex items-center gap-2">
                      <input
                        v-model="moveNewFolder"
                        type="text"
                        placeholder="Or type a new folder path..."
                        class="flex-1 rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:col-start-2 disabled:opacity-60 dark:bg-indigo-500 dark:hover:bg-indigo-400" :disabled="moving" @click="moveSelected">
                  {{ moving ? 'Moving...' : 'Move' }}
                </button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showMoveDialog = false">Cancel</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- File Detail Drawer -->
  <TransitionRoot as="template" :show="showDetails">
    <Dialog class="relative z-50" @close="showDetails = false">
      <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="" leave="ease-in-out duration-500" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>
      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
            <TransitionChild as="template" enter="transform transition ease-in-out duration-500 sm:duration-700" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-500 sm:duration-700" leave-from="translate-x-0" leave-to="translate-x-full">
              <DialogPanel class="pointer-events-auto relative w-96">
                <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="" leave="ease-in-out duration-500" leave-from="" leave-to="opacity-0">
                  <div class="absolute top-0 left-0 -ml-8 flex pt-4 pr-2 sm:-ml-10 sm:pr-4">
                    <button type="button" class="relative rounded-md text-gray-300 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 dark:text-gray-400 dark:hover:text-white dark:focus-visible:outline-indigo-500" @click="showDetails = false">
                      <span class="absolute -inset-2.5"></span>
                      <span class="sr-only">Close panel</span>
                      <XMarkIcon class="size-6" aria-hidden="true" />
                    </button>
                  </div>
                </TransitionChild>
                <div class="relative h-full overflow-y-auto bg-white p-8 dark:bg-gray-800 dark:after:absolute dark:after:inset-y-0 dark:after:left-0 dark:after:w-px dark:after:bg-white/10">
                  <div v-if="detailFile" class="space-y-6 pb-16">
                    <div>
                      <div v-if="isImage(detailFile.key) && detailPreviewUrl" class="overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-900">
                        <img :src="detailPreviewUrl" :alt="displayName(detailFile.key)" class="mx-auto max-h-64 object-contain" />
                      </div>
                      <div v-else-if="isVideo(detailFile.key) && detailPreviewUrl" class="overflow-hidden rounded-lg bg-black">
                        <video :src="detailPreviewUrl" controls class="mx-auto max-h-64 w-full" />
                      </div>
                      <div v-else-if="isAudio(detailFile.key) && detailPreviewUrl" class="rounded-lg bg-gray-100 p-4 dark:bg-gray-900">
                        <audio :src="detailPreviewUrl" controls class="w-full" />
                      </div>
                      <div v-else class="flex items-center gap-4">
                        <div class="flex size-16 items-center justify-center rounded-lg" :class="fileIconBg(detailFile.key)">
                          <component :is="fileIcon(detailFile.key)" class="size-8 text-white" />
                        </div>
                      </div>
                      <div class="mt-4 flex items-start justify-between">
                        <div>
                          <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ displayName(detailFile.key) }}</h2>
                          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ prettySize(detailFile.size) }}</p>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 class="font-medium text-gray-900 dark:text-white">Information</h3>
                      <dl class="mt-2 divide-y divide-gray-200 border-t border-b border-gray-200 dark:divide-white/10 dark:border-white/10">
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Bucket</dt>
                          <dd class="text-gray-900 dark:text-white">{{ detailFile.bucket }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Folder</dt>
                          <dd class="text-gray-900 dark:text-white">{{ fileFolder(detailFile.key) || '/' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4 py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Object Key</dt>
                          <dd class="break-all text-right text-gray-900 dark:text-white">{{ detailFile.key }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Type</dt>
                          <dd class="text-gray-900 dark:text-white">{{ fileExt(detailFile.key).toUpperCase() || 'Unknown' }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Last Modified</dt>
                          <dd class="text-gray-900 dark:text-white">{{ formatDate(detailFile.lastModified) }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">Size</dt>
                          <dd class="text-gray-900 dark:text-white">{{ prettySize(detailFile.size) }}</dd>
                        </div>
                      </dl>
                    </div>
                    <div class="flex gap-3">
                      <button type="button" class="flex-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:shadow-none dark:hover:bg-indigo-400" @click="download">Download</button>
                      <button v-if="detailFile.bucket === 'input'" type="button" class="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-gray-100 dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20" @click="removeDetail">Delete</button>
                    </div>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { FolderIcon, FolderPlusIcon, DocumentIcon, PhotoIcon, FilmIcon, MusicalNoteIcon, TrashIcon, XMarkIcon, ArrowPathIcon, ArrowRightIcon } from '@heroicons/vue/24/outline'
import { MagnifyingGlassIcon, HomeIcon, ChevronRightIcon } from '@heroicons/vue/20/solid'
import AppLayout from '@/components/layout/AppLayout.vue'
import UploadModal from '@/components/ui/UploadModal.vue'
import { useFileStore } from '@/stores/file'
import { fileApi, type FileBucket, type FileMetadata } from '@/api/file'

const fileStore = useFileStore()
const showUpload = ref(false)
const showDetails = ref(false)
const showNewFolder = ref(false)
const showMoveDialog = ref(false)
const detailFile = ref<FileMetadata | null>(null)
const detailPreviewUrl = ref<string | null>(null)
const searchQuery = ref('')
const previewUrls = ref<Record<string, string>>({})
const currentPrefix = ref('')
const newFolderName = ref('')
const moveTarget = ref('')
const moveNewFolder = ref('')
const moving = ref(false)
const selectedKeys = reactive(new Set<string>())

const buckets: FileBucket[] = ['input', 'output', 'temp']
const bucketLabels: Record<FileBucket, string> = {
  input: 'Input',
  output: 'Output',
  temp: 'Temp',
}

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'heic']
const VIDEO_EXTS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
const AUDIO_EXTS = ['mp3', 'wav', 'flac', 'aac', 'ogg']

function isImage(key: string) { return IMAGE_EXTS.includes(fileExt(key)) }
function isVideo(key: string) { return VIDEO_EXTS.includes(fileExt(key)) }
function isAudio(key: string) { return AUDIO_EXTS.includes(fileExt(key)) }
function isPreviewable(key: string) { return isImage(key) || isVideo(key) || isAudio(key) }

const breadcrumbs = computed(() =>
  currentPrefix.value.replace(/\/$/, '').split('/').filter(Boolean),
)

const folders = computed(() => {
  const prefix = currentPrefix.value
  const seen = new Set<string>()
  for (const f of fileStore.files) {
    if (!f.key.startsWith(prefix)) continue
    const rest = f.key.slice(prefix.length)
    const slashIdx = rest.indexOf('/')
    if (slashIdx > 0) {
      seen.add(prefix + rest.slice(0, slashIdx + 1))
    }
  }
  return Array.from(seen).sort()
})

const allFolders = computed(() => {
  const seen = new Set<string>()
  for (const f of fileStore.files) {
    const parts = f.key.split('/')
    for (let i = 1; i < parts.length; i++) {
      seen.add(parts.slice(0, i).join('/') + '/')
    }
  }
  return Array.from(seen).sort()
})

const currentFiles = computed(() => {
  const prefix = currentPrefix.value
  const q = searchQuery.value.trim().toLowerCase()
  return fileStore.files.filter((f) => {
    if (!f.key.startsWith(prefix)) return false
    const rest = f.key.slice(prefix.length)
    if (rest.includes('/')) return false
    if (q && !f.key.toLowerCase().includes(q)) return false
    return true
  })
})

onMounted(async () => {
  await fileStore.fetchFiles('input')
  loadThumbnails()
})

watch(() => fileStore.files, () => {
  loadThumbnails()
})

async function loadThumbnails() {
  for (const file of currentFiles.value) {
    if (!isImage(file.key)) continue
    const cacheKey = previewCacheKey(file)
    if (previewUrls.value[cacheKey]) continue
    try {
      const { url } = await fileApi.presignDownload(file.key, file.bucket)
      previewUrls.value[cacheKey] = url
    } catch { /* skip */ }
  }
}

function previewCacheKey(file: FileMetadata) {
  return `${file.bucket}:${file.key}`
}

function navigateTo(prefix: string) {
  currentPrefix.value = prefix
  selectedKeys.clear()
  loadThumbnails()
}

async function switchBucket(bucket: FileBucket) {
  currentPrefix.value = ''
  selectedKeys.clear()
  fileStore.setBucket(bucket)
  await fileStore.fetchFiles(bucket)
}

async function refresh() {
  await fileStore.fetchFiles(fileStore.activeBucket)
}

async function createFolder() {
  const name = newFolderName.value.trim()
  if (!name) return
  const folderKey = currentPrefix.value + name + '/.keep'
  const { url } = await fileApi.presignUpload(folderKey)
  const blob = new File([''], '.keep', { type: 'application/octet-stream' })
  await fileApi.uploadToMinio(url, blob)
  showNewFolder.value = false
  newFolderName.value = ''
  await refresh()
}

function toggleSelect(key: string) {
  if (selectedKeys.has(key)) {
    selectedKeys.delete(key)
  } else {
    selectedKeys.add(key)
  }
}

async function deleteSelected() {
  if (!confirm(`Delete ${selectedKeys.size} file(s)?`)) return
  for (const key of selectedKeys) {
    await fileStore.deleteFile(fileStore.activeBucket, key)
  }
  selectedKeys.clear()
}

async function moveSelected() {
  const dest = moveNewFolder.value.trim() || moveTarget.value
  const destPrefix = dest ? (dest.endsWith('/') ? dest : dest + '/') : ''
  moving.value = true
  try {
    const moves = Array.from(selectedKeys).map((srcKey) => {
      const fname = srcKey.split('/').pop() || srcKey
      return { srcKey, destKey: destPrefix + fname }
    })
    await fileApi.batchMove(fileStore.activeBucket, moves)
    selectedKeys.clear()
    showMoveDialog.value = false
    moveTarget.value = ''
    moveNewFolder.value = ''
    await refresh()
  } catch (e: any) {
    alert(e.message || 'Move failed')
  } finally {
    moving.value = false
  }
}

async function deleteFolder(prefix: string) {
  const folderFiles = fileStore.files.filter((f) => f.key.startsWith(prefix))
  if (!confirm(`Delete folder and ${folderFiles.length} file(s)?`)) return
  for (const f of folderFiles) {
    await fileStore.deleteFile(f.bucket, f.key)
  }
  await refresh()
}

function folderDisplayName(prefix: string) {
  const parts = prefix.replace(/\/$/, '').split('/')
  return parts[parts.length - 1]
}

function folderFileCount(prefix: string) {
  return fileStore.files.filter((f) => f.key.startsWith(prefix)).length
}

async function openDetails(file: FileMetadata) {
  detailFile.value = file
  detailPreviewUrl.value = null
  showDetails.value = true
  if (isPreviewable(file.key)) {
    try {
      const { url } = await fileApi.presignDownload(file.key, file.bucket)
      detailPreviewUrl.value = url
    } catch { /* skip */ }
  }
}

async function remove(file: FileMetadata) {
  if (!confirm(`Delete ${displayName(file.key)}?`)) return
  await fileStore.deleteFile(file.bucket, file.key)
}

async function removeDetail() {
  if (!detailFile.value || detailFile.value.bucket !== 'input') return
  await fileStore.deleteFile(detailFile.value.bucket, detailFile.value.key)
  showDetails.value = false
  detailFile.value = null
}

async function download() {
  if (!detailFile.value) return
  const { url } = await fileApi.presignDownload(detailFile.value.key, detailFile.value.bucket)
  window.open(url, '_blank')
}

async function onUploaded(file: FileMetadata) {
  showUpload.value = false
  fileStore.filesByBucket.input.unshift(file)
  fileStore.setBucket('input')
  await fileStore.fetchFiles('input')
}

function displayName(key: string) {
  return key.split('/').pop() || key
}

function fileFolder(key: string) {
  const parts = key.split('/')
  if (parts.length <= 1) return ''
  return parts.slice(0, -1).join('/') + '/'
}

function fileExt(key: string) {
  return key.split('.').pop()?.toLowerCase() || ''
}

function fileIcon(key: string) {
  const ext = fileExt(key)
  if (IMAGE_EXTS.includes(ext)) return PhotoIcon
  if (VIDEO_EXTS.includes(ext)) return FilmIcon
  if (AUDIO_EXTS.includes(ext)) return MusicalNoteIcon
  return DocumentIcon
}

function fileIconBg(key: string) {
  const ext = fileExt(key)
  if (IMAGE_EXTS.includes(ext)) return 'bg-pink-500'
  if (VIDEO_EXTS.includes(ext)) return 'bg-purple-500'
  if (AUDIO_EXTS.includes(ext)) return 'bg-amber-500'
  if (['csv', 'json', 'xml', 'yaml', 'yml'].includes(ext)) return 'bg-green-500'
  return 'bg-indigo-500'
}

function prettySize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}
</script>
