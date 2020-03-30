import time

# Settings
DEPTH = 4
EVALUATE_FOR = ['white']

MOVE_PATTERNS = {
    'pawn': {
        'white': {
            'move': (1, 0),
            'double_move': (2, 0),
            'attack': [(1, 1), (1, -1)]
        },
        'black': {
            'move': (-1, 0),
            'double_move': (-2, 0),
            'attack': [(-1, 1), (-1, -1)]
        }
    },
    'straight': [(1, 0), (-1, 0), (0, 1), (0, -1)],
    'diagonal': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    'knight': [(2, 1), (1, 2), (-2, 1), (1, -2), (2, -1), (-1, 2), (-2, -1), (-1, -2)]
}

CASTLING = {
    'white': [
    {
        'rook': (0, 0),
        'free_fields': [(0, 1), (0, 2), (0, 3)],
        'king_path': [(0, 4), (0, 3)],
        'king_move': ((0, 4), (0, 2)),
        'rook_move': ((0, 0), (0, 3))
    },
    {
        'rook': (0, 7),
        'free_fields': [(0, 5), (0, 6)],
        'king_path': [(0, 4), (0, 5)],
        'king_move': ((0, 4), (0, 6)),
        'rook_move': ((0, 7), (0, 5))
    }
    ],
    'black': [
    {
        'rook': (7, 0),
        'free_fields': [(7, 1), (7, 2), (7, 3)],
        'king_path': [(7, 4), (7, 3)],
        'king_move': ((7, 4), (7, 2)),
        'rook_move': ((7, 0), (7, 3))
    },
    {
        'rook': (7, 7),
        'free_fields': [(7, 5), (7, 6)],
        'king_path': [(7, 4), (7, 5)],
        'king_move': ((7, 4), (7, 6)),
        'rook_move': ((7, 7), (7, 5))
    }
    ]
}

MATE_THRESHOLD = 10000
INFINITY = 100000
FILES = [i-1 for i in range(8)]

class Board:
    def __init__(self):
        self.pieces = []
        self.next_move_color = 'white'
        self.last_move = None
        self.reset_en_passant()
        
    def reset_en_passant(self):
        self.en_passant = {
            'white': [False] * 8,
            'black': [False] * 8
        }
    
    def show(self):
        for rank in range(7, -1, -1):
            file_string = ''
            for file in range(0, 8):
                piece = self.get_piece_by_position((rank, file))
                if piece is None:
                    file_string += '.'
                else:
                    file_string += piece.rep()
                
            print(file_string)
        
    def get_piece_by_position(self, position):
        for piece in self.pieces:
            if piece.position == position:
                return piece
        
        return None
        
    def remove_piece_by_position(self, position):
        piece = self.get_piece_by_position(position)
        if piece is None:
            print('Hughe Fail!!')
        self.pieces.remove(piece)
            
    def get_pieces_by_color(self, color):
        for piece in self.pieces:
            if piece.color == color:
                yield piece
        
    def get_moves_for_color(self, color, verify_no_check = True):
        for piece in self.get_pieces_by_color(color):
            for move in piece.generate_moves(verify_no_check):
                yield move

        
    def get_pseudo_legal_moves_for_color(self, color):
        for piece in self.get_pieces_by_color(color):
            for move in piece.generate_pseudo_legal_moves():
                yield move
        
    def is_attacked(self, position, color):
        op_color = opposite_color(color)
        for move in self.get_pseudo_legal_moves_for_color(op_color):
            piece = move.get_piece_by_position(position)
            if piece is not None and piece.color == op_color:
                return True

        return False
    
    def get_king_by_color(self, color):
        for piece in self.pieces:
            if isinstance(piece, King) and piece.color == color:
                return piece
        return None
    
    def is_checked(self, color):
        king = self.get_king_by_color(color)
        return self.is_attacked(king.position, color)
    
    def copy_and_execute_move(self, move):
        # Copy the board
        new_board = Board()
        for piece in self.pieces:
            piece.copy_to_board(new_board)
        new_board.last_move = move
        new_board.next_move_color = opposite_color(self.next_move_color)

        if not move.special_move:
            # Maybe remove an existing enemy piece
            if move.is_capture:
                new_board.remove_piece_by_position(move.target)
            
            # Find the piece that should be moved
            piece = new_board.get_piece_by_position(move.origin)
            piece.move_piece(move.target)
            
        elif move.special_move == 'pawn_double':
            piece = new_board.get_piece_by_position(move.origin)
            piece.move_piece(move.target)
            
            new_board.en_passant[opposite_color(piece.color)][move.origin[1]] = True

        elif move.special_move == 'castling':
            king = new_board.get_piece_by_position(move.move_info['king_move'][0])
            king.move_piece(move.move_info['king_move'][1])
            
            rook = new_board.get_piece_by_position(move.move_info['rook_move'][0])
            rook.move_piece(move.move_info['rook_move'][1])
            
        elif move.special_move == 'en_passant':
            pawn = new_board.get_piece_by_position(move.origin)
            pawn.move_piece(move.target)
            
            # remove the captured pawn
            new_board.remove_piece_by_position((move.origin[0], move.target[1]))
        
        elif move.special_move == 'promotion':
            pawn = new_board.get_piece_by_position(move.origin)
            color = pawn.color
            
            new_board.remove_piece_by_position(move.origin)
            Queen(new_board, move.target, color)

        return new_board
    
    def evaluate(self, depth = 0, α = -INFINITY, β = INFINITY):
        board_evaluation = sum(piece.evaluate() for piece in self.pieces)

        if depth == 0 or board_evaluation > MATE_THRESHOLD or board_evaluation < -MATE_THRESHOLD:
            return { 'value': board_evaluation, 'move': self.last_move }
        
        value = -INFINITY
        best_move = None
        for move in self.get_moves_for_color(self.next_move_color, False):
            evaluation = move.evaluate(depth - 1, α = -β, β = -α)
            if -evaluation['value'] > value:
                value = -evaluation['value']
                best_move = move
            α = max(α, value)
            if α >= β:
                break
        
        # Draw detection (No move, but mate threshold not exceeded)
        if best_move is None:
            return { 'value': 0, 'move': None }
            
        return { 'value': value, 'move': best_move.last_move }

