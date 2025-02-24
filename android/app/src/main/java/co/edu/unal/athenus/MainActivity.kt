package co.edu.unal.athenus

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message
import com.google.android.material.navigation.NavigationView
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit


class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val messages = mutableListOf<Message>()
    private lateinit var adapter: MessageAdapter
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize View Binding
        val prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE)
        val isLoggedIn = prefs.getBoolean("isLoggedIn", false)

        if (!isLoggedIn) {
            val intent = Intent(
                this@MainActivity,
                LoginActivity::class.java
            )
            startActivity(intent)
            finish()
        } else {

            binding = ActivityMainBinding.inflate(layoutInflater)
            setContentView(binding.root)

            // Initialize RecyclerView and Adapter
            adapter = MessageAdapter(messages)
            binding.recyclerViewMessages?.layoutManager = LinearLayoutManager(this)
            binding.recyclerViewMessages?.adapter = adapter
            // Handle Send Button Click

            //
            val textViewWelcome: TextView = findViewById(R.id.textViewWelcome)
            val recyclerViewMessages: RecyclerView = findViewById(R.id.recyclerViewMessages)


            recyclerViewMessages.adapter?.registerAdapterDataObserver(object : RecyclerView.AdapterDataObserver() {
                override fun onChanged() {
                    if (recyclerViewMessages.adapter?.itemCount == 0) {
                        textViewWelcome.visibility = View.VISIBLE
                    }
                    else {
                        textViewWelcome.visibility = View.GONE
                    }
                }
            })
            drawerLayout = findViewById(R.id.drawer_layout) // Correcto
            val navigationView: NavigationView  = findViewById(R.id.navigation_view) // Correcto
            navigationView.setNavigationItemSelectedListener { item ->
                when (item.itemId) {
                    R.id.nav_chat -> {

                    }

                    R.id.nav_settings -> {
                        drawerLayout.closeDrawer(GravityCompat.START)
                        val intent = Intent(this, PaymentActivity::class.java)
                        startActivity(intent)
                    }
                }
                drawerLayout.closeDrawer(GravityCompat.START) // Cierra el menú después de la selección
                true
            }
            //
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
    }
    private fun getAuthToken(): String? {
        val sharedPreferences = getSharedPreferences("MyPrefs", MODE_PRIVATE)
        return sharedPreferences.getString("auth_token", null) // Devuelve null si no existe
    }


    private fun iniciarPago(plan: String, amount: String) {
        val intent = Intent(this, PaymentActivity::class.java)
        intent.putExtra("plan", plan)
        intent.putExtra("amount", amount)
        startActivity(intent)
    }
    val client = OkHttpClient.Builder()
    .connectTimeout(120, TimeUnit.SECONDS)
    .readTimeout(120, TimeUnit.SECONDS)
    .writeTimeout(120, TimeUnit.SECONDS)
    .build()


    private fun sendPostRequest(userMessage: String) {
        val prefs = applicationContext.getSharedPreferences("AppPrefs", MODE_PRIVATE)
        val token = prefs.getString("auth_token", null)
        val url = "https://2f58-186-31-184-101.ngrok-free.app/api/company/messages/"

        // Construir el JSON con los datos requeridos
        val json = JSONObject().apply {
            put("role", "tecnologia")
            put("message", userMessage)
            put("model", 4)
        }

        // Definir el tipo de contenido JSON
        val mediaType = "application/json".toMediaType()
        val requestBody = RequestBody.create(mediaType, json.toString())

        // Construir la solicitud con los encabezados requeridos
        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("Authorization", "Token $token") // Usa el token obtenido
            .addHeader("Content-Type", "application/json")
            .addHeader("X-CSRFToken", "2HHcrmprlo3Sfngt3L7Uno6wLzSWIlUFjRD5Vfodf86KpPTHDoSO1Gz10x5fbw8B")
            .build()

        // Usa el cliente global con timeout configurado
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    messages.add(Message("Error: ${e.message}", false))
                    adapter.notifyDataSetChanged()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                runOnUiThread {
                    if (response.isSuccessful && responseBody != null) {
                        try {
                            val jsonResponse = JSONObject(responseBody)
                            val modelMessage = jsonResponse.getJSONObject("model_response").getString("content")

                            // Agregar solo el mensaje extraído a la lista
                            messages.add(Message(modelMessage, false))
                        } catch (e: Exception) {
                            messages.add(Message("Error al procesar la respuesta", false))
                        }
                    } else {
                        messages.add(Message("Error en la respuesta: ${response.message}", false))
                    }
                    adapter.notifyDataSetChanged()
                    binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)
                }
            }

        })
    }
}
