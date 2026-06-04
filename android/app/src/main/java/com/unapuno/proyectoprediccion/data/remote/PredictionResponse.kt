package com.unapuno.proyectoprediccion.data.remote

import com.google.gson.annotations.SerializedName

data class PredictionResponse(
    @SerializedName("class") val predictedClass: String,
    @SerializedName("probability") val probability: Double,
    @SerializedName("inference_time") val inferenceTime: Double,
    @SerializedName("filename") val filename: String
)