class Piece:
    def __init__(self, board, position, color):
        self.board = board
        self.position = position
        self.color = color
        
        # Add the piece to the board
        self.board.pieces.append(self)
    
    def rep(self):
        if self.color == 'white':
            return self.char.upper()
        else:
            return self.char

    def move_piece(self, target_position):
        self.position = target_position
    
    def generate_moves(self, verify_no_check = True):
        for new_board in self.generate_pseudo_legal_moves():
            # If there is a check, the move can not be used
            if verify_no_check and new_board.is_checked(self.color):
                continue
            
            if new_board.last_move.special_move == 'castling':
                no_check_on_path = all(not new_board.is_attacked(position, self.color) for position in new_board.last_move.move_info['king_path'])
                if no_check_on_path:
                    yield new_board
            else:
                yield new_board
    
    def generate_pseudo_legal_moves(self):
        for pattern in self.move_patterns:
            target_position = add_pattern_to_position(self.position, pattern)
            
            while is_on_board(target_position):
                target_piece = self.board.get_piece_by_position(target_position)
                
                # No piece on the target square, we can move there
                if target_piece is None:
                    move = Move(self.position, target_position)
                    yield self.board.copy_and_execute_move(move)
                    
                # If we bump into a same color piece we can neither capture nor
                # move further.
                elif target_piece.color == self.color:
                    break
                else:
                    # We can capture but not move further
                    move = Move(self.position, target_position, is_capture = True)
                    yield self.board.copy_and_execute_move(move)
                    break
                
                # If we can't repeat the move (king, knight), break
                if not self.repeat_move:
                    break

                target_position = add_pattern_to_position(target_position, pattern)

    def evaluate(self):
        material_value = self.value
        positional_value = self.positional_value[self.position[0] if self.color == 'white' else 7 - self.position[0]][self.position[1]]
        
        total_value = material_value + positional_value
        return total_value if self.color == 'white' else -total_value
    
    def copy_to_board(self, board):
        return self.__class__(board, self.position, self.color)

class CastlePiece(Piece):
    def __init__(self, board, position, color, can_castle = True):
        self.can_castle = can_castle
        super().__init__(board, position, color)
    
    def move_piece(self, target_position):
        self.can_castle = False
        super().move_piece(target_position)
    
    def copy_to_board(self, board):
        return self.__class__(board, self.position, self.color, can_castle = self.can_castle)

class King(CastlePiece):
    move_patterns = MOVE_PATTERNS['straight'] + MOVE_PATTERNS['diagonal']
    repeat_move = False
    char = 'k'
    value = 60000
    positional_value = [
        [17,  30,  -3, -14,   6,  -1,  40,  18],
        [-4,   3, -14, -50, -57, -18,  13,   4],
        [-47, -42, -43, -79, -64, -32, -29, -32],
        [-55, -43, -52, -28, -51, -47,  -8, -50],
        [-55,  50,  11,  -4, -19,  13,   0, -49],
        [-62,  12, -57,  44, -67,  28,  37, -31],
        [-32,  10,  55,  56,  56,  55,  10,   3],
        [4,  54,  47, -99, -99,  60,  83, -62]
    ]

    def generate_pseudo_legal_moves(self):
        # First try out all non-castling king moves
        for regular_move in super().generate_pseudo_legal_moves():
            yield regular_move

        if self.can_castle:
            for castling in CASTLING[self.color]:
                # Find out if there is a rook to castle with
                maybe_rook = self.board.get_piece_by_position(castling['rook'])
                rook_can_castle = maybe_rook is not None and isinstance(maybe_rook, Rook) and maybe_rook.color == self.color and maybe_rook.can_castle
                
                # Chek if there is no piece in the way
                nothing_in_way = all(self.board.get_piece_by_position(position) is None for position in castling['free_fields'])
                
                if rook_can_castle and nothing_in_way:
                    move = Move(*castling['king_move'], special_move = 'castling', move_info = castling)
                    yield self.board.copy_and_execute_move(move)


