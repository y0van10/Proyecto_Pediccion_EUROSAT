package com.unapuno.proyectoprediccion.data.repository

import com.unapuno.proyectoprediccion.data.local.PredictionDao
import com.unapuno.proyectoprediccion.data.local.PredictionEntity
import com.unapuno.proyectoprediccion.data.remote.ApiService
import com.unapuno.proyectoprediccion.data.remote.PredictionResponse
import kotlinx.coroutines.flow.Flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PredictionRepository @Inject constructor(
    private val apiService: ApiService,
    private val predictionDao: PredictionDao
) {
    val predictions: Flow<List<PredictionEntity>> = predictionDao.getAllPredictions()

    suspend fun predict(imageFile: File): Result<PredictionResponse> {
        return try {
            val requestBody = imageFile.asRequestBody("image/*".toMediaTypeOrNull())
            val part = MultipartBody.Part.createFormData("file", imageFile.name, requestBody)

            val response = apiService.predict(part)
            if (response.isSuccessful && response.body() != null) {
                val prediction = response.body()!!

                predictionDao.insert(
                    PredictionEntity(
                        predictedClass = prediction.predictedClass,
                        probability = prediction.probability,
                        inferenceTime = prediction.inferenceTime,
                        filename = prediction.filename,
                        imagePath = imageFile.absolutePath
                    )
                )

                Result.success(prediction)
            } else {
                Result.failure(Exception("Error del servidor: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun clearHistory() {
        predictionDao.deleteAll()
    }
}
