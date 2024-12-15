package co.edu.unal.athenus

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message
import okhttp3.*
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val messages = mutableListOf<Message>()
    private lateinit var adapter: MessageAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize View Binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize RecyclerView and Adapter
        adapter = MessageAdapter(messages)
        binding.recyclerViewMessages?.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewMessages?.adapter = adapter

        // Handle Send Button Click
        binding.buttonSend?.setOnClickListener {
            val userMessage = binding.editTextMessage?.text.toString()
            if (userMessage.isNotBlank()) {
                // Add user message
                messages.add(Message(userMessage, true))
                adapter.notifyDataSetChanged()

                // Hacer petición POST al endpoint
                sendPostRequest(userMessage)

                // Limpiar el campo de entrada
                binding.editTextMessage?.text?.clear()
            }
        }
    }

    private fun sendPostRequest(userMessage: String) {
        val url = "http://10.0.2.2:8080/llm"
        val client = OkHttpClient()

        val requestBody = FormBody.Builder()
            .add("message", userMessage)
            .build()

        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                // Manejar errores de red
                runOnUiThread {
                    messages.add(Message("Error: ${e.message}", false))
                    adapter.notifyDataSetChanged()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    runOnUiThread {
                        messages.add(Message(responseBody ?: "Respuesta vacía", false))
                        adapter.notifyDataSetChanged()
                        binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)
                    }
                } else {
                    runOnUiThread {
                        messages.add(Message("Error en la respuesta: ${response.message}", false))
                        adapter.notifyDataSetChanged()
                    }
                }
            }
        })
    }
}
