package co.edu.unal.athenus

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message
import io.noties.markwon.Markwon
import okhttp3.*
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity(), WhisperManager.WhisperCallback {

    private lateinit var binding: ActivityMainBinding
    private val messages = mutableListOf<Message>()
    private lateinit var adapter: MessageAdapter
    private lateinit var whisperManager: WhisperManager
    private val audioRecordingPermissionCode = 101
    private val TAG = "MainActivity"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        initializeUI()
        setupWhisperManager()
        setupClickListeners()
    }

    private fun initializeUI() {
        adapter = MessageAdapter(messages)
        binding.recyclerViewMessages?.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewMessages?.adapter = adapter
    }

    private fun setupWhisperManager() {
        whisperManager = WhisperManager(this)
        whisperManager.setCallback(this)
    }

    private fun setupClickListeners() {
        binding.buttonSend?.setOnClickListener {
            val userMessage = binding.editTextMessage?.text.toString()
            if (userMessage.isNotBlank()) {
                sendMessage(userMessage)
            }
        }

        binding.buttonMic?.setOnClickListener {
            if (checkPermissions()) {
                if (!whisperManager.isRecording()) {
                    whisperManager.startRecording()
                    binding.buttonMic?.setColorFilter(ContextCompat.getColor(this, R.color.colorAccent))
                } else {
                    whisperManager.stopRecording()
                    binding.buttonMic?.clearColorFilter()
                }
            }
        }
    }

    private fun sendMessage(userMessage: String) {
        messages.add(Message(userMessage, true))
        adapter.notifyDataSetChanged()
        binding.buttonSend?.isEnabled = false
        binding.buttonSend?.text = "Loading..."
        sendPostRequest(userMessage)
        binding.editTextMessage?.text?.clear()
    }

    private fun sendPostRequest(userMessage: String) {
        val url = "https://ae55-2a09-bac5-26f9-10f-00-1b-26b.ngrok-free.app/api/company/employees/4/chatbot/"

        val client = OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
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
                handleRequestFailure(e)
            }

            override fun onResponse(call: Call, response: Response) {
                handleRequestResponse(response)
            }
        })
    }

    private fun handleRequestFailure(e: IOException) {
        runOnUiThread {
            binding.buttonSend?.isEnabled = true
            binding.buttonSend?.text = "Send"
            messages.add(Message("Error: ${e.message}", false))
            adapter.notifyDataSetChanged()
        }
    }

    private fun handleRequestResponse(response: Response) {
        if (response.isSuccessful) {
            val responseBody = response.body?.string()
            responseBody?.let {
                try {
                    val jsonObject = JSONObject(it)
                    val answer = jsonObject.getJSONObject("chatbot_response").getString("answer")
                    val employeeName = jsonObject.getString("employee")
                    updateUIWithResponse(employeeName, answer)
                } catch (e: Exception) {
                    handleJsonParseError(e)
                }
            }
        } else {
            handleRequestError(response)
        }
    }

    private fun updateUIWithResponse(employeeName: String, answer: String) {
        runOnUiThread {
            val markwon = Markwon.create(binding.root.context)
            val markdownText = markwon.toMarkdown(answer)
            
            binding.buttonSend?.isEnabled = true
            binding.buttonSend?.text = "Send"
            
            messages.add(Message("Hi $employeeName, $answer", false))
            adapter.notifyDataSetChanged()
            binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)
        }
    }

    private fun handleJsonParseError(e: Exception) {
        runOnUiThread {
            binding.buttonSend?.isEnabled = true
            binding.buttonSend?.text = "Send"
            messages.add(Message("Error processing JSON: ${e.message}", false))
            adapter.notifyDataSetChanged()
        }
    }

    private fun handleRequestError(response: Response) {
        runOnUiThread {
            binding.buttonSend?.isEnabled = true
            binding.buttonSend?.text = "Send"
            messages.add(Message("Response error: $response", false))
            adapter.notifyDataSetChanged()
        }
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

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == audioRecordingPermissionCode) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                binding.buttonMic?.performClick()
            }
        }
    }

    // WhisperCallback Implementation
    override fun onTranscriptionStarted() {
        runOnUiThread {
            binding.editTextMessage?.hint = "Transcribing audio..."
            binding.editTextMessage?.isEnabled = false
            binding.buttonSend?.isEnabled = false
            binding.buttonMic?.isEnabled = false
        }
    }

    override fun onTranscriptionResult(text: String) {
        runOnUiThread {
            binding.editTextMessage?.setText(text)
            binding.editTextMessage?.isEnabled = true
            binding.buttonSend?.isEnabled = true
            binding.buttonMic?.isEnabled = true
        }
    }

    override fun onTranscriptionCompleted() {
        runOnUiThread {
            binding.editTextMessage?.hint = "Type your message"
            binding.editTextMessage?.isEnabled = true
            binding.buttonSend?.isEnabled = true
            binding.buttonMic?.isEnabled = true
        }
    }

    override fun onError(error: String) {
        runOnUiThread {
            Log.e(TAG, "Whisper error: $error")
            binding.editTextMessage?.hint = "Type your message"
            binding.editTextMessage?.isEnabled = true
            binding.buttonSend?.isEnabled = true
            binding.buttonMic?.isEnabled = true
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        whisperManager.cleanup()
    }
}