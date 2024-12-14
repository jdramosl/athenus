package co.edu.unal.athenus

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import co.edu.unal.athenus.adapter.MessageAdapter
import co.edu.unal.athenus.databinding.ActivityMainBinding
import co.edu.unal.athenus.model.Message

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

                // Simulate assistant response
                messages.add(Message("This is a dummy response.", false))

                // Notify adapter and scroll to the latest message
                adapter.notifyDataSetChanged()
                binding.recyclerViewMessages?.scrollToPosition(messages.size - 1)

                // Clear the input field
                binding.editTextMessage?.text?.clear()
            }
        }
    }
}
