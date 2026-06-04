package com.unapuno.proyectoprediccion.ui.viewmodel

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.unapuno.proyectoprediccion.data.local.PredictionEntity
import com.unapuno.proyectoprediccion.data.remote.PredictionResponse
import com.unapuno.proyectoprediccion.data.repository.PredictionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

data class PredictionUiState(
    val isLoading: Boolean = false,
    val result: PredictionResponse? = null,
    val error: String? = null,
    val selectedImageUri: Uri? = null
)

@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: PredictionRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PredictionUiState())
    val uiState: StateFlow<PredictionUiState> = _uiState.asStateFlow()

    val history: StateFlow<List<PredictionEntity>> = repository.predictions
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun setSelectedImage(uri: Uri?) {
        _uiState.value = _uiState.value.copy(
            selectedImageUri = uri,
            result = null,
            error = null
        )
    }

    fun predict(imageFile: File) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            val result = repository.predict(imageFile)
            result.fold(
                onSuccess = { response ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        result = response
                    )
                },
                onFailure = { exception ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = exception.message ?: "Error desconocido"
                    )
                }
            )
        }
    }

    fun clearHistory() {
        viewModelScope.launch {
            repository.clearHistory()
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