class Queen(Piece):
    move_patterns = MOVE_PATTERNS['straight'] + MOVE_PATTERNS['diagonal']
    repeat_move = True
    char = 'q'
    value = 929
    positional_value = [
        [-39, -30, -31, -13, -31, -36, -34, -42],
        [-36, -18,   0, -19, -15, -15, -21, -38],
        [-30,  -6, -13, -11, -16, -11, -16, -27],
        [-14, -15,  -2,  -5,  -1, -10, -20, -22],
        [1, -16,  22,  17,  25,  20, -13,  -6],
        [-2,  43,  32,  60,  72,  63,  43,   2],
        [14,  32,  60, -10,  20,  76,  57,  24],
        [6,   1,  -8,-104,  69,  24,  88,  26]
    ]

class Rook(CastlePiece):
    move_patterns = MOVE_PATTERNS['straight']
    repeat_move = True
    char = 'r'
    value = 479
    positional_value = [
        [-30, -24, -18,   5,  -2, -18, -31, -32],
        [-53, -38, -31, -26, -29, -43, -44, -53],
        [-42, -28, -42, -25, -25, -35, -26, -46],
        [-28, -35, -16, -21, -13, -29, -46, -30],
        [0,   5,  16,  13,  18,  -4,  -9,  -6],
        [19,  35,  28,  33,  45,  27,  25,  15],
        [55,  29,  56,  67,  55,  62,  34,  60],
        [35,  29,  33,   4,  37,  33,  56,  50]
    ]
    
class Bishop(Piece):
    move_patterns = MOVE_PATTERNS['diagonal']
    repeat_move = True
    char = 'b'
    value = 320
    positional_value = [
        [-7,   2, -15, -12, -14, -15, -10, -10],
        [19,  20,  11,   6,   7,   6,  20,  16],
        [14,  25,  24,  15,   8,  25,  20,  15],
        [13,  10,  17,  23,  17,  16,   0,   7],
        [25,  17,  20,  34,  26,  25,  15,  10],
        [-9,  39, -32,  41,  52, -10,  28, -14],
        [-11,  20,  35, -42, -39,  31,   2, -22],
        [-59, -78, -82, -76, -23,-107, -37, -50]
    ]
    
class Knight(Piece):
    move_patterns = MOVE_PATTERNS['knight']
    repeat_move = False
    char = 'n'
    value = 280
    positional_value = [
        [-74, -23, -26, -24, -19, -35, -22, -69],
        [-23, -15,   2,   0,   2,   0, -23, -20],
        [-18,  10,  13,  22,  18,  15,  11, -14],
        [-1,   5,  31,  21,  22,  35,   2,   0],
        [24,  24,  45,  37,  33,  41,  25,  17],
        [10,  67,   1,  74,  73,  27,  62,  -2],
        [-3,  -6, 100, -36,   4,  62,  -4, -14],
        [-66, -53, -75, -75, -10, -55, -58, -70]
    ]

