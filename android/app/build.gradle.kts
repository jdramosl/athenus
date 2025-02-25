plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "co.edu.unal.athenus"
    compileSdk = 35

    defaultConfig {
        applicationId = "co.edu.unal.athenus"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            abiFilters.addAll(listOf("armeabi-v7a", "arm64-v8a"))
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    externalNativeBuild {
        cmake {
            path("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }
    ndkVersion = "25.2.9519653"
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        compose = true
        viewBinding = true
    }

    packaging {
        jniLibs.pickFirsts.add("lib/arm64-v8a/libtensorflowlite.so")
    }
}

dependencies {
    implementation(libs.stripe.android)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.material)
    implementation(libs.androidx.recyclerview)
    implementation(libs.core)
    // https://mvnrepository.com/artifact/com.squareup.okhttp3/okhttp
    implementation(libs.okhttp)
    implementation(libs.androidx.room.compiler)
    testImplementation(libs.junit)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.constraintlayout)
    // Main TensorFlow Lite libraries declaradas en HEAD:
    implementation(libs.tensorflow.lite.v2130)
    implementation(libs.tensorflow.lite.support)
    implementation(libs.tensorflow.lite.metadata)
    implementation(libs.tensorflow.lite.gpu)
    implementation(libs.tensorflow.lite.gpu.delegate.plugin)
    // Además, se agregan las dependencias de TensorFlow Lite provenientes del incoming:
    implementation("org.tensorflow:tensorflow-lite:2.13.0") // Core TensorFlow Lite library
    implementation("org.tensorflow:tensorflow-lite-gpu:2.13.0") // GPU acceleration (solo si se requiere)
    implementation("org.tensorflow:tensorflow-lite-support:0.4.4") // Biblioteca opcional de soporte

    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.jar", "*.so"))))
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
    configurations.all {
        resolutionStrategy {
            force("org.jetbrains:annotations:23.0.0")
            exclude(group = "com.intellij", module = "annotations")
            // Force specific TensorFlow version
            // Exclude conflicting libraries
            exclude(group = "com.google.ai.edge.litert", module = "litert")
            exclude(group = "com.google.ai.edge.litert", module = "litert-api")
        }
    }
}
