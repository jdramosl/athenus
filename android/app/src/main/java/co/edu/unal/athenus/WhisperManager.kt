package co.edu.unal.athenus

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import co.edu.unal.athenus.asr.Whisper
import co.edu.unal.athenus.asr.Recorder
import co.edu.unal.athenus.utils.WaveUtil
import java.io.File
import java.io.FileOutputStream
import java.io.IOException

class WhisperManager(private val context: Context) {
    private var mWhisper: Whisper? = null
    private var selectedTfliteFile: File? = null
    private var sdcardDataFolder: File? = null
    private val handler = Handler(Looper.getMainLooper())
    private var isRecording = false
    private var isTranscribing = false
    private lateinit var recorder: Recorder
    private var wavFile: File? = null
    private val TAG = "WhisperManager"

    interface WhisperCallback {
        fun onTranscriptionStarted()
        fun onTranscriptionResult(text: String)
        fun onTranscriptionCompleted()
        fun onError(error: String)
    }

    private var callback: WhisperCallback? = null

    init {
        sdcardDataFolder = context.getExternalFilesDir(null)
        selectedTfliteFile = File(sdcardDataFolder, "whisper-tiny.tflite")
        copyAssetsToSdcard(arrayOf("tflite", "bin"))
        initRecorder()
        initModel(selectedTfliteFile!!)
    }

    private fun copyAssetsToSdcard(extensions: Array<String>) {
        val assetManager = context.assets
        try {
            assetManager.list("")?.forEach { assetFileName ->
                extensions.forEach { extension ->
                    if (assetFileName.endsWith(".$extension")) {
                        val outFile = File(sdcardDataFolder, assetFileName)
                        if (!outFile.exists()) {
                            assetManager.open(assetFileName).use { input ->
                                FileOutputStream(outFile).use { output ->
                                    input.copyTo(output)
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

    private fun initRecorder() {
        recorder = Recorder(context).apply {
            setListener(object : Recorder.RecorderListener {
                override fun onUpdateReceived(message: String) {
                    when (message) {
                        Recorder.MSG_RECORDING_DONE -> {
                            handler.post { processAudio() }
                        }
                    }
                }

                override fun onDataReceived(samples: FloatArray) {
                    mWhisper?.writeBuffer(samples)
                }
            })
        }
    }

    private fun initModel(modelFile: File) {
        val isMultilingualModel = !modelFile.name.endsWith(".en.tflite")
        val vocabFileName = if (isMultilingualModel) "filters_vocab_multilingual.bin" else "filters_vocab_en.bin"
        val vocabFile = File(sdcardDataFolder, vocabFileName)

        mWhisper = Whisper(context)
        mWhisper?.loadModel(modelFile, vocabFile, isMultilingualModel)
        mWhisper?.setListener(object : Whisper.WhisperListener {
            override fun onUpdateReceived(message: String) {
                handler.post {
                    if (message == Whisper.MSG_PROCESSING_DONE) {
                        isTranscribing = false
                        callback?.onTranscriptionCompleted()
                    }
                }
            }

            override fun onResultReceived(result: String) {
                isTranscribing = false
                handler.post {
                    callback?.onTranscriptionResult(result)
                }
            }
        })
    }

    fun startRecording() {
        wavFile = File(sdcardDataFolder, WaveUtil.RECORDING_FILE)
        recorder.setFilePath(wavFile?.absolutePath)
        recorder.start()
        isRecording = true
    }

    fun stopRecording() {
        if (isRecording) {
            recorder.stop()
            isRecording = false
        }
    }

    private fun processAudio() {
        if (wavFile?.exists() == true) {
            isTranscribing = true
            callback?.onTranscriptionStarted()
            
            mWhisper?.let { whisper ->
                whisper.setFilePath(wavFile!!.absolutePath)
                whisper.setAction(Whisper.ACTION_TRANSCRIBE)
                whisper.start()
            }
        }
    }

    fun setCallback(callback: WhisperCallback) {
        this.callback = callback
    }

    fun isRecording(): Boolean = isRecording

    fun isTranscribing(): Boolean = isTranscribing

    fun cleanup() {
        mWhisper?.unloadModel()
        mWhisper = null
        wavFile?.delete()
    }
}