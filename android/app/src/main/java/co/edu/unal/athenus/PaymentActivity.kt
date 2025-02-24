package co.edu.unal.athenus


import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import com.google.android.material.navigation.NavigationView
import com.stripe.android.PaymentConfiguration
import com.stripe.android.paymentsheet.PaymentSheet
import com.stripe.android.paymentsheet.PaymentSheetResult

class PaymentActivity : AppCompatActivity() {
    private lateinit var paymentSheet: PaymentSheet
    private var customerId: String? = null
    private var ephemeralKey: String? = null
    private var clientSecret: String? = null
    //private val stripePublishableKey: String by lazy {
        //getString(R.string.stripe_publishable_key)}
    private lateinit var btnPersonal: Button
    private lateinit var btnEmpresarial: Button
    private lateinit var layoutPersonal: LinearLayout
    private lateinit var layoutEmpresarial: LinearLayout
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_payment)

        // Inicializar elementos
        btnPersonal = findViewById(R.id.btn_personal)
        btnEmpresarial = findViewById(R.id.btn_empresarial)
        layoutPersonal = findViewById(R.id.personal)
        layoutEmpresarial = findViewById(R.id.empresarial)
        btnPersonal.setTextColor(ContextCompat.getColor(this, android.R.color.white))
        btnPersonal.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_light))

        // Acción al presionar "Personal"
        btnPersonal.setOnClickListener {
            layoutPersonal.visibility = LinearLayout.VISIBLE
            layoutEmpresarial.visibility = LinearLayout.GONE
            btnPersonal.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_light))
            btnEmpresarial.setBackgroundColor(Color.LTGRAY)
            btnPersonal.setTextColor(ContextCompat.getColor(this, android.R.color.white))
            btnEmpresarial.setTextColor(Color.BLACK)
        }

        // Acción al presionar "Empresarial"
        btnEmpresarial.setOnClickListener {
            layoutPersonal.visibility = LinearLayout.GONE
            layoutEmpresarial.visibility = LinearLayout.VISIBLE
            btnEmpresarial.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_light))
            btnPersonal.setBackgroundColor(Color.LTGRAY)
            btnEmpresarial.setTextColor(ContextCompat.getColor(this, android.R.color.white))
            btnPersonal.setTextColor(Color.BLACK)

        }

        drawerLayout = findViewById(R.id.drawer_layout) // Correcto
        val navigationView: NavigationView = findViewById(R.id.navigation_view) // Correcto
        navigationView.setNavigationItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_chat -> {
                    drawerLayout.closeDrawer(GravityCompat.START)
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                }

                R.id.nav_settings -> {

                }
            }
            drawerLayout.closeDrawer(GravityCompat.START) // Cierra el menú después de la selección
            true
        }
    }
}
//        PaymentConfiguration.init(this, stripePublishableKey)
//
//        paymentSheet = PaymentSheet(this, ::onPaymentSheetResult)
//
//        val plan = intent.getStringExtra("plan")
//        val amount = intent.getStringExtra("amount")
//
//        // Simulación de obtener credenciales desde el backend
//        fetchPaymentIntent(amount ?: "2")
//
//        findViewById<Button>(R.id.pay_button).setOnClickListener {
//            customerId?.let { id ->
//                ephemeralKey?.let { key ->
//                    clientSecret?.let { secret ->
//                        paymentSheet.presentWithPaymentIntent(
//                            secret,
//                            PaymentSheet.Configuration(
//                                "Tu Empresa",
//                                customer = PaymentSheet.CustomerConfiguration(id, key)
//                            )
//                        )
//                    }
//                }
//            }
//        }
//        findViewById<Button>(R.id.btn_pagar_accesible).setOnClickListener {
//            iniciarPago("Accesible", "2")
//        }
//
//        findViewById<Button>(R.id.btn_pagar_plus).setOnClickListener {
//            iniciarPago("Plus", "20")
//        }
//
//        findViewById<Button>(R.id.btn_pagar_team).setOnClickListener {
//            iniciarPago("Team", "70")
//        }
//    }
//    private fun fetchPaymentIntent(amount: String) {
//        // Aquí debes llamar a tu backend para obtener clientSecret, customerId y ephemeralKey
//        customerId = "cus_test" // Simulación
//        ephemeralKey = "ek_test" // Simulación
//        clientSecret = "pi_test_secret" // Simulación
//    }
//    private fun onPaymentSheetResult(paymentSheetResult: PaymentSheetResult) {
//        when (paymentSheetResult) {
//            is PaymentSheetResult.Completed -> {
//                // Manejar pago exitoso
//            }
//            is PaymentSheetResult.Failed -> {
//                // Manejar fallo de pago
//            }
//            is PaymentSheetResult.Canceled -> {
//                // Manejar cancelación
//            }
//        }
//    }
//    private fun iniciarPago(plan: String, amount: String) {
//        val intent = Intent(this, PaymentActivity::class.java)
//        intent.putExtra("plan", plan)
//        intent.putExtra("amount", amount)
//        startActivity(intent)
//    }
//}
