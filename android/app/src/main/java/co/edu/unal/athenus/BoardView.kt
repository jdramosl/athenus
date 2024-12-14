package co.edu.unal.athenus

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Rect
import android.util.AttributeSet
import android.view.View

class BoardView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyle: Int = 0
) : View(context, attrs, defStyle) {

    // Constante para el ancho de las líneas del tablero
    companion object {
        const val GRID_WIDTH = 6
    }

    // Bitmaps para las X y O
    private var mHumanBitmap: Bitmap? = null
    private var mComputerBitmap: Bitmap? = null

    private lateinit var mPaint: Paint

    private var mGame: TicTacToeGame? = null

    init {
        initialize()
    }

    // Método para inicializar los recursos
    private fun initialize() {
        // Cargar las imágenes desde los recursos
        mHumanBitmap = BitmapFactory.decodeResource(resources, R.drawable.x)
        mComputerBitmap = BitmapFactory.decodeResource(resources, R.drawable.o_v)

        mPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Determinar el ancho y alto de la vista
        val boardWidth = width
        val boardHeight = height

        // Configurar las líneas del tablero
        mPaint.color = Color.LTGRAY
        mPaint.strokeWidth = GRID_WIDTH.toFloat()

        // Dibujar las dos líneas verticales
        val cellWidth = boardWidth / 3
        canvas.drawLine(cellWidth.toFloat(), 0f, cellWidth.toFloat(), boardHeight.toFloat(), mPaint)
        canvas.drawLine((cellWidth * 2).toFloat(), 0f, (cellWidth * 2).toFloat(), boardHeight.toFloat(), mPaint)

        // Dibujar las dos líneas horizontales
        val cellHeight = boardHeight / 3
        canvas.drawLine(0f, cellHeight.toFloat(), boardWidth.toFloat(), cellHeight.toFloat(), mPaint)
        canvas.drawLine(0f, (cellHeight * 2).toFloat(), boardWidth.toFloat(), (cellHeight * 2).toFloat(), mPaint)

        // Dibujar las piezas X y O
        for (i in 0 until (mGame?.boarD_SIZE ?: 9)) {
            val col = i % 3
            val row = i / 3
            val left = col * cellWidth
            val top = row * cellHeight
            val right = left + cellWidth
            val bottom = top + cellHeight

            // Verificar si la celda está ocupada por un jugador
            when (mGame?.getBoardOccupant(i)) {
                TicTacToeGame.HUMAN_PLAYER -> {
                    mHumanBitmap?.let { canvas.drawBitmap(it, null, Rect(left, top, right, bottom), null) }
                }
                TicTacToeGame.COMPUTER_PLAYER -> {
                    mComputerBitmap?.let { canvas.drawBitmap(it, null, Rect(left, top, right, bottom), null) }
                }
            }
        }

    }

    override fun performClick(): Boolean {
        super.performClick() // Llama a la implementación de la superclase para que el comportamiento estándar también sea ejecutado
        // Puedes agregar aquí lógica adicional si es necesario
        return true
    }

    fun setGame(game: TicTacToeGame) {
        mGame = game
        mGame?.clearBoard()  // Asegúrate de inicializar el tablero
        invalidate() // Redibuja la vista para reflejar los cambios
    }

    // Accesores para obtener el tamaño de las celdas
    fun getBoardCellWidth(): Int {
        return width / 3
    }

    fun getBoardCellHeight(): Int {
        return height / 3
    }
}
