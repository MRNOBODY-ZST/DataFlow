<template>
  <AppLayout :title="t('files.title')">
    <div class="flex h-[calc(100vh-4rem)] flex-col">
      <!-- Top toolbar -->
      <div class="flex shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 py-2.5 dark:border-white/10 dark:bg-gray-900">
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
            {{ t(`files.${bucket}`) }}
          </button>
        </div>

        <div class="flex items-center gap-2">
          <template v-if="selectedKeys.size > 0">
            <span class="text-xs text-gray-500 dark:text-gray-400">{{ selectedKeys.size }} {{ t('common.selected') }}</span>
            <button v-if="isInputBucket" type="button" class="rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showMoveDialog = true">
              <span class="flex items-center gap-1"><ArrowRightIcon class="size-3.5" /> {{ t('common.move') }}</span>
            </button>
            <button type="button" class="rounded-md bg-red-50 px-3 py-1.5 text-sm font-semibold text-red-700 shadow-xs inset-ring inset-ring-red-200 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-400 dark:inset-ring-red-500/20 dark:hover:bg-red-500/20" @click="deleteSelected">
              <TrashIcon class="size-4" />
            </button>
            <button type="button" class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" @click="selectedKeys.clear()">{{ t('common.clear') }}</button>
          </template>

          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('common.search')"
              class="w-40 rounded-md bg-white px-3 py-1.5 pl-8 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
            />
            <MagnifyingGlassIcon class="pointer-events-none absolute left-2 top-1/2 size-4 -translate-y-1/2 text-gray-400" />
          </div>

          <template v-if="isInputBucket">
            <button type="button" class="rounded-md bg-white px-2.5 py-1.5 text-gray-700 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showNewFolder = true">
              <FolderPlusIcon class="size-4" />
            </button>
            <button type="button" class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="showUpload = true">{{ t('common.upload') }}</button>
          </template>
          <button type="button" class="rounded-md bg-white px-2.5 py-1.5 text-gray-700 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="refresh">
            <ArrowPathIcon class="size-4" />
          </button>
        </div>
      </div>

      <!-- Breadcrumb -->
      <div class="flex shrink-0 items-center gap-1 border-b border-gray-100 bg-gray-50 px-4 py-1.5 text-sm dark:border-white/5 dark:bg-gray-800/50">
        <button type="button" class="text-indigo-600 hover:text-indigo-500 dark:text-indigo-400" @click="navigateTo('')">
          <HomeIcon class="size-4" />
        </button>
        <template v-for="(seg, i) in breadcrumbs" :key="i">
          <ChevronRightIcon class="size-3 text-gray-400" />
          <button
            type="button"
            class="truncate text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
            @click="navigateTo(breadcrumbs.slice(0, i + 1).join('/') + '/')"
          >{{ seg }}</button>
        </template>
        <span class="ml-auto text-xs text-gray-400 dark:text-gray-500">{{ t('files.nFiles', { n: currentFiles.length }) }}, {{ t('files.nFolders', { n: folders.length }) }}</span>
      </div>

      <!-- File grid — fills remaining space -->
      <div
        class="flex-1 overflow-y-auto bg-white p-4 dark:bg-gray-900"
        @contextmenu.prevent="onBackgroundContextMenu"
        @click="closeContextMenu"
      >
        <div v-if="fileStore.loading" class="flex h-full items-center justify-center text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</div>
        <div v-else-if="folders.length === 0 && currentFiles.length === 0" class="flex h-full items-center justify-center">
          <div class="mx-auto max-w-sm rounded-lg border border-dashed border-gray-300 px-6 py-10 text-center dark:border-white/20">
            <FolderIcon class="mx-auto size-10 text-gray-400" />
            <h3 class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">{{ t('files.empty') }}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('files.noFilesHere') }}</p>
            <div class="mt-6 flex justify-center gap-2">
              <button v-if="isInputBucket" type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showNewFolder = true">{{ t('files.newFolder') }}</button>
              <button v-if="isInputBucket" type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="showUpload = true">{{ t('common.upload') }}</button>
            </div>
          </div>
        </div>

        <div v-else class="grid grid-cols-2 gap-1 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
          <!-- Folders -->
          <div
            v-for="folder in folders"
            :key="'d:' + folder"
            class="group relative flex cursor-pointer flex-col items-center rounded-lg border border-transparent p-3 transition-colors hover:border-amber-200 hover:bg-amber-50 dark:hover:border-amber-500/30 dark:hover:bg-amber-500/5"
            :class="{ 'ring-2 ring-indigo-400 dark:ring-indigo-500': dragOverFolder === folder }"
            @click="navigateTo(folder)"
            @contextmenu.prevent.stop="onFolderContextMenu($event, folder)"
            @dragover.prevent="isInputBucket && (dragOverFolder = folder)"
            @dragleave="dragOverFolder = ''"
            @drop.prevent="isInputBucket && onDropToFolder($event, folder)"
          >
            <FolderIcon class="size-12 text-amber-400" />
            <p class="mt-2 w-full truncate text-center text-xs font-medium text-gray-900 dark:text-white">{{ folderDisplayName(folder) }}</p>
            <p class="text-[10px] text-gray-400 dark:text-gray-500">{{ t('files.nFiles', { n: folderFileCount(folder) }) }}</p>
          </div>

          <!-- Files -->
          <div
            v-for="file in currentFiles"
            :key="file.key"
            class="group relative flex cursor-pointer flex-col items-center rounded-lg border p-3 transition-colors"
            :class="selectedKeys.has(file.key)
              ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10'
              : 'border-transparent hover:border-gray-200 hover:bg-gray-50 dark:hover:border-white/10 dark:hover:bg-white/5'"
            :draggable="isInputBucket"
            @click.exact="openDetails(file)"
            @click.ctrl="toggleSelect(file.key)"
            @click.meta="toggleSelect(file.key)"
            @contextmenu.prevent.stop="onFileContextMenu($event, file)"
            @dragstart="onFileDragStart($event, file)"
            @dragend="draggedFileKey = ''"
          >
            <div class="absolute left-1.5 top-1.5">
              <input
                type="checkbox"
                :checked="selectedKeys.has(file.key)"
                class="size-3.5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600 dark:border-white/20 dark:bg-white/5"
                @click.stop
                @change="toggleSelect(file.key)"
              />
            </div>

            <div v-if="isImage(file.key) && previewUrls[previewCacheKey(file)]" class="flex size-12 items-center justify-center overflow-hidden rounded-lg">
              <img :src="previewUrls[previewCacheKey(file)]" :alt="displayName(file.key)" class="size-12 rounded-lg object-cover" />
            </div>
            <div v-else class="flex size-12 items-center justify-center rounded-lg" :class="fileIconBg(file.key)">
              <component :is="fileIcon(file.key)" class="size-6 text-white" />
            </div>
            <p class="mt-2 w-full truncate text-center text-xs font-medium text-gray-900 dark:text-white">{{ displayName(file.key) }}</p>
            <p class="text-[10px] text-gray-400 dark:text-gray-500">{{ prettySize(file.size) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div
        v-if="contextMenu.show"
        class="fixed z-100 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-xl dark:border-white/10 dark:bg-gray-800"
        :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      >
        <template v-if="contextMenu.type === 'file'">
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="ctxOpen"><EyeIcon class="size-4" /> {{ t('files.viewDetails') }}</button>
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="ctxDownload"><ArrowDownTrayIcon class="size-4" /> {{ t('common.download') }}</button>
          <template v-if="isInputBucket">
            <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="ctxRename"><PencilIcon class="size-4" /> {{ t('common.rename') }}</button>
            <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="ctxMove"><ArrowRightIcon class="size-4" /> {{ t('files.moveTo') }}</button>
          </template>
          <div class="my-1 border-t border-gray-100 dark:border-white/5" />
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10" @click="ctxDelete"><TrashIcon class="size-4" /> {{ t('common.delete') }}</button>
        </template>
        <template v-else-if="contextMenu.type === 'folder'">
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="ctxOpenFolder"><FolderOpenIcon class="size-4" /> {{ t('common.open') }}</button>
          <div class="my-1 border-t border-gray-100 dark:border-white/5" />
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10" @click="ctxDeleteFolder"><TrashIcon class="size-4" /> {{ t('files.deleteFolder') }}</button>
        </template>
        <template v-else>
          <template v-if="isInputBucket">
            <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="showNewFolder = true; closeContextMenu()"><FolderPlusIcon class="size-4" /> {{ t('files.newFolder') }}</button>
            <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="showUpload = true; closeContextMenu()"><ArrowUpTrayIcon class="size-4" /> {{ t('files.uploadFiles') }}</button>
          </template>
          <button class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5" @click="refresh(); closeContextMenu()"><ArrowPathIcon class="size-4" /> {{ t('common.refresh') }}</button>
        </template>
      </div>
    </Teleport>
  </AppLayout>

  <UploadModal :open="showUpload" @close="showUpload = false" @uploaded="onUploaded" />

  <!-- Rename Dialog -->
  <TransitionRoot as="template" :show="showRename">
    <Dialog class="relative z-50" @close="showRename = false">
      <TransitionChild as="template" enter="ease-out duration-200" enter-from="opacity-0" enter-to="" leave="ease-in duration-150" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50" />
      </TransitionChild>
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <DialogPanel class="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
          <DialogTitle class="text-base font-semibold text-gray-900 dark:text-white">{{ t('common.rename') }}</DialogTitle>
          <input
            v-model="renameValue"
            type="text"
            class="mt-3 w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-indigo-500"
            @keydown.enter="doRename"
          />
          <div class="mt-4 flex justify-end gap-2">
            <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showRename = false">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="doRename">{{ t('common.rename') }}</button>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- New Folder Dialog -->
  <TransitionRoot as="template" :show="showNewFolder">
    <Dialog class="relative z-50" @close="showNewFolder = false">
      <TransitionChild as="template" enter="ease-out duration-200" enter-from="opacity-0" enter-to="" leave="ease-in duration-150" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50" />
      </TransitionChild>
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <DialogPanel class="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
          <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-500/10">
            <FolderPlusIcon class="size-6 text-amber-600 dark:text-amber-400" />
          </div>
          <DialogTitle class="mt-3 text-center text-base font-semibold text-gray-900 dark:text-white">{{ t('files.newFolder') }}</DialogTitle>
          <p v-if="currentPrefix" class="mt-1 text-center text-xs text-gray-500 dark:text-gray-400">{{ t('files.insideFolder', { path: currentPrefix }) }}</p>
          <input
            v-model="newFolderName"
            type="text"
            :placeholder="t('files.folderName')"
            class="mt-3 w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
            @keydown.enter="createFolder"
          />
          <div class="mt-4 flex justify-end gap-2">
            <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showNewFolder = false">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" :disabled="!newFolderName.trim()" @click="createFolder">{{ t('common.create') }}</button>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Move Dialog -->
  <TransitionRoot as="template" :show="showMoveDialog">
    <Dialog class="relative z-50" @close="showMoveDialog = false">
      <TransitionChild as="template" enter="ease-out duration-200" enter-from="opacity-0" enter-to="" leave="ease-in duration-150" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50" />
      </TransitionChild>
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <DialogPanel class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
          <DialogTitle class="text-base font-semibold text-gray-900 dark:text-white">{{ t('files.moveNFiles', { n: selectedKeys.size }) }}</DialogTitle>
          <div class="mt-4 max-h-60 space-y-1.5 overflow-y-auto">
            <button
              type="button"
              class="flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm"
              :class="moveTarget === '' ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10' : 'border-gray-200 hover:bg-gray-50 dark:border-white/10 dark:hover:bg-white/5'"
              @click="moveTarget = ''"
            ><HomeIcon class="size-4 text-gray-400" /> {{ t('files.root') }}</button>
            <button
              v-for="f in allFolders"
              :key="f"
              type="button"
              class="flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm"
              :class="moveTarget === f ? 'border-indigo-400 bg-indigo-50 dark:border-indigo-500/50 dark:bg-indigo-500/10' : 'border-gray-200 hover:bg-gray-50 dark:border-white/10 dark:hover:bg-white/5'"
              @click="moveTarget = f"
            ><FolderIcon class="size-4 text-amber-400" /> {{ f }}</button>
            <input
              v-model="moveNewFolder"
              type="text"
              :placeholder="t('files.newFolderPath')"
              class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
            />
          </div>
          <div class="mt-4 flex justify-end gap-2">
            <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showMoveDialog = false">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" :disabled="moving" @click="moveSelected">{{ moving ? t('files.moving') : t('common.move') }}</button>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- File Detail Drawer -->
  <TransitionRoot as="template" :show="showDetails">
    <Dialog class="relative z-50" @close="showDetails = false">
      <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="" leave="ease-in-out duration-500" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50" />
      </TransitionChild>
      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
            <TransitionChild as="template" enter="transform transition ease-in-out duration-500" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-500" leave-from="translate-x-0" leave-to="translate-x-full">
              <DialogPanel class="pointer-events-auto relative w-96">
                <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="" leave="ease-in-out duration-500" leave-from="" leave-to="opacity-0">
                  <div class="absolute top-0 left-0 -ml-8 flex pt-4 pr-2 sm:-ml-10 sm:pr-4">
                    <button type="button" class="relative rounded-md text-gray-300 hover:text-white dark:text-gray-400 dark:hover:text-white" @click="showDetails = false">
                      <XMarkIcon class="size-6" />
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
                      <h3 class="font-medium text-gray-900 dark:text-white">{{ t('files.information') }}</h3>
                      <dl class="mt-2 divide-y divide-gray-200 border-t border-b border-gray-200 dark:divide-white/10 dark:border-white/10">
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.bucket') }}</dt>
                          <dd class="text-gray-900 dark:text-white">{{ detailFile.bucket }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.folder') }}</dt>
                          <dd class="text-gray-900 dark:text-white">{{ fileFolder(detailFile.key) || '/' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4 py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.objectKey') }}</dt>
                          <dd class="break-all text-right text-gray-900 dark:text-white">{{ detailFile.key }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.type') }}</dt>
                          <dd class="text-gray-900 dark:text-white">{{ fileExt(detailFile.key).toUpperCase() || t('files.unknown') }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.lastModified') }}</dt>
                          <dd class="text-gray-900 dark:text-white">{{ formatDate(detailFile.lastModified) }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm font-medium">
                          <dt class="text-gray-500 dark:text-gray-400">{{ t('files.size') }}</dt>
                          <dd class="text-gray-900 dark:text-white">{{ prettySize(detailFile.size) }}</dd>
                        </div>
                      </dl>
                    </div>
                    <div class="flex gap-3">
                      <button type="button" class="flex-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="downloadFile(detailFile)">{{ t('common.download') }}</button>
                      <button type="button" class="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-gray-100 dark:inset-ring-white/5 dark:hover:bg-white/20" @click="removeDetail">{{ t('common.delete') }}</button>
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
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import {
  FolderIcon, FolderPlusIcon, FolderOpenIcon, DocumentIcon, PhotoIcon, FilmIcon,
  MusicalNoteIcon, TrashIcon, XMarkIcon, ArrowPathIcon, ArrowRightIcon,
  ArrowDownTrayIcon, ArrowUpTrayIcon, EyeIcon, PencilIcon,
} from '@heroicons/vue/24/outline'
import { MagnifyingGlassIcon, HomeIcon, ChevronRightIcon } from '@heroicons/vue/20/solid'
import AppLayout from '@/components/layout/AppLayout.vue'
import UploadModal from '@/components/ui/UploadModal.vue'
import { useFileStore } from '@/stores/file'
import { fileApi, type FileBucket, type FileMetadata } from '@/api/file'

const fileStore = useFileStore()
const { t } = useI18n()
const showUpload = ref(false)
const showDetails = ref(false)
const showNewFolder = ref(false)
const showMoveDialog = ref(false)
const showRename = ref(false)
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
const renameValue = ref('')
const renameFile = ref<FileMetadata | null>(null)
const draggedFileKey = ref('')
const dragOverFolder = ref('')

const contextMenu = reactive({
  show: false,
  x: 0,
  y: 0,
  type: '' as '' | 'file' | 'folder' | 'background',
  file: null as FileMetadata | null,
  folder: '',
})

const buckets: FileBucket[] = ['input', 'output', 'temp']
const bucketLabels: Record<FileBucket, string> = { input: 'Input', output: 'Output', temp: 'Temp' }
const isInputBucket = computed(() => fileStore.activeBucket === 'input')

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'heic']
const VIDEO_EXTS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
const AUDIO_EXTS = ['mp3', 'wav', 'flac', 'aac', 'ogg']

function isImage(key: string) { return IMAGE_EXTS.includes(fileExt(key)) }
function isVideo(key: string) { return VIDEO_EXTS.includes(fileExt(key)) }
function isAudio(key: string) { return AUDIO_EXTS.includes(fileExt(key)) }
function isPreviewable(key: string) { return isImage(key) || isVideo(key) || isAudio(key) }

const breadcrumbs = computed(() => currentPrefix.value.replace(/\/$/, '').split('/').filter(Boolean))

const folders = computed(() => {
  const prefix = currentPrefix.value
  const seen = new Set<string>()
  for (const f of fileStore.files) {
    if (!f.key.startsWith(prefix)) continue
    const rest = f.key.slice(prefix.length)
    const slashIdx = rest.indexOf('/')
    if (slashIdx > 0) seen.add(prefix + rest.slice(0, slashIdx + 1))
  }
  return Array.from(seen).sort()
})

const allFolders = computed(() => {
  const seen = new Set<string>()
  for (const f of fileStore.files) {
    const parts = f.key.split('/')
    for (let i = 1; i < parts.length; i++) seen.add(parts.slice(0, i).join('/') + '/')
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

watch(() => fileStore.files, () => loadThumbnails())

async function loadThumbnails() {
  for (const file of currentFiles.value) {
    if (!isImage(file.key)) continue
    const ck = previewCacheKey(file)
    if (previewUrls.value[ck]) continue
    try {
      const { url } = await fileApi.presignDownload(file.key, file.bucket)
      previewUrls.value[ck] = url
    } catch { /* skip */ }
  }
}

function previewCacheKey(file: FileMetadata) { return `${file.bucket}:${file.key}` }

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

async function refresh() { await fileStore.fetchFiles(fileStore.activeBucket) }

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
  if (selectedKeys.has(key)) selectedKeys.delete(key)
  else selectedKeys.add(key)
}

async function deleteSelected() {
  if (!confirm(t('files.confirmDeleteN', { n: selectedKeys.size }))) return
  for (const key of selectedKeys) await fileStore.deleteFile(fileStore.activeBucket, key)
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
  if (!confirm(t('files.confirmDeleteFolder', { n: folderFiles.length }))) return
  for (const f of folderFiles) await fileStore.deleteFile(f.bucket, f.key)
  await refresh()
}

// --- Context Menu ---
function onFileContextMenu(e: MouseEvent, file: FileMetadata) {
  contextMenu.show = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.type = 'file'
  contextMenu.file = file
  contextMenu.folder = ''
}

function onFolderContextMenu(e: MouseEvent, folder: string) {
  contextMenu.show = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.type = 'folder'
  contextMenu.file = null
  contextMenu.folder = folder
}

function onBackgroundContextMenu(e: MouseEvent) {
  contextMenu.show = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.type = 'background'
  contextMenu.file = null
  contextMenu.folder = ''
}

function closeContextMenu() { contextMenu.show = false }

function ctxOpen() {
  if (contextMenu.file) openDetails(contextMenu.file)
  closeContextMenu()
}

async function ctxDownload() {
  if (contextMenu.file) await downloadFile(contextMenu.file)
  closeContextMenu()
}

function ctxRename() {
  if (!contextMenu.file) return
  renameFile.value = contextMenu.file
  renameValue.value = displayName(contextMenu.file.key)
  showRename.value = true
  closeContextMenu()
}

function ctxMove() {
  if (contextMenu.file) {
    selectedKeys.clear()
    selectedKeys.add(contextMenu.file.key)
    showMoveDialog.value = true
  }
  closeContextMenu()
}

async function ctxDelete() {
  if (!contextMenu.file) return
  closeContextMenu()
  if (!confirm(t('files.confirmDeleteFile', { name: displayName(contextMenu.file.key) }))) return
  await fileStore.deleteFile(contextMenu.file.bucket, contextMenu.file.key)
}

function ctxOpenFolder() {
  if (contextMenu.folder) navigateTo(contextMenu.folder)
  closeContextMenu()
}

async function ctxDeleteFolder() {
  if (!contextMenu.folder) return
  closeContextMenu()
  await deleteFolder(contextMenu.folder)
}

async function doRename() {
  if (!renameFile.value || !renameValue.value.trim()) return
  const oldKey = renameFile.value.key
  const folder = fileFolder(oldKey)
  const newKey = folder + renameValue.value.trim()
  if (newKey === oldKey) { showRename.value = false; return }
  await fileApi.moveFile(fileStore.activeBucket, oldKey, newKey)
  showRename.value = false
  renameFile.value = null
  await refresh()
}

// --- Drag and Drop ---
function onFileDragStart(e: DragEvent, file: FileMetadata) {
  draggedFileKey.value = file.key
  if (!selectedKeys.has(file.key)) {
    selectedKeys.clear()
    selectedKeys.add(file.key)
  }
  e.dataTransfer?.setData('text/plain', file.key)
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}

async function onDropToFolder(e: DragEvent, folder: string) {
  dragOverFolder.value = ''
  const keys = selectedKeys.size > 0 ? Array.from(selectedKeys) : [e.dataTransfer?.getData('text/plain') ?? '']
  const validKeys = keys.filter(k => k && !k.startsWith(folder))
  if (validKeys.length === 0) return
  const moves = validKeys.map(srcKey => ({
    srcKey,
    destKey: folder + (srcKey.split('/').pop() || srcKey),
  }))
  await fileApi.batchMove(fileStore.activeBucket, moves)
  selectedKeys.clear()
  draggedFileKey.value = ''
  await refresh()
}

// --- Details & helpers ---
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

async function downloadFile(file: FileMetadata) {
  const { url } = await fileApi.presignDownload(file.key, file.bucket)
  window.open(url, '_blank')
}

async function removeDetail() {
  if (!detailFile.value) return
  await fileStore.deleteFile(detailFile.value.bucket, detailFile.value.key)
  showDetails.value = false
  detailFile.value = null
}

async function onUploaded(file: FileMetadata) {
  showUpload.value = false
  fileStore.filesByBucket.input.unshift(file)
  fileStore.setBucket('input')
  await fileStore.fetchFiles('input')
}

function folderDisplayName(prefix: string) { return prefix.replace(/\/$/, '').split('/').pop() || prefix }
function folderFileCount(prefix: string) { return fileStore.files.filter((f) => f.key.startsWith(prefix)).length }
function displayName(key: string) { return key.split('/').pop() || key }
function fileFolder(key: string) { const p = key.split('/'); return p.length <= 1 ? '' : p.slice(0, -1).join('/') + '/' }
function fileExt(key: string) { return key.split('.').pop()?.toLowerCase() || '' }

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
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}
</script>
