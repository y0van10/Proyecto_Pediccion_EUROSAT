package com.unapuno.proyectoprediccion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import com.unapuno.proyectoprediccion.ui.navigation.AppNavGraph
import com.unapuno.proyectoprediccion.ui.theme.ProyectoPrediccionTheme
import com.unapuno.proyectoprediccion.ui.viewmodel.MainViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ProyectoPrediccionTheme {
                AppNavGraph(viewModel = viewModel)
            }
        }
    }
}
