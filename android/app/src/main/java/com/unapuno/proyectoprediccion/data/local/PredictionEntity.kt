package com.unapuno.proyectoprediccion.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "predictions")
data class PredictionEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val predictedClass: String,
    val probability: Double,
    val inferenceTime: Double,
    val filename: String,
    val imagePath: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)
