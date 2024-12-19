package co.edu.unal.athenus.model

data class Message(
    val text: String,
    val isUser: Boolean // true si el mensaje es del usuario, false si es del asistente
)
