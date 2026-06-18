package com.psim.mobile.gps

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.location.Location
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import com.psim.mobile.MainActivity
import com.psim.mobile.R
import com.psim.mobile.api.ApiClient
import com.psim.mobile.api.ReportRequest
import com.psim.mobile.device.DeviceInfo
import com.psim.mobile.device.TokenStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class GpsService : Service() {

    private lateinit var tokenStore: TokenStore
    private lateinit var deviceInfo: DeviceInfo
    private lateinit var locationHelper: LocationHelper
    private var wakelock: PowerManager.WakeLock? = null
    private var lastLocation: Location? = null
    private val serviceScope = CoroutineScope(Dispatchers.IO + Job())
    private var reportJob: Job? = null

    companion object {
        const val CHANNEL_ID = "gps_tracking_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_START = "com.psim.mobile.START"
        const val ACTION_STOP = "com.psim.mobile.STOP"

        fun start(context: Context) {
            val intent = Intent(context, GpsService::class.java).apply {
                action = ACTION_START
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            val intent = Intent(context, GpsService::class.java).apply {
                action = ACTION_STOP
            }
            context.startService(intent)
        }
    }

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        deviceInfo = DeviceInfo(this)
        locationHelper = LocationHelper(this)
        ApiClient.configure(tokenStore.serverUrl)
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                val notification = buildNotification()
                startForeground(NOTIFICATION_ID, notification)
                startLocationReporting()
            }
            ACTION_STOP -> {
                stopLocationReporting()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        stopLocationReporting()
        super.onDestroy()
    }

    private fun startLocationReporting() {
        acquireWakelock()

        locationHelper.getCurrentLocation { location ->
            if (location != null) {
                lastLocation = location
                reportLocation(location)
            }
        }

        locationHelper.startPeriodicUpdates { location ->
            lastLocation = location
        }

        val intervalMinutes = tokenStore.reportIntervalMinutes
        reportJob = serviceScope.launch {
            while (isActive) {
                delay(intervalMinutes * 60 * 1000L)
                val loc = lastLocation
                if (loc != null) {
                    reportLocation(loc)
                }
            }
        }
    }

    private fun stopLocationReporting() {
        reportJob?.cancel()
        reportJob = null
        locationHelper.stopPeriodicUpdates()
        releaseWakelock()
    }

    private fun reportLocation(location: Location) {
        if (!tokenStore.isConfigured) return

        val timeFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val batteryLevel = getBatteryLevel()

        val request = ReportRequest(
            longitude = location.longitude,
            latitude = location.latitude,
            battery_level = batteryLevel,
            location = "${location.latitude},${location.longitude}",
            track_time = timeFormat.format(Date()),
            description = "device:${deviceInfo.deviceName}"
        )

        serviceScope.launch {
            val result = ApiClient.reportLocation(tokenStore.apiToken, request)
            result.onFailure { e ->
                android.util.Log.e("GpsService", "Report failed", e)
            }
        }
    }

    private fun getBatteryLevel(): Int? {
        val intent = registerReceiver(null,
            android.content.IntentFilter(android.content.Intent.ACTION_BATTERY_CHANGED))
        if (intent != null) {
            val level = intent.getIntExtra("level", -1)
            val scale = intent.getIntExtra("scale", -1)
            if (level >= 0 && scale > 0) {
                return (level * 100 / scale)
            }
        }
        return null
    }

    private fun acquireWakelock() {
        if (wakelock == null) {
            val pm = getSystemService(POWER_SERVICE) as PowerManager
            wakelock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "PSIM:LocationWakeLock"
            )
            wakelock?.acquire(30 * 60 * 1000L)
        }
    }

    private fun releaseWakelock() {
        wakelock?.let {
            if (it.isHeld) it.release()
        }
        wakelock = null
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getString(R.string.notification_channel_desc)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val stopIntent = PendingIntent.getService(
            this, 0,
            Intent(this, GpsService::class.java).apply { action = ACTION_STOP },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.app_name))
            .setContentText(getString(R.string.notification_text))
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .addAction(android.R.drawable.ic_media_pause, "停止", stopIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
}
