package co.edu.unal.athenus;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LoginActivity extends AppCompatActivity {

    private static final String LOGIN_URL = "https://2f58-186-31-184-101.ngrok-free.app/api/user/token/";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        TextView tvGoToRegister = findViewById(R.id.tvGoToRegister);
        tvGoToRegister.setOnClickListener(v -> {
            Intent intent = new Intent(LoginActivity.this, RegisterActivity.class);
            startActivity(intent);
        });

        EditText etemail = findViewById(R.id.etUsername);
        EditText etPassword = findViewById(R.id.etPassword);
        Button btnLogin = findViewById(R.id.btnLogin);

        btnLogin.setOnClickListener(v -> {
            String email = etemail.getText().toString();
            String password = etPassword.getText().toString();

            if (email.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "Por favor ingrese usuario y contraseña", Toast.LENGTH_SHORT).show();
                return;
            }

            loginUser(email, password);
        });
    }

    private void loginUser(String email, String password) {
        OkHttpClient client = new OkHttpClient();

        try {
            JSONObject json = new JSONObject();
            json.put("email", email);
            json.put("password", password);

            RequestBody body = RequestBody.create(json.toString(), JSON);
            Request request = new Request.Builder()
                    .url(LOGIN_URL)
                    .post(body)
                    .build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    runOnUiThread(() -> Toast.makeText(LoginActivity.this, "Error de conexión", Toast.LENGTH_SHORT).show());
                }

                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    if (response.isSuccessful() && response.body() != null) {
                        String responseBody = response.body().string();
                        Log.d("TOKEN_DEBUG", "Respuesta completa del servidor: " + responseBody);

                        try {
                            JSONObject jsonResponse = new JSONObject(responseBody);
                            if (jsonResponse.has("token")) { // Verifica si el JSON tiene el campo "token"
                                String token = jsonResponse.getString("token");
                                Log.d("TOKEN_DEBUG", "Token recibido: " + token);

                                // Guardar el token
                                SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
                                boolean success = prefs.edit().putString("auth_token", token).commit(); // Usa commit() para verificar si se guardó
                                boolean successloggedIn = prefs.edit().putBoolean("isLoggedIn", true).commit();

                                Log.d("TOKEN_DEBUG", "Token guardado correctamente: " + success+successloggedIn);

                                // Redirigir al usuario
                                runOnUiThread(() -> {
                                    Toast.makeText(LoginActivity.this, "Login exitoso", Toast.LENGTH_SHORT).show();
                                    startActivity(new Intent(LoginActivity.this, MainActivity.class));
                                    finish();
                                });

                            } else {
                                Log.e("TOKEN_DEBUG", "El JSON de respuesta no contiene 'token'");
                            }

                        } catch (JSONException e) {
                            Log.e("TOKEN_DEBUG", "Error procesando JSON: ", e);
                        } finally {
                            response.close();
                        }

                    } else {
                        Log.e("TOKEN_DEBUG", "Respuesta fallida del servidor: " + response.message());
                        runOnUiThread(() -> Toast.makeText(LoginActivity.this, "Credenciales incorrectas", Toast.LENGTH_SHORT).show());
                    }
                }
            });
        } catch (Exception e) {
            Log.e("RegisterError", "Error en la solicitud", e);
            Toast.makeText(this, "Error en la solicitud", Toast.LENGTH_SHORT).show();
        }
    }
}

