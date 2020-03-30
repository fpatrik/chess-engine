from chessy3 import Board, Move, King, Queen, Rook, Bishop, Knight, Pawn

def test_king_on_board():
    board = Board()
    king = King(board, (0, 0), 'white')
    King(board, (7, 7), 'black')
    
    assert king.color == 'white'
    assert isinstance(board.get_piece_by_position((0, 0)), King)
    
def test_king_moves_corner():
    board = Board()
    king = King(board, (0, 0), 'white')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 3
    assert len(moves) == 3

def test_king_moves_center():
    board = Board()
    king = King(board, (1, 1), 'white')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 8
    assert len(moves) == 8
    
def test_king_moves_with_check():
    board = Board()
    king = King(board, (0, 1), 'white')
    King(board, (0, 3), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 5
    assert len(moves) == 3


def test_king_in_check():
    board = Board()
    King(board, (0, 0), 'white')
    Queen(board, (0, 7), 'black')
    King(board, (7, 7), 'black')
    
    assert board.is_checked('white') == True
    
def test_king_and_queen_moves_with_check():
    board = Board()
    king = King(board, (0, 0), 'white')
    queen_black = Queen(board, (0, 7), 'black')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves_king = [move for move in king.generate_pseudo_legal_moves()]
    moves_king = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves_king) == 3
    assert len(moves_king) == 2
    
    pseudo_legal_moves_queen = [move for move in queen_black.generate_pseudo_legal_moves()]
    moves_queen = [move for move in queen_black.generate_moves()]
    
    assert len(pseudo_legal_moves_queen) == 20
    assert len(moves_queen) == 20
    
def test_discovered_check_with_knight():
    board = Board()
    king = King(board, (0, 0), 'white')
    knight = Knight(board, (0, 1), 'white')
    queen_black = Queen(board, (0, 7), 'black')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves_king = [move for move in king.generate_pseudo_legal_moves()]
    moves_king = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves_king) == 2
    assert len(moves_king) == 2
    
    pseudo_legal_moves_queen = [move for move in queen_black.generate_pseudo_legal_moves()]
    moves_queen = [move for move in queen_black.generate_moves()]
    
    assert len(pseudo_legal_moves_queen) == 19
    assert len(moves_queen) == 19
    
    pseudo_legal_moves_knight = [move for move in knight.generate_pseudo_legal_moves()]
    moves_knight = [move for move in knight.generate_moves()]
    
    assert len(pseudo_legal_moves_knight) == 3
    assert len(moves_knight) == 0
    
def test_castling_white_long():
    board = Board()
    king = King(board, (0, 4), 'white')
    Rook(board, (0, 0), 'white')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 6

def test_castling_white_long_with_piece_between():
    board = Board()
    king = King(board, (0, 4), 'white')
    Rook(board, (0, 0), 'white')
    Knight(board, (0, 1), 'white')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 5
    assert len(moves) == 5

def test_castling_white_long_with_check():
    board = Board()
    king = King(board, (0, 4), 'white')
    Rook(board, (0, 0), 'white')
    Queen(board, (6, 4), 'black')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 4
    
def test_castling_white_check_on_path():
    board = Board()
    king = King(board, (0, 4), 'white')
    Rook(board, (0, 0), 'white')
    Bishop(board, (4, 2), 'black')
    King(board, (7, 7), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 5
    
def test_castling_white_short():
    board = Board()
    king = King(board, (0, 4), 'white')
    Rook(board, (0, 7), 'white')
    King(board, (7, 0), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 6
    
def test_castling_black_short():
    board = Board()
    King(board, (0, 4), 'white')
    Rook(board, (7, 0), 'black')
    king = King(board, (7, 4), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 6
    
def test_castling_black_long():
    board = Board()
    King(board, (0, 4), 'white')
    Rook(board, (7, 7), 'black')
    king = King(board, (7, 4), 'black')
    
    pseudo_legal_moves = [move for move in king.generate_pseudo_legal_moves()]
    moves = [move for move in king.generate_moves()]
    
    assert len(pseudo_legal_moves) == 6
    assert len(moves) == 6

def test_pawn_moves():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (1, 0), 'white')
    King(board, (7, 7), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 2

def test_blocked_pawn_1():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (1, 0), 'white')
    King(board, (3, 0), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 1
    
def test_blocked_pawn_2():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (1, 0), 'white')
    King(board, (2, 0), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 0
    
def test_pawn_attack_1():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (1, 0), 'white')
    Bishop(board, (2, 1), 'black')
    King(board, (7, 7), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 3

def test_pawn_attack_2():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (5, 5), 'black')
    Bishop(board, (4, 4), 'white')
    King(board, (7, 6), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 2
    
def test_pawn_promotion():
    board = Board()
    King(board, (0, 0), 'white')
    pawn = Pawn(board, (6, 0), 'white')
    King(board, (7, 7), 'black')

    moves = [move for move in pawn.generate_moves()]
    
    assert len(moves) == 1
    assert isinstance(moves[0].get_piece_by_position((7,0)), Queen)

def test_en_passant():
    board = Board()
    King(board, (0, 0), 'white')
    Pawn(board, (1, 0), 'white')
    Pawn(board, (3, 1), 'black')
    King(board, (7, 7), 'black')
    
    move = Move((1,0), (3,0), special_move = 'pawn_double')
    new_board = board.copy_and_execute_move(move)

    assert new_board.en_passant['black'][0]
    
    black_pawn = new_board.get_piece_by_position((3,1))
    moves = [move for move in black_pawn.generate_moves()]
    
    assert len(moves) == 2
    
    move = Move((3,1), (2,0), special_move = 'en_passant')
    newest_board = new_board.copy_and_execute_move(move)
    
    assert len([piece for piece in newest_board.pieces]) == 3
    
def test_mate_detection():
    board = Board()
    King(board, (0, 0), 'white')
    King(board, (2, 1), 'black')
    Rook(board, (0, 7), 'black')
    
    assert board.evaluate(depth=2)['value'] < 10000

    
    
    
    