<template>
  <el-container style="height:100vh">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">{{ isCollapse ? '重' : '重点人员信息管理系统' }}</div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon><span>首页</span>
        </el-menu-item>
        <el-menu-item index="/persons">
          <el-icon><User /></el-icon><span>重点人员管理</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Warning /></el-icon><span>预警管理</span>
        </el-menu-item>
        <el-menu-item index="/visit-tasks">
          <el-icon><List /></el-icon><span>走访任务</span>
        </el-menu-item>
        <el-menu-item index="/risk-assessment">
          <el-icon><TrendCharts /></el-icon><span>风险评估</span>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon><span>通知中心</span>
        </el-menu-item>
        <el-menu-item index="/lost-contact">
          <el-icon><Search /></el-icon><span>失联追踪</span>
        </el-menu-item>
        <el-menu-item index="/map">
          <el-icon><MapLocation /></el-icon><span>地图监控</span>
        </el-menu-item>
        <el-menu-item index="/cross-region">
          <el-icon><Switch /></el-icon><span>流入流出管理</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Collection /></el-icon><span>人员类别</span>
        </el-menu-item>
        <el-menu-item index="/tags">
          <el-icon><PriceTag /></el-icon><span>标签管理</span>
        </el-menu-item>
        <el-sub-menu v-if="userStore.isAdmin" index="sys">
          <template #title>
            <el-icon><Setting /></el-icon><span>系统管理</span>
          </template>
          <el-menu-item index="/departments">部门管理</el-menu-item>
          <el-menu-item index="/users">用户管理</el-menu-item>
          <el-menu-item index="/logs">操作日志</el-menu-item>
          <el-menu-item index="/devices">定位设备</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon size="20" style="cursor:pointer" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <span class="page-title">{{ route.meta?.title }}</span>
        </div>
        <div class="header-right">
          <span style="margin-right:12px;color:#333">{{ userStore.username }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar size="small" style="background-color:#409eff;cursor:pointer">{{ userStore.username?.charAt(0) }}</el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

    <el-dialog v-model="pwdVisible" title="修改密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="原密码" prop="old_password"><el-input v-model="pwdForm.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码" prop="new_password"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
        <el-form-item label="确认密码" prop="confirm_password"><el-input v-model="pwdForm.confirm_password" type="password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="handleChangePwd">确认</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, User, Warning, Collection, PriceTag, Setting, Fold, Expand, List, TrendCharts, Bell, Search, MapLocation, Switch } from '@element-plus/icons-vue'
import { useUserStore } from '../store'
import { changePassword } from '../api/auth'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const pwdVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref(null)

const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码不少于6位', trigger: 'blur' }],
  confirm_password: [{ required: true, message: '请确认新密码', trigger: 'blur' }, {
    validator: (rule, value, cb) => value === pwdForm.new_password ? cb() : cb(new Error('两次密码不一致')),
    trigger: 'blur',
  }],
}

const handleCommand = (cmd) => {
  if (cmd === 'password') { pwdForm.old_password = ''; pwdForm.new_password = ''; pwdForm.confirm_password = ''; pwdVisible.value = true }
  else if (cmd === 'logout') handleLogout()
}

const handleChangePwd = async () => {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  pwdLoading.value = true
  try {
    const res = await changePassword({ old_password: pwdForm.old_password, new_password: pwdForm.new_password })
    if (res.code === 200) { ElMessage.success('密码修改成功，请重新登录'); pwdVisible.value = false; handleLogout() }
  } finally { pwdLoading.value = false }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确认退出登录？', '提示')
    userStore.logout()
    router.push('/login')
  } catch {}
}
</script>

<style scoped>
.aside { background-color: #304156; overflow-y: auto; overflow-x: hidden; }
.logo { height: 56px; line-height: 56px; text-align: center; color: #fff; font-size: 16px; font-weight: bold; background-color: #2b3a4a; overflow: hidden; white-space: nowrap; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e6e6e6; padding: 0 16px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 16px; font-weight: bold; color: #333; }
.header-right { display: flex; align-items: center; }
.main { background: #f0f2f5; min-height: calc(100vh - 60px); }
.el-menu { border-right: none; }
</style>
