import unittest
import numpy as np

from src.game.ttt import TTT

class TestWinner(unittest.TestCase):

    def test_row(self):
        t3 = TTT(3)
        s3 = np.array([0,0,0,-1,-1,0, 1,1,1])
        self.assertEqual(t3.check_winner(s3),{'winner':1, 'lines':[[6,7,8]]})
        self.assertTrue(t3.is_terminated(s3))
    
    def test_column(self):
        t4 = TTT(4)
        s4 = np.array([1,0,0,-1, 0,1,0,-1, 1,0,0,-1, 0,1,0,-1])
        self.assertEqual(t4.check_winner(s4),{'winner':-1,'lines':[[3,7,11,15]]})
        self.assertTrue(t4.is_terminated(s4))


    def test_diagonal1(self):
        t3 = TTT(3)
        s3 = np.array([1,0,-1, 0,1,-1, 0,0,1])
        self.assertTrue(t3.is_terminated(s3))
        self.assertEqual(t3.check_winner(s3),{'winner':1,'lines':[[0,4,8]]})

        t4 = TTT(4)
        s4 = np.array([-1,0,0,1, 0,-1,0,1, 0,1,-1,0, 1,0,0,-1])
        self.assertTrue(t4.is_terminated(s4))
        self.assertEqual(t4.check_winner(s4),{'winner':-1,'lines':[[0,5,10,15]]})

    def test_diagonal2(self):
        t3 = TTT(3)
        s3 = np.array([1,0,-1, 1,-1,0, -1,1,0])
        self.assertEqual(t3.check_winner(s3),{'winner':-1,'lines':[[2,4,6]]})
        self.assertTrue(t3.is_terminated(s3))

        t4 = TTT(4)
        s4 = np.array([-1,0,0,1, -1,0,1,0, -1,1,0,0, 1,0,0,0])
        self.assertTrue(t4.is_terminated(s4))
        self.assertEqual(t4.check_winner(s4),{'winner':1,'lines':[[3,6,9,12]]})

class TestUtils(unittest.TestCase):

    def test_availables(self):
        t3 = TTT(3)
        s3 = [[1,-1,0]
             ,[0,1,-1]
             ,[1,-1,0]]
        s3 = np.array(s3).reshape(-1)
        indices = t3.get_available_positions(s3)
        self.assertListEqual(indices,[2,3,8])

    def test_score1(self):
        t3 = TTT(3)
        s = [
            [1,-1,0],
            [-1,1,0],
            [0,0,1]
        ]
        s = np.array(s).reshape(-1)
        terminated = t3.is_terminated(s)
        score = t3.get_score(s)
        self.assertTrue(terminated)
        self.assertEqual(score,5)

    def test_result1(self):
        t3 = TTT(3)
        s = [
            [ 1,-1,-1],
            [-1, 1, 1],
            [ 1,-1, 1]
        ]
        s = np.array(s).reshape(-1)
        result = t3.get_result(s)
        to_equal = {'terminated':True, 'score':1, 'winner':1, 'lines':[[0,4,8]]}
        self.assertDictEqual(result, to_equal)

    def test_state_encode(self):
        t3 = TTT(3)
        encoded01 = t3.get_encoded_state()
        state02 = np.array([0,0,0,0,0,0,0,0,0],dtype=int)
        encoded02 = t3.get_encoded_state(state02)
        self.assertEqual(encoded01,encoded02)

    def test_get_mover(self):
        t = TTT(3)
        s = [
            [0,1,0],
            [0,-1,0],
            [0,0,0]
        ]
        s = np.array(s)
        s = s.reshape(-1)
        
        mover = t.get_mover(state=s)
        self.assertTrue(mover == 1)

    def test_set_state(self):
        t = TTT(3)
        state = [1,0,0,1,1,0,-1,-1,0]
        t.set_state(state)
        mover = t.get_mover()
        order = t._order
        num_of_moves = t._num_moves
        _state = np.array(state,dtype=int)
        self.assertEqual(mover,-1)
        self.assertEqual(order,False)
        self.assertEqual(num_of_moves,5)
        self.assertTrue(np.array_equal(_state,t._state))


class TestFullGame(unittest.TestCase):

    def test_game1(self):
        #  0 1 0
        # -1 1 0
        # -1 1 0
        t = TTT(3)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':False,'score':0})

        t.put(1)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':False,'score':0})

        t.put(3)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':False,'score':0})

        t.put(4)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':False,'score':0})
        
        t.put(6)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':False,'score':0})

        t.put(7)
        result = t.get_result()
        self.assertDictEqual(result,{'terminated':True,'score':5})
        
        return

if __name__ == '__main__':
    unittest.main()