class Pawn(Piece):
    char = 'p'
    value = 100
    positional_value = [
        [0,   0,   0,   0,   0,   0,   0,   0],
        [-31,   8,  -7, -37, -36, -14,   3, -31],
        [-22,   9,   5, -11, -10,  -2,   3, -19],
        [-26,   3,  10,   9,   6,   1,   0, -23],
        [-17,  16,  -2,  15,  14,   0,  15, -13],
        [7,  29,  21,  44,  40,  31,  44,   7],
        [78,  83,  86,  73, 102,  82,  85,  90],
        [0,   0,   0,   0,   0,   0,   0,   0]
    ]

    def generate_pseudo_legal_moves(self):
        patterns = MOVE_PATTERNS['pawn'][self.color]
        promotion = self.color == 'white' and self.position[0] == FILES[7] or self.color == 'black' and self.position[0] == FILES[2]
        
        # Pawn move one square ahead
        target_position = add_pattern_to_position(self.position, patterns['move'])
        target_piece = self.board.get_piece_by_position(target_position)
        if target_piece is None:
            move = Move(self.position, target_position, special_move = ('promotion' if promotion else False))
            yield self.board.copy_and_execute_move(move)
        
            # Pawn double move
            if self.color == 'white' and self.position[0] == FILES[2] or self.color == 'black' and self.position[0] == FILES[7]:
                target_position = add_pattern_to_position(self.position, patterns['double_move'])
                target_piece = self.board.get_piece_by_position(target_position)
                if target_piece is None:
                    move = Move(self.position, target_position, special_move='pawn_double')
                    yield self.board.copy_and_execute_move(move)
        
        # Pawn attack
        for attack_pattern in patterns['attack']:
            target_position = add_pattern_to_position(self.position, attack_pattern)
            target_piece = self.board.get_piece_by_position(target_position)
            
            # No need to check if target position is on board, because if not there is no piece there
            if target_piece is not None and target_piece.color == opposite_color(self.color):
                move = Move(self.position, target_position, special_move = ('promotion' if promotion else False), is_capture = True)
                yield self.board.copy_and_execute_move(move)
            
            # Check if we can capture en passant
            if is_on_board(target_position) and self.board.en_passant[self.color][target_position[1]]:
                if self.position[0] == FILES[5] and self.color == 'white' or self.position[0] == FILES[4] and self.color == 'black':
                    move = Move(self.position, target_position, special_move = 'en_passant', is_capture = True)
                    yield self.board.copy_and_execute_move(move)
        
class Move:
    def __init__(self, origin, target, special_move = False, move_info = None, is_capture = False):
        self.origin = origin
        self.target = target
        self.special_move = special_move
        self.move_info = move_info
        self.is_capture = is_capture

def opposite_color(color):
    return 'white' if color == 'black' else 'black'

def add_pattern_to_position(position, pattern):
    return tuple(position[i] + pattern[i] for i in [0, 1])

def is_on_board(position):
    return 0 <= position[0] <= 7 and 0 <= position[1] <= 7

def notation_to_move(notation):
    rank = int(notation[1]) - 1
    file = 'abcdefgh'.index(notation[0])
    
    return (rank, file)

def move_to_notation(move):
    return 'abcdefgh'[move[1]] + str(move[0] + 1)

def main():
    board = Board()
    
    Pawn(board, (1,0), 'white')
    Pawn(board, (1,1), 'white')
    Pawn(board, (1,2), 'white')
    Pawn(board, (1,3), 'white')
    Pawn(board, (1,4), 'white')
    Pawn(board, (1,5), 'white')
    Pawn(board, (1,6), 'white')
    Pawn(board, (1,7), 'white')
    Rook(board, (0,0), 'white')
    Knight(board, (0,1), 'white')
    Bishop(board, (0,2), 'white')
    Queen(board, (0,3), 'white')
    King(board, (0,4), 'white')
    Bishop(board, (0,5), 'white')
    Knight(board, (0,6), 'white')
    Rook(board, (0,7), 'white')
    
    Pawn(board, (6,0), 'black')
    Pawn(board, (6,1), 'black')
    Pawn(board, (6,2), 'black')
    Pawn(board, (6,3), 'black')
    Pawn(board, (6,4), 'black')
    Pawn(board, (6,5), 'black')
    Pawn(board, (6,6), 'black')
    Pawn(board, (6,7), 'black')
    Rook(board, (7,0), 'black')
    Knight(board, (7,1), 'black')
    Bishop(board, (7,2), 'black')
    Queen(board, (7,3), 'black')
    King(board, (7,4), 'black')
    Bishop(board, (7,5), 'black')
    Knight(board, (7,6), 'black')
    Rook(board, (7,7), 'black')
    
    board.show()
    while True:
        # Get legal moves
        legal_moves = [move for move in board.get_moves_for_color(board.next_move_color)]
        
        if len(legal_moves) == 0:
            if board.is_checked(board.next_move_color):
                print(opposite_color(board.next_move_color), ' wins!')
            else:
                print('draw!')
            break
        
        if board.next_move_color in EVALUATE_FOR:
            start = time.time()
            
            evaluation = board.evaluate(DEPTH)
            best_move = evaluation['move']
            best_score = evaluation['value']

            end = time.time()
            duration = round(end - start, 2)
            print('Best move: ', move_to_notation(best_move.origin), ' to ', move_to_notation(best_move.target), ', Evaluation: ', best_score, ', In: ', str(duration), 's, Depth: ', DEPTH)

        
        is_legal = False
        while not is_legal:
            move = input('Enter move: ')
            origin = notation_to_move(move[:2])
            target = notation_to_move(move[2:])
            
            for move in legal_moves:
                if move.last_move.origin == origin and move.last_move.target == target:
                    is_legal = True
                    board = move

        board.show()

if __name__ == '__main__':
    main()
        