package co.edu.unal.athenus;

import java.util.Random;

public class TicTacToeGame {

    // The computer's difficulty levels
    public enum DifficultyLevel {
        Easy, Harder, Expert;

        // Método para obtener un entero asociado al nivel
        public int getValue() {
            switch (this) {
                case Easy:
                    return 0;
                case Harder:
                    return 1;
                case Expert:
                    return 2;
                default:
                    return -1; // Valor por defecto
            }
        }

        // Método para obtener un nivel a partir de un entero
        public static DifficultyLevel fromInt(int value) {
            switch (value) {
                case 0:
                    return Easy;
                case 1:
                    return Harder;
                case 2:
                    return Expert;
                default:
                    return Expert; // Valor por defecto
            }
        }
    }
    // Current difficulty level
    private DifficultyLevel mDifficultyLevel = DifficultyLevel.Expert;
    private final char[] mBoard = {'1','2','3','4','5','6','7','8','9'};
    private final int BOARD_SIZE = 9;

    public static final char HUMAN_PLAYER = 'X';
    public static final char COMPUTER_PLAYER = 'O';

    private final Random mRand;
    public static final char OPEN_SPOT = ' ';


    public TicTacToeGame() {
        mRand = new Random();

    }

    private void displayBoard()	{
        System.out.println();
        System.out.println(mBoard[0] + " | " + mBoard[1] + " | " + mBoard[2]);
        System.out.println("-----------");
        System.out.println(mBoard[3] + " | " + mBoard[4] + " | " + mBoard[5]);
        System.out.println("-----------");
        System.out.println(mBoard[6] + " | " + mBoard[7] + " | " + mBoard[8]);
        System.out.println();
    }

    // Check for a winner.  Return
    //  0 if no winner or tie yet
    //  1 if it's a tie
    //  2 if X won
    //  3 if O won
    public int checkForWinner() {

        // Check horizontal wins
        for (int i = 0; i <= 6; i += 3)	{
            if (mBoard[i] == HUMAN_PLAYER &&
                    mBoard[i+1] == HUMAN_PLAYER &&
                    mBoard[i+2]== HUMAN_PLAYER)
                return 2;
            if (mBoard[i] == COMPUTER_PLAYER &&
                    mBoard[i+1]== COMPUTER_PLAYER &&
                    mBoard[i+2] == COMPUTER_PLAYER)
                return 3;
        }

        // Check vertical wins
        for (int i = 0; i <= 2; i++) {
            if (mBoard[i] == HUMAN_PLAYER &&
                    mBoard[i+3] == HUMAN_PLAYER &&
                    mBoard[i+6]== HUMAN_PLAYER)
                return 2;
            if (mBoard[i] == COMPUTER_PLAYER &&
                    mBoard[i+3] == COMPUTER_PLAYER &&
                    mBoard[i+6]== COMPUTER_PLAYER)
                return 3;
        }

        // Check for diagonal wins
        if ((mBoard[0] == HUMAN_PLAYER &&
                mBoard[4] == HUMAN_PLAYER &&
                mBoard[8] == HUMAN_PLAYER) ||
                (mBoard[2] == HUMAN_PLAYER &&
                        mBoard[4] == HUMAN_PLAYER &&
                        mBoard[6] == HUMAN_PLAYER))
            return 2;
        if ((mBoard[0] == COMPUTER_PLAYER &&
                mBoard[4] == COMPUTER_PLAYER &&
                mBoard[8] == COMPUTER_PLAYER) ||
                (mBoard[2] == COMPUTER_PLAYER &&
                        mBoard[4] == COMPUTER_PLAYER &&
                        mBoard[6] == COMPUTER_PLAYER))
            return 3;

        // Check for tie
        for (int i = 0; i < BOARD_SIZE; i++) {
            // If we find a number, then no one has won yet
            if (mBoard[i] != HUMAN_PLAYER && mBoard[i] != COMPUTER_PLAYER)
                return 0;
        }

        // If we make it through the previous loop, all places are taken, so it's a tie
        return 1;
    }

