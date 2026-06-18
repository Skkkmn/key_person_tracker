package com.psim.mobile.device

import android.content.Context
import android.content.SharedPreferences

class TokenStore(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("psim_tracker", Context.MODE_PRIVATE)

    var apiToken: String
        get() = prefs.getString(KEY_TOKEN, "") ?: ""
        set(value) = prefs.edit().putString(KEY_TOKEN, value).apply()

    var serverUrl: String
        get() = prefs.getString(KEY_SERVER_URL, "http://10.0.2.2:5000") ?: ""
        set(value) = prefs.edit().putString(KEY_SERVER_URL, value.trimEnd('/')).apply()

    var deviceId: String
        get() = prefs.getString(KEY_DEVICE_ID, "") ?: ""
        set(value) = prefs.edit().putString(KEY_DEVICE_ID, value).apply()

    var reportIntervalMinutes: Long
        get() = prefs.getLong(KEY_INTERVAL, DEFAULT_INTERVAL)
        set(value) = prefs.edit().putLong(KEY_INTERVAL, value).apply()

    val isConfigured: Boolean
        get() = apiToken.isNotBlank() && serverUrl.isNotBlank()

    fun clear() {
        prefs.edit().clear().apply()
    }

    companion object {
        private const val KEY_TOKEN = "api_token"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_INTERVAL = "report_interval"
        const val DEFAULT_INTERVAL: Long = 15
    }
}
