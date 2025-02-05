package co.edu.unal.athenus

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.MotionEvent
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message
import co.edu.unal.athenus.asr.Whisper
import co.edu.unal.athenus.utils.WaveUtil
import io.noties.markwon.Markwon
import okhttp3.*
import java.io.File
import java.io.IOException
import android.content.res.AssetManager
import co.edu.unal.athenus.asr.Recorder
import org.json.JSONObject
import java.io.FileOutputStream
import java.io.InputStream
import java.io.OutputStream

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val messages = mutableListOf<Message>()
    private lateinit var adapter: MessageAdapter
    
    // Whisper-related properties
    private var mWhisper: Whisper? = null
    private var selectedTfliteFile: File? = null
    private var sdcardDataFolder: File? = null
    private val handler = Handler(Looper.getMainLooper())

    // recording-related properties
    private var isRecording = false
    private val audioRecordingPermissionCode = 101
    private var isTranscribing = false
    private val TAG = "MainActivity"
    
    // Add new properties
    private lateinit var recorder: Recorder
    private var wavFile: File? = null

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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize View Binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize RecyclerView and adapter
        adapter = MessageAdapter(messages)
        binding.recyclerViewMessages?.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewMessages?.adapter = adapter

        // Setup data folder and copy necessary files
        sdcardDataFolder = getExternalFilesDir(null)
        copyAssetsToSdcard(arrayOf("tflite", "bin", "wav", "pcm"))
        
        // Initialize Whisper with proper file paths
        selectedTfliteFile = File(sdcardDataFolder, "whisper-tiny.tflite")
        initModel(selectedTfliteFile!!)
        
        // Handle Send Button Click
        binding.buttonSend?.setOnClickListener {
            val userMessage = binding.editTextMessage?.text.toString()
            if (userMessage.isNotBlank()) {
                messages.add(Message(userMessage, true))
                adapter.notifyDataSetChanged()
                binding.buttonSend?.isEnabled = false
                binding.buttonSend?.text = "Loading..."
                sendPostRequest(userMessage)
                binding.editTextMessage?.text?.clear()
            }
        }
        // Add mic button listener
        binding.buttonMic?.setOnClickListener {
            if (!isRecording) {
                // Start recording
                if (checkPermissions()) {
                    startRecording()
                    binding.buttonMic?.setColorFilter(ContextCompat.getColor(this, R.color.colorAccent))
                }
            } else {
                // Stop recording
                stopRecording()
                binding.buttonMic?.clearColorFilter()
                processAudio()
            }
        }

        // Initialize Recorder
        recorder = Recorder(this).apply {
            setListener(object : Recorder.RecorderListener {
                override fun onUpdateReceived(message: String) {
                    Log.d(TAG, "Recorder update: $message")
                    when (message) {
                        Recorder.MSG_RECORDING_DONE -> {
                            handler.post { processAudio() }
                        }
                    }
                }

                override fun onDataReceived(samples: FloatArray) {
                    // Send live samples to Whisper if needed
                    mWhisper?.writeBuffer(samples)
                }
            })
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

    override fun onDestroy() {
        super.onDestroy()
        deinitModel()
        // Clean up temporary files
        wavFile?.delete()
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
                runOnUiThread {
                    binding.buttonSend?.isEnabled = true
                    binding.buttonSend?.text = "Send"
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
                                binding.buttonSend?.isEnabled = true
                                binding.buttonSend?.text = "Send"
                                val markdownMessage = Message("Hi " +employeeName+", "+answer, false)
                                messages.add(markdownMessage)
                                adapter.notifyDataSetChanged()

                                // Scroll a la última posición
                                binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)
                            }
                        } catch (e: Exception) {
                            runOnUiThread {
                                binding.buttonSend?.isEnabled = true
                                binding.buttonSend?.text = "Send"
                                messages.add(Message("Error al procesar el JSON: ${e.message}", false))
                                adapter.notifyDataSetChanged()
                            }
                        }
                    }
                } else {
                    runOnUiThread {
                        binding.buttonSend?.isEnabled = true
                        binding.buttonSend?.text = "Send"
                        messages.add(Message("Error en la respuesta: ${response}", false))
                        adapter.notifyDataSetChanged()
                    }
                }
            }
        })
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
                audioRecordingPermissionCode
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
            binding.buttonMic?.isEnabled = false
            Log.d(TAG, "Recording started")
        }
    }

    private fun stopRecording() {
        if (isRecording) {
            recorder.stop()
            isRecording = false
            binding.buttonMic?.isEnabled = true
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

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == audioRecordingPermissionCode) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted
            }
        }
    }
}