    // Genera un movimiento aleatorio
    private int getRandomMove() {
        int move;
        do {
            move = mRand.nextInt(BOARD_SIZE);
        } while (mBoard[move] == HUMAN_PLAYER || mBoard[move] == COMPUTER_PLAYER);
        return move;
    }


    // Encuentra un movimiento ganador
    private int getWinningMove() {
        for (int i = 0; i < BOARD_SIZE; i++) {
            if (mBoard[i] != HUMAN_PLAYER && mBoard[i] != COMPUTER_PLAYER) {
                char curr = mBoard[i];
                mBoard[i] = COMPUTER_PLAYER;
                if (checkForWinner() == 3) { // Asume 3 es el código para victoria de la computadora
                    mBoard[i] = curr; // Restaura el estado original del tablero
                    return i;
                }
                mBoard[i] = curr;
            }
        }
        return -1;
    }

    // Encuentra un movimiento para bloquear al oponente
    private int getBlockingMove() {
        for (int i = 0; i < BOARD_SIZE; i++) {
            if (mBoard[i] != HUMAN_PLAYER && mBoard[i] != COMPUTER_PLAYER) {
                char curr = mBoard[i];
                mBoard[i] = HUMAN_PLAYER;
                if (checkForWinner() == 2) { // Asume 2 es el código para victoria del humano
                    mBoard[i] = curr; // Restaura el estado original del tablero
                    return i;
                }
                mBoard[i] = curr;
            }
        }
        return -1;
    }

    public int getComputerMove() {
        int move = -1;

        if (mDifficultyLevel == DifficultyLevel.Easy) {
            move = getRandomMove();
        } else if (mDifficultyLevel == DifficultyLevel.Harder) {
            move = getWinningMove();
            if (move == -1) {
                move = getRandomMove();
            }
        } else if (mDifficultyLevel == DifficultyLevel.Expert) {
            move = getWinningMove();
            if (move == -1) {
                move = getBlockingMove();
            }
            if (move == -1) {
                move = getRandomMove();
            }
        }

        System.out.println("Computer is moving to " + (move + 1));
        mBoard[move] = COMPUTER_PLAYER;
        return move;
    }

    public char getBoardOccupant(int index) {
        if (index >= 0 && index < BOARD_SIZE) {
            return mBoard[index]; // Devuelve el valor de la celda, que puede ser 'X', 'O' o el número original
        }
        return OPEN_SPOT; // Si el índice es inválido, devuelve un espacio vacío
    }

    /** Clear the board of all X's and O's by setting all spots to OPEN_SPOT. */
    public void clearBoard(){
        // Restablecer el tablero a su estado inicial
        for (int i = 0; i < BOARD_SIZE; i++) {
            mBoard[i] = (char) ('1' + i);  // '1' a '9'
        }
    }
    /** Set the given player at the given location on the game board.
     * The location must be available, or the board will not be changed.
     *
     * @param player - The HUMAN_PLAYER or COMPUTER_PLAYER
     * @param location - The location (0-8) to place the move
     */
    public boolean setMove(char player, int location) {
        // Verificar si la celda está vacía
        if (mBoard[location] != HUMAN_PLAYER && mBoard[location] != COMPUTER_PLAYER) {
            mBoard[location] = player;  // Coloca la marca del jugador en el tablero
            return true;  // El movimiento fue válido
        }
        return false;  // El movimiento no fue válido (ya está ocupada)
    }

    public DifficultyLevel getDifficultyLevel() {
        return mDifficultyLevel;
    }
    public void setDifficultyLevel(DifficultyLevel difficultyLevel) {
        mDifficultyLevel = difficultyLevel;
    }

    public int getBOARD_SIZE() {
        return BOARD_SIZE;
    }

    public char[] getBoardState() {
        return mBoard.clone(); // Devuelve una copia del arreglo actual del tablero
    }

    public void setBoardState(char[] boardState){
        System.arraycopy(boardState, 0, this.mBoard, 0, boardState.length);
    }

}

