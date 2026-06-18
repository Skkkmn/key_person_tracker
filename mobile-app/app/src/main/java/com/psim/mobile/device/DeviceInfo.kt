package com.psim.mobile.device

import android.content.Context
import android.content.SharedPreferences
import android.provider.Settings
import android.telephony.TelephonyManager

class DeviceInfo(private val context: Context) {

    val deviceId: String
        get() = Settings.Secure.getString(
            context.contentResolver, Settings.Secure.ANDROID_ID
        )

    val deviceName: String
        get() = android.os.Build.MODEL

    val manufacturer: String
        get() = android.os.Build.MANUFACTURER

    val imei: String
        get() {
            val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
            return if (tm != null) {
                tm.imei ?: ""
            } else ""
        }
}
