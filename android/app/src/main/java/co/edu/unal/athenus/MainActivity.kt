package co.edu.unal.athenus

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.navigation.NavigationView
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.Response
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.concurrent.TimeUnit

import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message

// --- Partes añadidas para uso de Whisper ---
import co.edu.unal.athenus.asr.Whisper
import co.edu.unal.athenus.asr.Recorder
import co.edu.unal.athenus.utils.WaveUtil
// ----------------------------------------------

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val messages = mutableListOf<Message>()
    private lateinit var adapter: MessageAdapter
    private lateinit var drawerLayout: DrawerLayout

    // --- Propiedades relacionadas a Whisper (añadidas del incoming) ---
    private var mWhisper: Whisper? = null
    private var selectedTfliteFile: File? = null
    private var sdcardDataFolder: File? = null
    private val handler = Handler(Looper.getMainLooper())
    private var isRecording = false
    private var isTranscribing = false
    private val TAG = "MainActivity"
    private lateinit var recorder: Recorder
    private var wavFile: File? = null
    // -----------------------------------------------------------------

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE)
        val isLoggedIn = prefs.getBoolean("isLoggedIn", false)

        if (!isLoggedIn) {
            val intent = Intent(this@MainActivity, LoginActivity::class.java)
            startActivity(intent)
            finish()
        } else {
            binding = ActivityMainBinding.inflate(layoutInflater)
            setContentView(binding.root)

            // Inicializar RecyclerView y Adapter
            adapter = MessageAdapter(messages)
            binding.recyclerViewMessages?.layoutManager = LinearLayoutManager(this)
            binding.recyclerViewMessages?.adapter = adapter

            // Configurar bienvenida
            val textViewWelcome: TextView = findViewById(R.id.textViewWelcome)
            val recyclerViewMessages: RecyclerView = findViewById(R.id.recyclerViewMessages)
            recyclerViewMessages.adapter?.registerAdapterDataObserver(object : RecyclerView.AdapterDataObserver() {
                override fun onChanged() {
                    textViewWelcome.visibility = if (recyclerViewMessages.adapter?.itemCount == 0)
                        View.VISIBLE else View.GONE
                }
            })

            drawerLayout = findViewById(R.id.drawer_layout)
            val navigationView: NavigationView = findViewById(R.id.navigation_view)
            navigationView.setNavigationItemSelectedListener { item ->
                when (item.itemId) {
                    R.id.nav_chat -> { /* ... */ }
                    R.id.nav_settings -> {
                        drawerLayout.closeDrawer(GravityCompat.START)
                        val intent = Intent(this, PaymentActivity::class.java)
                        startActivity(intent)
                    }
                }
                drawerLayout.closeDrawer(GravityCompat.START)
                true
            }
            
            // --- Inicialización de Whisper ---
            sdcardDataFolder = getExternalFilesDir(null)
            copyAssetsToSdcard(arrayOf("tflite", "bin", "wav", "pcm"))
            selectedTfliteFile = File(sdcardDataFolder, "whisper-tiny.tflite")
            initModel(selectedTfliteFile!!)
            // ----------------------------------

            // Configurar botón Send
            binding.buttonSend?.setOnClickListener {
                val userMessage = binding.editTextMessage?.text.toString()
                if (userMessage.isNotBlank()) {
                    messages.add(Message(userMessage, true))
                    adapter.notifyDataSetChanged()
                    sendPostRequest(userMessage)
                    binding.editTextMessage?.text?.clear()
                }
            }
        }

        // Configurar botón Mic para iniciar/terminar grabación y proceso de audio (Whisper)
        binding.buttonMic?.setOnClickListener {
            if (!isRecording && !isTranscribing) {
                if (checkPermissions()) {
                    startRecording()
                    binding.buttonMic?.setColorFilter(
                        ContextCompat.getColor(this, R.color.colorAccent)
                    )
                }
            } else if (isRecording) {
                stopRecording()
                binding.buttonMic?.clearColorFilter()
                processAudio()
            }
        }

        // Inicializar Recorder con su listener para integrar Whisper
        recorder = Recorder(this).apply {
            setListener(object : Recorder.RecorderListener {
                override fun onUpdateReceived(message: String) {
                    Log.d(TAG, "Recorder update: $message")
                    if (message == Recorder.MSG_RECORDING_DONE) {
                        handler.post { processAudio() }
                    }
                }
                override fun onDataReceived(samples: FloatArray) {
                    mWhisper?.writeBuffer(samples)
                }
            })
        }
    }

    // --- Métodos relacionados a Whisper (añadidos del incoming) ---

    private fun copyAssetsToSdcard(extensions: Array<String>) {
        val assetManager = assets
        try {
            val assetFiles = assetManager.list("")
            assetFiles?.forEach { assetFileName ->
                extensions.forEach { extension ->
                    if (assetFileName.endsWith(".$extension")) {
                        val outFile = File(sdcardDataFolder, assetFileName)
                        if (!outFile.exists()) {
                            assetManager.open(assetFileName).use { inputStream ->
                                FileOutputStream(outFile).use { outputStream ->
                                    inputStream.copyTo(outputStream)
                                }
                            }
                        }
                    }
                }
            }
        } catch (e: IOException) {
            Log.e(TAG, "Failed to copy assets", e)
        }
    }

    private fun initModel(modelFile: File) {
        val isMultilingualModel = !modelFile.name.endsWith(".en.tflite")
        val vocabFileName = if (isMultilingualModel) "filters_vocab_multilingual.bin" else "filters_vocab_en.bin"
        val vocabFile = File(sdcardDataFolder, vocabFileName)

        mWhisper = Whisper(this)
        mWhisper?.loadModel(modelFile, vocabFile, isMultilingualModel)
        mWhisper?.setListener(object : Whisper.WhisperListener {
            override fun onUpdateReceived(message: String) {
                Log.d(TAG, "Update: $message")
                handler.post {
                    if (message == Whisper.MSG_PROCESSING_DONE) {
                        isTranscribing = false
                    }
                }
            }
            override fun onResultReceived(result: String) {
                Log.d(TAG, "Transcription result: $result")
                isTranscribing = false
                handler.post {
                    binding.buttonMic?.isEnabled = true
                    binding.editTextMessage?.setText(result)
                    Log.d(TAG, "UI updated with transcription result")
                }
            }
        })
    }

    private fun deinitModel() {
        mWhisper?.unloadModel()
        mWhisper = null
    }

    private fun checkPermissions(): Boolean {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                101
            )
            return false
        }
        return true
    }

    private fun startRecording() {
        if (checkPermissions()) {
            wavFile = File(sdcardDataFolder, WaveUtil.RECORDING_FILE)
            recorder.setFilePath(wavFile?.absolutePath)
            recorder.start()
            isRecording = true
            binding.buttonMic?.isEnabled = true // Mantenemos habilitado para poder alternar
            Log.d(TAG, "Recording started")
        }
    }

    private fun stopRecording() {
        if (isRecording) {
            recorder.stop()
            isRecording = false
            binding.buttonMic?.isEnabled = false // Se deshabilita temporalmente mientras se procesa
            Log.d(TAG, "Recording stopped")
        }
    }

    private fun processAudio() {
        if (wavFile?.exists() == true) {
            isTranscribing = true
            binding.editTextMessage?.hint = "Transcribing audio..."
            binding.editTextMessage?.isEnabled = false
            binding.buttonSend?.isEnabled = false

            mWhisper?.let { whisper ->
                whisper.setListener(object : Whisper.WhisperListener {
                    override fun onUpdateReceived(message: String) {
                        handler.post {
                            if (message == Whisper.MSG_PROCESSING_DONE) {
                                binding.editTextMessage?.hint = "Type your message"
                                binding.editTextMessage?.isEnabled = true
                                binding.buttonSend?.isEnabled = true
                                binding.buttonMic?.isEnabled = true
                                isTranscribing = false
                            }
                        }
                    }
                    override fun onResultReceived(result: String) {
                        handler.post {
                            binding.editTextMessage?.setText(result)
                            binding.editTextMessage?.isEnabled = true
                            binding.buttonSend?.isEnabled = true
                        }
                    }
                })
                whisper.setFilePath(wavFile!!.absolutePath)
                whisper.setAction(Whisper.ACTION_TRANSCRIBE)
                whisper.start()
            }
        }
    }

    private fun startTranscription(filePath: String) {
        if (mWhisper == null) {
            initModel(selectedTfliteFile!!)
        }
        isTranscribing = true
        binding.buttonMic?.isEnabled = false
        binding.buttonSend?.isEnabled = false
        binding.editTextMessage?.hint = "Transcribing audio..."
        binding.editTextMessage?.isEnabled = false
        
        mWhisper?.let { whisper ->
            try {
                whisper.setFilePath(filePath)
                whisper.setAction(Whisper.ACTION_TRANSCRIBE)
                whisper.start()
                Log.d(TAG, "Transcription started")
            } catch (e: Exception) {
                Log.e(TAG, "Transcription failed", e)
                handler.post {
                    binding.editTextMessage?.hint = "Type your message"
                    binding.editTextMessage?.isEnabled = true
                    stopTranscription()
                }
            }
        }
    }

    private fun stopTranscription() {
        Log.d(TAG, "Stopping transcription")
        mWhisper?.stop()
        isTranscribing = false
        binding.buttonMic?.isEnabled = true 
        binding.buttonSend?.isEnabled = true
        Log.d(TAG, "Transcription stopped")
    }
    // -------------------------------------------------------

    override fun onDestroy() {
        super.onDestroy()
        deinitModel()
        wavFile?.delete()
    }

    private fun getAuthToken(): String? {
        val sharedPreferences = getSharedPreferences("MyPrefs", MODE_PRIVATE)
        return sharedPreferences.getString("auth_token", null)
    }

    private fun iniciarPago(plan: String, amount: String) {
        val intent = Intent(this, PaymentActivity::class.java)
        intent.putExtra("plan", plan)
        intent.putExtra("amount", amount)
        startActivity(intent)
    }

    val client: OkHttpClient = OkHttpClient.Builder()
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

        val mediaType = "application/json".toMediaType()
        val requestBody = RequestBody.create(mediaType, json.toString())

        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("Authorization", "Token $token")
            .addHeader("Content-Type", "application/json")
            .addHeader("X-CSRFToken", "2HHcrmprlo3Sfngt3L7Uno6wLzSWIlUFjRD5Vfodf86KpPTHDoSO1Gz10x5fbw8B")
            .build()

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


