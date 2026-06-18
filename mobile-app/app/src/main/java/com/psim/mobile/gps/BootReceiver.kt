package com.psim.mobile.gps

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.psim.mobile.device.TokenStore

class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            val tokenStore = TokenStore(context)
            if (tokenStore.isConfigured) {
                GpsService.start(context)
            }
        }
    }
}
