package com.psim.mobile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.psim.mobile.device.DeviceInfo
import com.psim.mobile.device.TokenStore
import com.psim.mobile.gps.GpsService

class MainActivity : AppCompatActivity() {

    private lateinit var tokenStore: TokenStore
    private lateinit var deviceInfo: DeviceInfo

    private lateinit var etServerUrl: EditText
    private lateinit var etApiToken: EditText
    private lateinit var tvDeviceId: TextView
    private lateinit var tvStatus: TextView
    private lateinit var btnSave: Button
    private lateinit var btnStart: Button
    private lateinit var btnStop: Button

    private val requestMultiplePermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            askDisableBatteryOptimization()
        } else {
            Toast.makeText(this, "需要定位权限才能运行", Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tokenStore = TokenStore(this)
        deviceInfo = DeviceInfo(this)

        bindViews()
        loadConfig()
        updateStatus()
        setupListeners()
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun bindViews() {
        etServerUrl = findViewById(R.id.et_server_url)
        etApiToken = findViewById(R.id.et_api_token)
        tvDeviceId = findViewById(R.id.tv_device_id)
        tvStatus = findViewById(R.id.tv_status)
        btnSave = findViewById(R.id.btn_save)
        btnStart = findViewById(R.id.btn_start)
        btnStop = findViewById(R.id.btn_stop)
    }

    private fun loadConfig() {
        etServerUrl.setText(tokenStore.serverUrl)
        etApiToken.setText(tokenStore.apiToken)
        tvDeviceId.text = "设备ID: ${deviceInfo.deviceId}"
    }

    private fun updateStatus() {
        val isRunning = isServiceRunning()
        tvStatus.text = if (isRunning) "状态: 运行中" else "状态: 已停止"
        btnStart.isEnabled = !isRunning && tokenStore.isConfigured
        btnStop.isEnabled = isRunning
    }

    private fun setupListeners() {
        btnSave.setOnClickListener {
            tokenStore.serverUrl = etServerUrl.text.toString().trim()
            tokenStore.apiToken = etApiToken.text.toString().trim()
            tokenStore.deviceId = deviceInfo.deviceId
            Toast.makeText(this, "配置已保存", Toast.LENGTH_SHORT).show()
            updateStatus()
        }

        btnStart.setOnClickListener {
            if (!tokenStore.isConfigured) {
                Toast.makeText(this, "请先保存服务器地址和令牌", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            checkAndRequestPermissions()
        }

        btnStop.setOnClickListener {
            GpsService.stop(this)
            updateStatus()
        }
    }

    private fun checkAndRequestPermissions() {
        val permissions = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED
        ) {
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_BACKGROUND_LOCATION)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
            }
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissions.isNotEmpty()) {
            requestMultiplePermissions.launch(permissions.toTypedArray())
        } else {
            askDisableBatteryOptimization()
        }
    }

    private fun askDisableBatteryOptimization() {
        val pm = getSystemService(POWER_SERVICE) as PowerManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
            !pm.isIgnoringBatteryOptimizations(packageName)
        ) {
            AlertDialog.Builder(this)
                .setTitle("电池优化")
                .setMessage("为了确保定位服务稳定运行，请允许忽略电池优化")
                .setPositiveButton("去设置") { _, _ ->
                    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                        data = Uri.parse("package:$packageName")
                    }
                    startActivity(intent)
                }
                .setNegativeButton("跳过", null)
                .show()
        } else {
            startService()
        }
    }

    private fun startService() {
        GpsService.start(this)
        updateStatus()
        Toast.makeText(this, "定位服务已启动", Toast.LENGTH_SHORT).show()
    }

    private fun isServiceRunning(): Boolean {
        val manager = getSystemService(ACTIVITY_SERVICE) as android.app.ActivityManager
        for (service in manager.getRunningServices(Integer.MAX_VALUE)) {
            if (GpsService::class.java.name == service.service.className) {
                return true
            }
        }
        return false
    }
}
