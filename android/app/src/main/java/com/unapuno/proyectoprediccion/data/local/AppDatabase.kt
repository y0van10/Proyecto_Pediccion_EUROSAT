package com.unapuno.proyectoprediccion.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [PredictionEntity::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun predictionDao(): PredictionDao
}
