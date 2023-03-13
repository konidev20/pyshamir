import unittest
from pyshamir import split, combine
from base64 import b64encode, b64decode

class TestSplit(unittest.TestCase):
  secret = b64decode('a+m4G0kEkKDQK4MFGz7L0vLz5oViQkDSLThiC4zDRZU=')
  def test_split(self):
    try:
      parts = split(self.secret, 5, 3)
      self.assertEqual(len(parts),5)
    except ValueError as ve:
      self.fail(ve.args[0])
    for part in parts:
      self.assertEqual(len(part), len(self.secret)+1)

    # test that the parts are different
    for i in range(len(parts) - 1):
      self.assertNotEqual(parts[i].hex(), parts[i + 1].hex())

  def test_split_invalid(self):
    with self.assertRaisesRegex(ValueError, 'Parts and threshold must be greater than 1'):
      split(self.secret, 0, 0)

    with self.assertRaisesRegex(ValueError, 'Parts must be greater than threshold'):
      split(self.secret, 2, 3)

    with self.assertRaisesRegex(ValueError, 'Parts must be less than 256'):
      split(self.secret, 1000, 3)

    with self.assertRaisesRegex(ValueError, 'Secret must be at least 1 byte long'):
      split(None, 5, 3)

    with self.assertRaisesRegex(ValueError, 'Secret must be at least 1 byte long'):
      split(bytearray(b''), 5, 3)

class TestCombine(unittest.TestCase):
  secret = b64decode('esfX3MUC++BrcwkiwsKtK6M5Pi5yvuc/A/6LweWJ5FA=')

  def test_combine(self):
    try:
      parts = split(self.secret, 5, 3)
    except ValueError as ve:
      self.fail(ve.args[0])

    # brute force test if all the possible combinations of keys
    # result in the same secret
    for i in range(5):
      for j in range(5):
        if j == i:
          continue
        for k in range(5):
          if k == i or k == j:
            continue
          int_parts = [parts[i], parts[j], parts[k]]
          try:
            recomb = combine(int_parts)
            self.assertEqual(b64encode(recomb), b64encode(self.secret))
          except ValueError as ve:
            self.fail(ve.args[0])

  def test_combine_invalid(self):
    with self.assertRaisesRegex(ValueError, 'Not enough parts to combine'):
      combine(bytearray())
    with self.assertRaisesRegex(ValueError, 'Not enough parts to combine'):
      combine(None)

    #check part length mismatch
    parts = [bytearray(b'ab'),bytearray(b'abc')]
    with self.assertRaisesRegex(ValueError, 'Parts are not the same length'):
      combine(parts)

    #check part length too small
    parts = [bytearray(b'a'),bytearray(b'b')]
    with self.assertRaisesRegex(ValueError, 'Part is too short'):
      combine(parts)

    #duplicate
    parts = [bytearray(b'ab'),bytearray(b'ab')]
    with self.assertRaisesRegex(ValueError, 'Duplicate sample'):
      combine(parts)

if __name__ == '__main__':
    unittest.main()
