package com.psim.mobile.api

data class ReportRequest(
    val longitude: Double,
    val latitude: Double,
    val battery_level: Int?,
    val location: String,
    val track_time: String,
    val description: String
)

data class ReportResponse(
    val code: Int,
    val message: String
)

data class DeviceBindInfo(
    val device_id: Int,
    val person_id: Int,
    val person_name: String?,
    val api_token: String,
    val is_active: Boolean
)
