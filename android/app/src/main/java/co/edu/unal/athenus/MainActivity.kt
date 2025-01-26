package co.edu.unal.athenus

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message
import io.noties.markwon.Markwon
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import org.json.JSONObject
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
        val url = "https://ae55-2a09-bac5-26f9-10f-00-1b-26b.ngrok-free.app/api/company/employees/4/chatbot/"

        // Configurar el cliente con tiempos de espera
        val client = OkHttpClient.Builder()
            .connectTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .build()

        val requestBody = FormBody.Builder()
            .add("message", userMessage)
            .build()

        val request = Request.Builder()
            .header("Authorization", "Token 07d5ab3e1e69ce896946ecf0d76803a8236da06c")
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
                    if (responseBody != null) {
                        try {
                            // Analizar JSON y obtener la propiedad "answer"
                            val jsonObject = JSONObject(responseBody)
                            val answer = jsonObject.getJSONObject("chatbot_response").getString("answer")
                            val employeeName = jsonObject.getString("employee")
                            val markwon = Markwon.create(binding.root.context)
                            val markdownText = markwon.toMarkdown(answer)

                            // Mostrar como Markdown (Usando Markwon)
                            runOnUiThread {
                                val markdownMessage = Message("Hi " +employeeName+", "+answer, false)
                                messages.add(markdownMessage)
                                adapter.notifyDataSetChanged()

                                // Scroll a la última posición
                                binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)
                            }
                        } catch (e: Exception) {
                            runOnUiThread {
                                messages.add(Message("Error al procesar el JSON: ${e.message}", false))
                                adapter.notifyDataSetChanged()
                            }
                        }
                    }
                } else {
                    runOnUiThread {
                        messages.add(Message("Error en la respuesta: ${response}", false))
                        adapter.notifyDataSetChanged()
                    }
                }
            }
        })
    }
}
