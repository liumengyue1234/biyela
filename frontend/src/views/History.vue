<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史检测记录</span>
          <el-button type="danger" @click="handleBatchDelete" :disabled="selectedIds.length === 0">
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="影像名称">
          <el-input
            v-model="queryParams.imageName"
            placeholder="请输入影像名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="检测结果">
          <el-select v-model="queryParams.result" placeholder="请选择结果" clearable>
            <el-option label="阳性" value="positive" />
            <el-option label="阴性" value="negative" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测时间">
          <el-date-picker
            v-model="queryParams.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        :data="historyList"
        style="width: 100%"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="imageName" label="影像名称" />
        <el-table-column prop="modelName" label="使用模型" width="120" />
        <el-table-column prop="result" label="检测结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'positive' ? 'danger' : 'success'">
              {{ row.result === 'positive' ? '阳性' : '阴性' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="diceScore" label="Dice系数" width="100" />
        <el-table-column prop="iouScore" label="IoU" width="100" />
        <el-table-column prop="detectTime" label="检测时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)">
              查看详情
            </el-button>
            <el-button type="warning" link @click="handleViewReport(row)">
              查看报告
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

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="检测详情" width="900px">
      <div class="detail-content" v-if="currentDetail">
        <el-row :gutter="20">
          <el-col :span="12">
            <h3>原始影像</h3>
            <img :src="currentDetail.originalImage" alt="原始影像" style="width: 100%;" />
          </el-col>
          <el-col :span="12">
            <h3>分割结果</h3>
            <img :src="currentDetail.segmentationImage" alt="分割结果" style="width: 100%;" />
          </el-col>
        </el-row>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="影像名称">{{ currentDetail.imageName }}</el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentDetail.modelName }}</el-descriptions-item>
          <el-descriptions-item label="检测结果">
            <el-tag :type="currentDetail.result === 'positive' ? 'danger' : 'success'">
              {{ currentDetail.result === 'positive' ? '阳性' : '阴性' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="检测时间">{{ currentDetail.detectTime }}</el-descriptions-item>
          <el-descriptions-item label="Dice系数">{{ currentDetail.diceScore }}</el-descriptions-item>
          <el-descriptions-item label="IoU">{{ currentDetail.iouScore }}</el-descriptions-item>
          <el-descriptions-item label="精确率">{{ currentDetail.precision }}</el-descriptions-item>
          <el-descriptions-item label="召回率">{{ currentDetail.recall }}</el-descriptions-item>
          <el-descriptions-item label="F1分数">{{ currentDetail.f1Score }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { detectionApi } from '../api'

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const selectedIds = ref([])
const detailDialogVisible = ref(false)
const currentDetail = ref(null)

const queryParams = reactive({
  imageName: '',
  result: '',
  dateRange: [],
  pageNum: 1,
  pageSize: 10
})

onMounted(() => {
  getList()
})

const getList = async () => {
  loading.value = true
  try {
    const params = { ...queryParams }
    if (params.dateRange && params.dateRange.length === 2) {
      params.startDate = params.dateRange[0]
      params.endDate = params.dateRange[1]
    }
    delete params.dateRange

    const res = await detectionApi.getHistory(params)
    historyList.value = res.data.records
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.imageName = ''
  queryParams.result = ''
  queryParams.dateRange = []
  queryParams.pageNum = 1
  getList()
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleViewDetail = async (row) => {
  try {
    const res = await detectionApi.getDetail(row.id)
    currentDetail.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const handleViewReport = (row) => {
  window.open(`/report?id=${row.id}`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await detectionApi.deleteRecord(row.id)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条记录吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await detectionApi.batchDelete(selectedIds.value)
      ElMessage.success('批量删除成功')
      getList()
    } catch (error) {
      ElMessage.error('批量删除失败')
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
</script>

<style scoped>
.history {
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

.detail-content {
  padding: 10px;
}
</style>
