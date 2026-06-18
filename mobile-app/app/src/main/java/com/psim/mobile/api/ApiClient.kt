package com.psim.mobile.api

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

interface ApiService {

    @POST("/api/devices/mobile-report")
    suspend fun reportLocation(
        @Header("X-Device-Token") token: String,
        @Body request: ReportRequest
    ): ReportResponse
}

object ApiClient {

    private var baseUrl: String = "http://10.0.2.2:5000"
    private var retrofit: Retrofit? = null
    private var apiService: ApiService? = null

    fun configure(serverUrl: String) {
        if (baseUrl == serverUrl && retrofit != null) return
        baseUrl = serverUrl.trimEnd('/')

        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit!!.create(ApiService::class.java)
    }

    fun getService(): ApiService {
        return apiService ?: throw IllegalStateException("ApiClient not configured. Call configure() first.")
    }

    suspend fun reportLocation(token: String, request: ReportRequest): Result<ReportResponse> {
        return try {
            val response = getService().reportLocation(token, request)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
