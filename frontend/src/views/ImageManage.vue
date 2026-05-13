<template>
  <div class="image-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>CT影像管理</span>
          <el-button type="primary" @click="handleUpload">
            <el-icon><Upload /></el-icon>
            上传影像
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="影像名称">
          <el-input
            v-model="queryParams.name"
            placeholder="请输入影像名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="检测状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="未检测" value="pending" />
            <el-option label="已检测" value="detected" />
            <el-option label="检测中" value="processing" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="imageList" style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="影像名称" />
        <el-table-column prop="size" label="文件大小" width="120" />
        <el-table-column prop="status" label="检测状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="上传时间" width="180" />
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button type="primary" link @click="handlePreview(row)">
              预览
            </el-button>
            <el-button
              type="success"
              link
              @click="handleDetect(row)"
              :disabled="row.status === 'processing'"
            >
              {{ row.status === 'processing' ? '检测中' : '检测' }}
            </el-button>
            <el-button type="warning" link @click="handleDownload(row)">
              下载
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryParams.pageNum"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传CT影像" width="500px">
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :auto-upload="false"
        drag
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg/png/dcm 格式，单个文件不超过500MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">
          确定上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="影像预览" width="800px">
      <div class="image-preview">
        <img :src="previewImageUrl" alt="CT影像" style="width: 100%;" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { imageApi } from '../api'

const loading = ref(false)
const imageList = ref([])
const total = ref(0)
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const previewImageUrl = ref('')
const uploadRef = ref()

const queryParams = reactive({
  name: '',
  status: '',
  pageNum: 1,
  pageSize: 10
})

const uploadUrl = import.meta.env.VITE_API_BASE_URL + '/api/images/upload'
const uploadHeaders = {
  Authorization: 'Bearer ' + localStorage.getItem('token')
}

onMounted(() => {
  getList()
})

const getList = async () => {
  loading.value = true
  try {
    const res = await imageApi.list(queryParams)
    imageList.value = res.data.records
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取影像列表失败')
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.name = ''
  queryParams.status = ''
  queryParams.pageNum = 1
  getList()
}

const handleUpload = () => {
  uploadDialogVisible.value = true
}

const beforeUpload = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'application/dicom']
  const isAllowed = allowedTypes.includes(file.type) || file.name.endsWith('.dcm')
  const isLt500M = file.size / 1024 / 1024 < 500

  if (!isAllowed) {
    ElMessage.error('只能上传 JPG/PNG/DCM 格式的文件!')
    return false
  }
  if (!isLt500M) {
    ElMessage.error('文件大小不能超过 500MB!')
    return false
  }
  return true
}

const submitUpload = () => {
  uploadRef.value.submit()
}

const handleUploadSuccess = (response) => {
  ElMessage.success('上传成功')
  uploadDialogVisible.value = false
  getList()
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const handlePreview = (row) => {
  previewImageUrl.value = row.url
  previewDialogVisible.value = true
}

const handleDetect = async (row) => {
  try {
    await imageApi.detect(row.id)
    ElMessage.success('已提交检测任务')
    getList()
  } catch (error) {
    ElMessage.error('提交检测失败')
  }
}

const handleDownload = (row) => {
  window.open(row.downloadUrl)
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该影像吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await imageApi.delete(row.id)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSizeChange = (val) => {
  queryParams.pageSize = val
  getList()
}

const handlePageChange = (val) => {
  queryParams.pageNum = val
  getList()
}

const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'detected': 'success',
    'processing': 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'pending': '未检测',
    'detected': '已检测',
    'processing': '检测中'
  }
  return map[status] || '未知'
}
</script>

<style scoped>
.image-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.image-preview {
  display: flex;
  justify-content: center;
}
</style>
