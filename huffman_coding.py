import heapq
from typing import Optional, Self

from bitarray import bitarray

from utils import StringSample, SamplesStatistic


class HuffmanCoder:
    """
    Class for encoding and decoding texts via Huffman codes.
    Class instance store a root value for particular text we encode last time.
    """
    class Node:
        def __init__(
                self,
                _character: Optional[str],
                _frequency: int,
                _left: Optional[Self] = None,
                _right: Optional[Self] = None
        ) -> None:
            self.character = _character
            self.frequency = _frequency
            self.right = _right
            self.left = _left

        def __lt__(self, other: Self) -> bool:
            return self.frequency < other.frequency

        def is_leaf(self) -> bool:
            """
            Func for determine if a node is a leaf.
            :return: True if this node is leaf-node.
            """
            return self.right is None and self.left is None

    def __init__(self) -> None:
        self._root = None

    def _get_huffman_tree_root(self, text: str) -> Optional[Node]:
        """
        Build huffman tree for our text until gets root-node
        :param text: text value, which we should encode.
        :return: root-node.
        """
        if len(text) == 0:
            return

        freq = {i: text.count(i) for i in set(text)}
        pq = [self.Node(k, v) for k, v in freq.items()]
        heapq.heapify(pq)

        while len(pq) != 1:
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            total_frequency = left.frequency + right.frequency
            heapq.heappush(pq, self.Node(None, total_frequency, left, right))

        return pq[0]

    def _fill_huffman_codes(
            self,
            node: Optional[Node],
            code: str,
            huffman_codes: dict
    ) -> None:
        """
        Recursive function for filling huffman_codes dictionary with values
        we should encode
        :param node: current Node of our recursion
        :param code: prefix for our code
        :param huffman_codes: dictionary we should fill
        :return: None
        """
        if node is None:
            return

        if node.is_leaf():
            res_code = code if len(code) > 0 else '1'
            huffman_codes[node.character] = bitarray(res_code)

        self._fill_huffman_codes(node.left, code + '0', huffman_codes)
        self._fill_huffman_codes(node.right, code + '1', huffman_codes)

    def encode(self, text: str) -> bitarray:
        """
        Function for encoding text with huffman codes
        :param text: text, which we should encode
        :return: bitarray with all text encoded via our huffman_codes
        """
        encoded_b_arr = bitarray()

        huffman_codes = {}

        self._root = self._get_huffman_tree_root(text)
        self._fill_huffman_codes(self._root, '', huffman_codes)

        for character in text:
            encoded_b_arr += huffman_codes.get(character)

        return encoded_b_arr

    def _decoding_parser(
            self,
            node: Optional[Node],
            index: int,
            encoded_b_arr: bitarray,
            decoded_str: str
    ) -> (int, str):
        """
        Recursive function for reading bits and comparing codes until we
        match with the code of some letter
        :param node: current Node
        :param index: current index in bitarray
        :param encoded_b_arr: bitarray with our encoded text
        :param decoded_str: decoded part of original text at current index
        :return: original decoded text
        """
        if node is None:
            return index, decoded_str

        if node.is_leaf():
            decoded_str += node.character
            return index, decoded_str

        index = index + 1
        node = node.left if encoded_b_arr[index] == 0 else node.right
        return self._decoding_parser(node, index, encoded_b_arr, decoded_str)

    def decode(self, encoded_b_arr: bitarray) -> str:
        """
        Function for decoding bitarray to our original text
        :param encoded_b_arr: bitarray with previously encoded text
        :return: original text
        """
        decoded_str = ''
        if self._root.is_leaf():
            while self._root.freq > 0:
                decoded_str += self._root.character
                self._root.freq = self._root.freq - 1
        else:
            index = -1
            while index < len(encoded_b_arr) - 1:
                index, decoded_str = self._decoding_parser(
                    self._root, index, encoded_b_arr, decoded_str
                )
        return decoded_str


if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/Huffman_coding'

    huffman_coder = HuffmanCoder()

    origin_sample = StringSample.get_html_str_data_by_url(url)
    encoded_sample = huffman_coder.encode(origin_sample)
    decoded_sample = huffman_coder.decode(encoded_sample)

    stat = SamplesStatistic(origin_sample, encoded_sample, decoded_sample)
    stat.samples_statistic(memory=True, show_samples=False)

