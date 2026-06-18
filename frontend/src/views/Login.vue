<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">重点人员信息管理系统</h2>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="captcha">
          <div style="display:flex;gap:8px;width:100%">
            <el-input v-model="form.captcha" placeholder="验证码" :prefix-icon="Key" style="flex:1" />
            <img v-if="captchaImage" :src="captchaImage" style="width:120px;height:40px;cursor:pointer;border:1px solid #dcdfe6;border-radius:4px;flex-shrink:0" @click="loadCaptcha" />
            <el-button v-else :loading="captchaLoading" size="default" @click="loadCaptcha">获取验证码</el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login, getCaptcha } from '../api/auth'
import { useUserStore } from '../store'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const captchaImage = ref('')
const captchaToken = ref('')
const captchaLoading = ref(false)

const form = reactive({
  username: 'admin',
  password: '123456',
  captcha: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const res = await getCaptcha()
    captchaToken.value = res.token
    captchaImage.value = URL.createObjectURL(res.image)
  } catch {
    ElMessage.error('验证码加载失败')
  } finally {
    captchaLoading.value = false
  }
}

onMounted(loadCaptcha)

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await login({
      username: form.username,
      password: form.password,
      captcha: form.captcha,
      captcha_token: captchaToken.value,
    })
    if (res.code === 200) {
      userStore.setToken(res.data.token)
      userStore.setUser(res.data.user)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      loadCaptcha()
    }
  } catch {
    loadCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 22px;
}
</style>
