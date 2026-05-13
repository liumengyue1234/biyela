<template>
  <div class="image-uploader">
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :limit="limit"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :on-exceed="handleExceed"
      :accept="accept"
      :drag="drag"
      :disabled="disabled"
      class="upload-area"
    >
      <slot name="trigger">
        <div class="default-trigger">
          <el-icon :size="48" color="#409eff"><UploadFilled /></el-icon>
          <p class="upload-title">{{ placeholder }}</p>
          <p class="upload-hint">{{ hint }}</p>
        </div>
      </slot>
    </el-upload>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: [File, Array],
    default: null,
  },
  limit: {
    type: Number,
    default: 1,
  },
  accept: {
    type: String,
    default: '.png,.jpg,.jpeg,.bmp,.dcm',
  },
  drag: {
    type: Boolean,
    default: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  maxSize: {
    type: Number,
    default: 50, // MB
  },
  placeholder: {
    type: String,
    default: '点击或拖拽文件到此区域',
  },
  hint: {
    type: String,
    default: '支持 PNG、JPG、BMP、DCM 格式，单个文件不超过50MB',
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'remove'])

const uploadRef = ref()

const validateFile = (file) => {
  const isValidType = props.accept.split(',').some(ext => {
    return file.name.toLowerCase().endsWith(ext.trim())
  })
  if (!isValidType) {
    ElMessage.error(`不支持的文件格式，请上传 ${props.accept} 格式的文件`)
    return false
  }
  const isValidSize = file.size / 1024 / 1024 < props.maxSize
  if (!isValidSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  return true
}

const handleChange = (file) => {
  if (!validateFile(file)) {
    uploadRef.value?.handleRemove(file)
    return
  }
  const rawFile = file.raw || file
  emit('update:modelValue', rawFile)
  emit('change', rawFile)
}

const handleRemove = (file) => {
  emit('update:modelValue', null)
  emit('remove', file)
}

const handleExceed = () => {
  ElMessage.warning(`最多只能上传 ${props.limit} 个文件`)
}

const clearFiles = () => {
  uploadRef.value?.clearFiles()
  emit('update:modelValue', null)
}

defineExpose({ clearFiles })
</script>

<style scoped>
.upload-area {
  width: 100%;
}
.default-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}
.upload-title {
  font-size: 15px;
  color: #303133;
  margin: 8px 0 4px;
}
.upload-hint {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
</style>
